import base64
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .models import AIReport

# ─── Thiết lập biến Môi trường Sinh văn bản (Trực quan và Không ngẫu nhiên) ──────────────────────
def get_gen_config():
    if not GEMINI_AVAILABLE:
        return None
    return genai.types.GenerationConfig(
        temperature=0,
        top_p=0.05,
        top_k=1,
    )

# ─── Kịch bản Prompt dành riêng để rèn luyện AI chẩn đoán Âm thanh cơ học ─────────────────────────────────────────────────────
SOUND_PROMPT = """
Bạn là thợ máy, chuyên gia cơ khí xe máy và ô tô dạn dày kinh nghiệm tại Việt Nam. 
Nhiệm vụ của bạn là LẮNG NGHE ĐOẠN VIDEO/AUDIO VÀ CHẨN ĐOÁN BỆNH XE SỬ DỤNG ĐÚNG THUẬT NGỮ THỢ VIỆT NAM (như lột dên, lupe, kêu cò, xước nòng, rớt đầu, v.v.).

=== CẨM NANG ÂM THANH ĐẶC TRƯNG VIỆT NAM ===
1. Tiếng "rít rít", "két két" (squealing/screeching):
   - Khi phanh: Hết má phanh, kẹt heo dầu, đĩa phanh/tăm bua mòn.
   - Khi nổ máy/lên ga: Trùng/trượt dây curoa (đối với xe tay ga/ô tô).
2. Tiếng "tạch tạch", "è è" RẤT YẾU VÀ KHÔNG THỂ NỔ MÁY (clicking/whirring khi khởi động):
   - Nguyên nhân: Hết bình ắc quy, hư củ đề, tuôn răng đề, hư rơ-le đề.
   - CHÚ Ý: Tiếng "tạch tạch" đề KHÔNG BAO GIỜ xảy ra khi máy đang nổ. Nếu video xe đang nổ/đang chạy mà có tiếng lốc cóc kim loại, ĐÓ KHÔNG PHẢI LÀ HƯ ĐỀ/ẮC QUY. Đề hỏng thì CHỈ KÊU LÚC BẤM ĐỀ THÔI.
3. Tiếng "cộc cộc", "lóc cóc" KIM LOẠI Va Đập LỚN VÀ CHẮC TỪ LỐC MÁY (Engine knocking/Piston slap):
   - Ngôn ngữ thợ: Lột dên, xước nòng (piston), lỏng ắc piston, gãy tay biên, rớt đầu lupe.
   - LUẬT BẮT BUỘC: Nếu nghe tiếng "CỘC CỘC" liên tục nhịp nhàng theo tiếng máy, KỂ CẢ CÓ NHẠC HAY TIẾNG ỒN TRÊN TIKTOK lấn át, bạn HÃY KẾT LUẬN LÀ "LỘT DÊN / XƯỚC NÒNG PISTON".
   - Tuỵệt đối cấm đánh tráo tiếng này với lỗi bình ắc quy/củ đề. Lỗi piston kêu lớn khi thốc ga rã máy. ĐÂY LÀ LỖI RẤT NẶNG (CẤM LÁI CHẠY TIẾP).
4. Tiếng "lạch cạch", "tạch tạch" nhỏ và xè xè ở nắp cu-lát (Tapping/Valves):
   - Ngôn ngữ thợ: Kêu cò (xú-bắp lỏng), sên cam chùng (sên đập lốc xè xè).
   - Truyền động: Sên (xích) chùng đập cacte, nhông sên dĩa mòn.
5. Tiếng "xào xào", "rào rào", "rột rột" (grinding):
   - Bánh xe: Bể bạc đạn (nứt vòng bi).
   - Động cơ: Thiếu nhớt bôi trơn nghiêm trọng, bể đạn dên, nồi kêu.
6. Âm thanh pô nổ lụp bụp (popping/backfire):
   - Dư xăng, hỏng bugi, hở xú-bắp, lủng pô.
7. Tiếng "hú" lớn khi thốc ga (howling/whining):
   - Bể nhông láp (xe ga), mòn bánh răng nhông số.

=== BẢNG NEO GIÁ THAM KHẢO (VNĐ – xe máy phổ thông) ===
| Loại sửa chữa              | Linh kiện          | Công thợ       | Tổng hợp lý   |
|----------------------------|--------------------|----------------|---------------|
| Thay lốp / vỏ xe máy       | 80.000–150.000     | 20.000–30.000  | 100.000–180.000|
| Sửa thắng / Bố thắng       | 30.000–80.000      | 30.000–60.000  | 60.000–140.000|
| Thay bình ắc quy           | 150.000–350.000    | 20.000–30.000  | 170.000–380.000|
| Sửa củ đề / Thay than đề   | 50.000–150.000     | 50.000–80.000  | 100.000–230.000|
| Khắc phục kêu cò, sên cam  | 50.000–150.000     | 50.000–100.000 | 100.000–250.000|
| Nhông sên dĩa              | 150.000–350.000    | 50.000–100.000 | 200.000–450.000|
| Bể bạc đạn bánh xe         | 40.000–80.000      | 30.000–50.000  | 70.000–130.000|
| RÃ MÁY: Lột dên/Hư piston  | 500.000–1.200.000  | 300.000–600.000| 800.000–1.800.000|
| Thay nồi/Côn               | 300.000–800.000    | 150.000–300.000| 450.000–1.100.000|
(Với ô tô: nhân hệ số 3–6x so với xe máy tuỳ hạng xe)

QUY TẮC NHẬN DIỆN BẮT BUỘC:
1. Giao tiếp như thợ sửa xe bản địa. Dùng thuật ngữ "Lột dên", "Lupe", "Kêu cò", "Sên cam chùng", "Bể vòng bi/bạc đạn".
2. XUYÊN QUY NHIỄU ÂM THANH: Phát video trên mạng xã hội như TikTok có nhạc hay giọng lồng tiếng, hãy tập trung vào âm nền cơ khí cộc cộc, lạch cạch đằng sau.
3. Mức khẩn cấp (urgency_level): 1-Nhẹ, 2-Bình thường, 3-Sửa sớm, 4-Tuyệt đối cẩn trọng (mòn bố thắng), 5-Cấm lái (Lột dên, nghẹt lốc máy, hư piston).

TRẢ VỀ DUY NHẤT ĐỊNH DẠNG JSON SAU, KHÔNG THÊM BẤT KỲ VĂN BẢN/MARKDOWN NÀO KHÁC BÊN NGOÀI:
{
  "reasoning": "SUY NGHĨ TỪNG BƯỚC CỦA BẠN TRƯỚC: 1. Đoạn âm thanh có những tiếng gì? 2. Tiếng đó xảy ra khi đứng yên, bấm đề hay lúc máy đang chạy? 3. Âm sắc là gì (nhựa, kim loại, rít)? 4. Dẫn đến kết luận bênh gì? (BẮT BUỘC RẤT CHI TIẾT)",
  "diagnosis": "Tên định bệnh dùng thuật ngữ thợ (VD: Lột dên / Hư piston)",
  "sound_type": "Mô tả loại tiếng (VD: Tiếng cộc cộc đanh thép liên tục)",
  "sound_location": "Vị trí dự đoán (VD: Lốc máy giữa)",
  "severity": "Nhẹ | Trung bình | Nghiêm trọng | Nguy hiểm",
  "details": "Giải thích chi tiết hơn: Bạn nghe thấy tiếng gì qua lớp nhạc/ồn, tại sao lại ra bệnh này, hậu quả ra sao.",
  "root_cause": "Nguyên nhân gốc bằng thuật ngữ Việt (VD: Thiếu nhớt gây xước nòng, lột dên)",
  "parts_needed": ["Bộ piston bạc", "Bộ tay biên (dên)", "Dầu máy"],
  "parts_cost": "600.000 – 1.000.000 VNĐ",
  "parts_recommended": "800.000 VNĐ",
  "labor_cost": "300.000 – 600.000 VNĐ",
  "labor_recommended": "450.000 VNĐ",
  "estimated_price": "900.000 – 1.600.000 VNĐ",
  "total_recommended": "1.250.000 VNĐ",
  "price_note": "Báo giá tham khảo rã máy/làm máy móc, thay đổi tùy theo độ hỏng của lốc máy.",
  "recommended_action": "Dừng xe ngay lập tức, gọi cứu hộ chở xe ra tiệm thợ uy tín để rã máy kiểm tra.",
  "can_drive": false,
  "urgency_level": 5,
  "warning_signs": "Chạy tiếp sẽ phá vỡ toàn bộ lốc máy và đứt xích cam, thiệt hại cực lớn."
}

NẾU KHÔNG CÓ TIẾNG ĐỘNG CƠ CƠ KHÍ NÀO CHỈ TOÀN TIẾNG NGƯỜI/NHẠC HOẶC RẤT KHÓ NGHE:
{"reasoning":"Tôi chỉ nghe thấy tiếng nhạc/người nói hoặc âm thanh quá méo, không có bất kỳ tiếng gõ cơ khí hoặc ma sát nào đặc trưng của động cơ xe.","diagnosis":"Âm thanh không rõ/Không có tiếng máy","sound_type":"Không xác định","sound_location":"Không xác định","severity":"Nhẹ","details":"Chỉ nghe thấy nhạc/clip vui nhộn, không có âm thanh cốt lõi của hỏng hóc cơ khí.","root_cause":"Không xác định","parts_needed":[],"parts_cost":"Chưa xác định","parts_recommended":null,"labor_cost":"Chưa xác định","labor_recommended":null,"estimated_price":"Chưa xác định","total_recommended":null,"price_note":"Cần âm thanh máy móc rõ hơn","recommended_action":"Tránh lấy video chỉ có nhạc để chẩn đoán, xin lồng ghép tiếng máy xe thật.","can_drive":true,"urgency_level":1,"warning_signs":null}
"""


def save_sound_report(request, result):
    """Hàm tĩnh hỗ trợ Record lại Phân tích Âm thanh của AI xuống DB."""
    try:
        AIReport.objects.create(
            customer=request.user if request.user.is_authenticated else None,
            diagnosis=result.get('diagnosis', ''),
            severity=result.get('severity', 'Trung bình'),
            details=result.get('details', ''),
            parts_cost=result.get('parts_cost', ''),
            labor_cost=result.get('labor_cost', ''),
            estimated_price=result.get('estimated_price', ''),
            price_note=result.get('price_note', ''),
            recommended_action=result.get('recommended_action', ''),
            can_drive=result.get('can_drive', True),
            urgency_level=result.get('urgency_level', 1),
            ai_powered=result.get('ai_powered', True),
            source=AIReport.SOURCE_SOUND,
        )
    except Exception:
        pass


class AnalyzeSoundView(APIView):
    """API Chẩn đoán File âm thanh thông qua Base64 cho xe bằng sức mạnh Gemini 2.5 Flash Native Audio."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({"error": "Vui lòng gửi file âm thanh."}, status=400)

        # Rào chắn bảo mật 1: Từ chối dung lượng vượt trên 10MB
        if audio_file.size > 10 * 1024 * 1024:
            return Response({"error": "File âm thanh quá lớn (tối đa 10MB)."}, status=400)

        audio_data = audio_file.read()
        content_type = audio_file.content_type or 'audio/webm'

        # Ánh xạ/Bình thường hóa mã định dạng MIME cho file Audio theo tiêu chuẩn input của Gemini API
        mime_map = {
            'audio/webm': 'audio/webm',
            'audio/ogg':  'audio/ogg',
            'audio/wav':  'audio/wav',
            'audio/wave': 'audio/wav',
            'audio/mp4':  'audio/mp4',
            'audio/mpeg': 'audio/mpeg',
            'audio/mp3':  'audio/mpeg',
            'audio/aac':  'audio/aac',
        }
        mime_type = mime_map.get(content_type.split(';')[0].strip(), 'audio/webm')

        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            return Response({
                "diagnosis": "API chưa cấu hình",
                "severity": "Trung bình",
                "details": "Chưa cấu hình GEMINI_API_KEY.",
                "ai_powered": False,
            }, status=200)

        try:
            genai.configure(api_key=api_key)
            cfg = get_gen_config()

            audio_part = {
                "mime_type": mime_type,
                "data": base64.b64encode(audio_data).decode('utf-8'),
            }

            response = None
            last_error = None

            # ── Giải thuật Fallback Model (Thử 2.5 Flash hỗ trợ Audio gốc -> 2.0 -> 1.5) ──
            for model_name in [
                'gemini-2.5-flash',
                'gemini-2.0-flash',
                'gemini-1.5-flash-latest',
            ]:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(
                        [SOUND_PROMPT, {"inline_data": audio_part}],
                        generation_config=cfg,
                    )
                    break
                except Exception as e:
                    last_error = e
                    continue

            if response is None:
                raise last_error

            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()

            result = json.loads(raw_text)
            result['ai_powered'] = True
            result['source'] = 'sound'
            if not isinstance(result.get('parts_needed'), list):
                result['parts_needed'] = []

            save_sound_report(request, result)
            return Response(result)

        except json.JSONDecodeError:
            raw = response.text[:200] if 'response' in locals() else 'Không có phản hồi'
            return Response({
                "diagnosis": "Kết quả không đọc được",
                "severity": "Trung bình",
                "details": f"AI phân tích xong nhưng định dạng lỗi: {raw}",
                "ai_powered": True,
                "source": "sound",
            }, status=200)

        except Exception as e:
            return Response({
                "diagnosis": "Không thể kết nối AI",
                "severity": "Trung bình",
                "details": f"Lỗi: {str(e)[:120]}",
                "ai_powered": False,
                "source": "sound",
            }, status=200)

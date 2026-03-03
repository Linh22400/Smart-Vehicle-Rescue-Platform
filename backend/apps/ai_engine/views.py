import os
import json
import base64
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import permissions
from django.conf import settings

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# ─── Deterministic generation config ───────────────────────────────────────
# temperature=0 → greedy decoding → same input always gives same output
# This is the single most important fix for price consistency.
GEN_CONFIG = None  # lazily initialised after genai is imported

def get_gen_config():
    global GEN_CONFIG
    if GEN_CONFIG is None and GEMINI_AVAILABLE:
        GEN_CONFIG = genai.types.GenerationConfig(
            temperature=0,       # no randomness
            top_p=0.05,          # very tight nucleus
            top_k=1,             # only pick the most likely token
        )
    return GEN_CONFIG


def build_prompt() -> str:
    """Build prompt with injected current date + price anchor table."""
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    month_year = now.strftime("tháng %m năm %Y")

    return f"""
Bạn là chuyên gia cơ khí xe cơ giới tại Việt Nam với hơn 15 năm kinh nghiệm.
Nhiệm vụ: Phân tích ảnh hư hỏng xe, định giá CHÍNH XÁC dựa trên bảng neo giá bên dưới.

⚠️ NGÀY HIỆN TẠI: {date_str}. Dùng giá thị trường Việt Nam {month_year}.

=== BẢNG NEO GIÁ THAM KHẢO (VNĐ – xe máy phổ thông) ===
| Loại sửa chữa              | Linh kiện          | Công thợ       | Tổng hợp lý   |
|----------------------------|--------------------|----------------|---------------|
| Thay lốp xe máy            | 80.000–150.000     | 20.000–30.000  | 100.000–180.000|
| Thay dầu nhớt xe máy       | 50.000–120.000     | 15.000–20.000  | 65.000–140.000 |
| Sửa thắng/phanh xe máy     | 30.000–80.000      | 30.000–60.000  | 60.000–140.000 |
| Thay bố thắng xe máy       | 20.000–50.000      | 20.000–40.000  | 40.000–90.000  |
| Sửa hệ thống điện xe máy   | 50.000–200.000     | 50.000–150.000 | 100.000–350.000|
| Thay ắc quy xe máy         | 150.000–350.000    | 20.000–30.000  | 170.000–380.000|
| Sửa xăm/vá lốp xe máy      | 15.000–40.000      | 15.000–30.000  | 30.000–70.000  |
| Sửa kính chiếu hậu vỡ      | 50.000–200.000     | 20.000–50.000  | 70.000–250.000 |
| Sơn lại nhựa/vỏ xe máy     | 100.000–400.000    | 50.000–200.000 | 150.000–600.000|
| Thay bugi xe máy            | 20.000–50.000      | 15.000–25.000  | 35.000–75.000  |
| Vá xe (đường/lốp thường)   | 10.000–20.000      | 10.000–20.000  | 20.000–40.000  |
| Sửa/thay nhông xích đĩa    | 100.000–300.000    | 50.000–100.000 | 150.000–400.000|
| Xe trầy xước nhẹ sơn       | 30.000–100.000     | 30.000–80.000  | 60.000–180.000 |
| Nứt vỡ đèn xe máy          | 80.000–250.000     | 20.000–50.000  | 100.000–300.000|
| Thay nhớt hộp số (tay ga)  | 30.000–60.000      | 15.000–20.000  | 45.000–80.000  |
(Với ô tô: nhân hệ số 3–6x so với xe máy tùy hạng xe)

QUY TẮC ĐỊNH GIÁ BẮT BUỘC:
- Dựa VÀO BẢNG NEO GIÁ trên, chọn hàng gần nhất với hư hỏng trong ảnh
- Khoảng giá PHẢI HẸP: chênh lệch tối đa 30% (ví dụ: 100k–130k)
- parts_recommended = (parts_min + parts_max) / 2
- labor_recommended = (labor_min + labor_max) / 2  
- total_recommended = parts_recommended + labor_recommended
- Luôn làm tròn đến 5.000 VNĐ gần nhất

Trả về JSON THUẦN TÚY theo đúng format sau, KHÔNG thêm bất kỳ text nào khác:

{{
  "diagnosis": "Tên hỏng hóc ngắn gọn (tối đa 80 ký tự)",
  "severity": "Nhẹ",
  "details": "Mô tả chi tiết 3-4 câu (tiếng Việt)",
  "root_cause": "Nguyên nhân gốc (1 câu)",
  "parts_needed": ["Tên linh kiện 1"],
  "parts_cost": "80.000 – 150.000 VNĐ",
  "parts_recommended": "115.000 VNĐ",
  "labor_cost": "20.000 – 30.000 VNĐ",
  "labor_recommended": "25.000 VNĐ",
  "estimated_price": "100.000 – 180.000 VNĐ",
  "total_recommended": "140.000 VNĐ",
  "price_note": "Giá tham khảo {month_year}. Chính hãng cao hơn ~30%. Hỏi ít nhất 2 thợ.",
  "recommended_action": "Hành động cụ thể (1 câu)",
  "can_drive": true,
  "urgency_level": 2,
  "warning_signs": null
}}

Nếu ảnh không rõ/không phải xe:
{{"diagnosis":"Ảnh không rõ – cần chụp lại","severity":"Nhẹ",
  "details":"Không nhận dạng được.","root_cause":"Không xác định",
  "parts_needed":[],"parts_cost":"Chưa xác định","parts_recommended":null,
  "labor_cost":"Chưa xác định","labor_recommended":null,
  "estimated_price":"Chưa xác định","total_recommended":null,
  "price_note":"Cần ảnh rõ hơn","recommended_action":"Chụp lại ảnh rõ hơn",
  "can_drive":true,"urgency_level":1,"warning_signs":null}}

CHỈ TRẢ VỀ JSON THUẦN TÚY, KHÔNG CÓ ```json```, KHÔNG BẤT KỲ TEXT NÀO KHÁC.
"""


def get_fallback_result(reason=""):
    return {
        "diagnosis": "Cần kiểm tra trực tiếp (AI tạm thời không khả dụng)",
        "severity": "Trung bình",
        "details": f"Không thể phân tích tự động lúc này. {reason} Vui lòng mô tả vấn đề với thợ.",
        "root_cause": "Chưa xác định",
        "parts_needed": [],
        "parts_cost": "Cần kiểm tra trực tiếp",
        "labor_cost": "Cần kiểm tra trực tiếp",
        "estimated_price": "Cần kiểm tra trực tiếp",
        "price_note": "Nên hỏi ít nhất 2 thợ để so sánh giá.",
        "recommended_action": "Liên hệ thợ cứu hộ để được kiểm tra trực tiếp",
        "can_drive": False,
        "urgency_level": 3,
        "warning_signs": None,
        "ai_powered": False,
    }


def save_report(request, result: dict):
    """Save AI result to DB. Import here to avoid circular at module level."""
    from .models import AIReport
    try:
        customer = request.user if request.user.is_authenticated else None
        AIReport.objects.create(
            customer=customer,
            diagnosis=result.get('diagnosis', ''),
            severity=result.get('severity', ''),
            details=result.get('details', ''),
            parts_cost=result.get('parts_cost', ''),
            labor_cost=result.get('labor_cost', ''),
            estimated_price=result.get('estimated_price', ''),
            price_note=result.get('price_note', ''),
            recommended_action=result.get('recommended_action', ''),
            can_drive=result.get('can_drive', True),
            urgency_level=result.get('urgency_level', 1),
            ai_powered=result.get('ai_powered', True),
        )
    except Exception:
        pass  # Never crash the analysis if saving fails


class AnalyzeDamageView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({"error": "Vui lòng tải ảnh lên"}, status=400)

        image_data = file_obj.read()
        mime_type = file_obj.content_type or 'image/jpeg'

        if not GEMINI_AVAILABLE:
            result = {**get_fallback_result("(Thư viện Gemini chưa cài đặt)"), "ai_powered": False}
            save_report(request, result)
            return Response(result)

        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            result = {**get_fallback_result("(Chưa cấu hình API key)"), "ai_powered": False}
            save_report(request, result)
            return Response(result)

        try:
            genai.configure(api_key=api_key)

            prompt_text = build_prompt()
            image_part = {
                "mime_type": mime_type,
                "data": base64.b64encode(image_data).decode('utf-8')
            }

            response = None
            last_error = None
            cfg = get_gen_config()  # temperature=0 for consistency

            # ── 1. Try gemini-2.0-flash WITH Google Search grounding ──
            try:
                model = genai.GenerativeModel(
                    'gemini-2.0-flash',
                    tools=[{'google_search': {}}],
                )
                response = model.generate_content(
                    [prompt_text, {"inline_data": image_part}],
                    generation_config=cfg,
                    tool_config={'function_calling_config': {'mode': 'AUTO'}},
                )
            except Exception as grounding_err:
                response = None
                last_error = grounding_err

            # ── 2. Fallback chain without grounding ──
            if response is None:
                for model_name in [
                    'gemini-2.0-flash',
                    'gemini-2.5-flash',
                    'gemini-1.5-flash-latest',
                    'gemini-pro-vision',
                ]:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(
                            [prompt_text, {"inline_data": image_part}],
                            generation_config=cfg,
                        )
                        break
                    except Exception as model_err:
                        last_error = model_err
                        continue

            if response is None:
                raise last_error

            raw_text = response.text.strip()
            # Strip markdown code fences if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()

            result = json.loads(raw_text)
            result['ai_powered'] = True
            # Normalise list field to avoid frontend issues
            if not isinstance(result.get('parts_needed'), list):
                result['parts_needed'] = []
            save_report(request, result)
            return Response(result)

        except json.JSONDecodeError:
            result = {
                "diagnosis": response.text[:150] if 'response' in locals() else "Kết quả không đọc được",
                "severity": "Trung bình",
                "details": "AI đã phân tích nhưng kết quả không đúng format. Vui lòng thử lại.",
                "root_cause": "Không xác định",
                "parts_needed": [],
                "parts_cost": "Cần kiểm tra",
                "labor_cost": "Cần kiểm tra",
                "estimated_price": "Cần kiểm tra trực tiếp",
                "price_note": "Nên hỏi ít nhất 2 thợ để so sánh giá.",
                "recommended_action": "Liên hệ thợ để được tư vấn",
                "can_drive": False,
                "urgency_level": 3,
                "warning_signs": None,
                "ai_powered": True,
            }
            save_report(request, result)
            return Response(result)

        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "400" in error_msg:
                result = get_fallback_result("(API key không hợp lệ)")
            elif "quota" in error_msg.lower():
                result = get_fallback_result("(Đã hết quota miễn phí hôm nay)")
            else:
                result = get_fallback_result(f"(Lỗi kết nối: {error_msg[:80]})")
            result['ai_powered'] = False
            save_report(request, result)
            return Response(result)

# ─────────────────────────────────────────
#  AIReport History & Management Views
# ─────────────────────────────────────────

class AIReportListView(APIView):
    """GET  /api/ai/history/  – list current user's AI reports (newest first)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .models import AIReport
        reports = AIReport.objects.filter(customer=request.user)[:50]
        data = [{
            'id': r.id,
            'diagnosis': r.diagnosis,
            'severity': r.severity,
            'details': r.details,
            'parts_cost': r.parts_cost,
            'labor_cost': r.labor_cost,
            'estimated_price': r.estimated_price,
            'price_note': r.price_note,
            'recommended_action': r.recommended_action,
            'can_drive': r.can_drive,
            'urgency_level': r.urgency_level,
            'ai_powered': r.ai_powered,
            'created_at': r.created_at.isoformat(),
        } for r in reports]
        return Response(data)


class AIReportDeleteView(APIView):
    """DELETE  /api/ai/history/<id>/delete/  – delete one report (owner only)"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        from .models import AIReport
        try:
            report = AIReport.objects.get(pk=pk, customer=request.user)
            report.delete()
            return Response({"message": "Đã xóa"})
        except AIReport.DoesNotExist:
            return Response({"error": "Không tìm thấy"}, status=404)


class AIReportCleanupView(APIView):
    """
    DELETE  /api/ai/history/cleanup/
    Deletes all reports older than `days` days for the current user.
    Query param: ?days=30  (default 60)

    Server-side: Can also be scheduled as a cron job to auto-clean ALL users.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        from .models import AIReport
        days = int(request.query_params.get('days', 60))
        cutoff = timezone.now() - timedelta(days=days)
        deleted_count, _ = AIReport.objects.filter(
            customer=request.user,
            created_at__lt=cutoff
        ).delete()
        return Response({
            "message": f"Đã xóa {deleted_count} báo cáo cũ hơn {days} ngày"
        })

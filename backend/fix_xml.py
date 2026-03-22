import codecs

fpath = r'C:\Users\ASUS\.gemini\antigravity\brain\4dc3daa2-a884-45dc-949b-3e6c76a75a2a\chuong3_phan2.md'
with codecs.open(fpath, 'r', 'utf-8') as f:
    text = f.read()

start_marker = '### 3.8.1. Sequence Diagram — Luồng gọi cứu hộ SOS'
end_marker = '## 3.9. Sơ đồ trạng thái (State Machine Diagram)'

idx1 = text.find(start_marker)
idx2 = text.find(end_marker)

new_section = f"""### 3.8.1. Sequence Diagram — Luồng gọi cứu hộ SOS

Sơ đồ này mô tả luồng tương tác đầy đủ giữa Khách hàng, Frontend Vue.js, Backend API, SQLite Database và module bên ngoài kể từ khi Khách bấm "Gọi cứu hộ" cho đến khi hoàn tất thanh toán.

`[SƠ ĐỒ: Import XML bên dưới vào DrawIO — Extras → Edit Diagram]`

```xml
<mxfile host="app.diagrams.net">
  <diagram name="Sequence - SOS Flow">
    <mxGraphModel width="1060" height="780">
      <root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>

        <!-- LIFELINE HEADERS -->
        <mxCell id="lh1" value="Khách hàng" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="20" y="20" width="130" height="740" as="geometry"/>
        </mxCell>
        <mxCell id="lh2" value="Frontend (Vue)" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="210" y="20" width="140" height="740" as="geometry"/>
        </mxCell>
        <mxCell id="lh3" value="Backend (Django)" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="420" y="20" width="155" height="740" as="geometry"/>
        </mxCell>
        <mxCell id="lh4" value="SQLite DB" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="20" width="120" height="740" as="geometry"/>
        </mxCell>
        <mxCell id="lh5" value="Thợ cứu hộ" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="870" y="20" width="130" height="740" as="geometry"/>
        </mxCell>

        <!-- MESSAGES -->
        <mxCell id="m1" value="1. Bật GPS, chọn xe, ảnh hư hỏng" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh1" target="lh2">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="100" y="80"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m2" value="2. POST /api/bookings/sos/ {{lat, lon, type}}" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh2" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="290" y="120"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m3" value="3. SELECT thợ rảnh trong 5km" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh4">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="500" y="160"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m4" value="4. [danh sách thợ rảnh]" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh4" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="700" y="200"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m5" value="5. 200 OK {{mechanics[]}}" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh2">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="490" y="240"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m6" value="6. Hiển thị danh sách thợ trên bản đồ" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh2" target="lh1">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="280" y="280"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m7" value="7. Chọn thợ → Xác nhận gọi" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh1" target="lh2">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="100" y="320"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m8" value="8. POST /api/bookings/create/ {{mechanic_id...}}" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh2" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="290" y="360"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m9" value="9. INSERT Booking (PENDING)" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh4">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="500" y="400"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m10" value="10. 201 Created {{booking_id}}" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh2">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="490" y="440"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m11" value="11. GET /mechanic/list/ (mỗi 15s)" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh5" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="930" y="480"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m12" value="12. Thợ Nhận đơn → PATCH ACCEPTED" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh5" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="930" y="520"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m13" value="13. UPDATE Booking.status = ACCEPTED" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh4">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="500" y="560"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m14" value="14. Khách tracking → thấy thợ di chuyển" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh2">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="490" y="600"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m15" value="15. Thợ PATCH COMPLETED + Nhập chi phí" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh5" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="930" y="640"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m16" value="16. Khách Chuyển khoản → VietQR" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh2" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="290" y="680"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m17" value="17. Khách PATCH payment=PAID" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh2">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="490" y="720"/></Array></mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 3.8.2. Sequence Diagram — Luồng Chẩn đoán AI (Gemini)

```xml
<mxfile host="app.diagrams.net">
  <diagram name="Sequence - AI Diagnosis">
    <mxGraphModel width="870" height="530">
      <root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <mxCell id="lh1" value="Người dùng" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="20" y="20" width="130" height="480" as="geometry"/>
        </mxCell>
        <mxCell id="lh2" value="AIScreen (Vue.js)" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="210" y="20" width="160" height="480" as="geometry"/>
        </mxCell>
        <mxCell id="lh3" value="Django Backend" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="430" y="20" width="160" height="480" as="geometry"/>
        </mxCell>
        <mxCell id="lh4" value="Google Gemini API" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="650" y="20" width="200" height="480" as="geometry"/>
        </mxCell>

        <mxCell id="m1" value="1. Cung cấp file ảnh/âm thanh" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh1" target="lh2">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="100" y="90"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m2" value="2. POST /api/ai/analyze-damage/" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh2" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="300" y="140"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m3" value="3. Build prompt" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=horizontal;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="560" y="180"/><mxPoint x="560" y="210"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m4" value="4. POST Gemini generateContent()" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh4">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="520" y="250"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m5" value="5. 200 OK {{JSON}}" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh4" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="740" y="300"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m6" value="6. Lưu lịch sử chẩn đoán" style="html=1;verticalAlign=bottom;endArrow=block;edgeStyle=elbowEdgeStyle;elbow=horizontal;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh3">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="560" y="340"/><mxPoint x="560" y="370"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m7" value="7. 201 {{report}}" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh3" target="lh2">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="500" y="410"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="m8" value="8. Hiển thị kết quả" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;edgeStyle=elbowEdgeStyle;elbow=vertical;curved=0;rounded=0;" edge="1" parent="1" source="lh2" target="lh1">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="280" y="450"/></Array></mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

"""

if idx1 > -1 and idx2 > -1:
    text = text[:idx1] + new_section + text[idx2:]
    with codecs.open(fpath, 'w', 'utf-8') as f:
        f.write(text)
    print("Fixed both diagrams.")
else:
    print("Could not find markers.")

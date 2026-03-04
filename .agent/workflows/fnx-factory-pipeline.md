---
description: Toàn bộ quy trình từ dữ liệu thô đến báo cáo bảo chứng.
---

# WORKFLOW: FNX Talent Factory Pipeline

Dây chuyền sản xuất nhân tài được kích hoạt theo các bước sau:

1. **Giai đoạn Ingestion (Nhập liệu)**
   - Kích hoạt `yearbook-ingestion` Skill khi có dữ liệu mới.
   - Phát sự kiện `RAW_DATA_RECEIVED`.

2. **Giai đoạn Enrichment (Làm giàu)**
   - SourcingAgent thực hiện `mcp-social-hunt` để cập nhật ID số.
   - Phát sự kiện `PROFILE_READY`.

3. **Giai đoạn Assessment (Định danh)**
   - AssessmentAgent thực hiện `competency-assessment` Skill.
   - Ánh xạ kinh nghiệm sang **Building 21**.
   - Phát sự kiện `COMPETENCY_MEASURED`.

4. **Giai đoạn Matching (Khớp lệnh)**
   - Khi có `JD_SUBMITTED`, JDDecoderAgent thực hiện `jd-decoding` Skill.
   - MatchingAgent thực hiện `talent-fit-matching` Skill.

5. **Giai đoạn Delivery (Xuất xưởng)**
   - ReportingAgent thực hiện `insight-report-generation` Skill.
   - Xuất bản báo cáo **FNX Insight Report**.

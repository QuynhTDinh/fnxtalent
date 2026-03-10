---
description: Quy trình AI tạo Google Forms survey từ yêu cầu đầu vào.
---

# WORKFLOW: Survey Creation Pipeline

Quy trình tự động tạo khảo sát Google Forms thông qua hệ thống Agent AI.

1. **Nhận yêu cầu** (Input)
   - User chọn nhóm survey: `student_career` / `enterprise_hr` / `working_pro`
   - Nhập mô tả cụ thể: mục tiêu, đối tượng, số câu hỏi mong muốn
   - Gọi: `POST /api/survey/design`

2. **Thiết kế nội dung** (SurveyDesignerAgent)
   - Agent nhận brief → tạo survey blueprint (JSON)
   - Blueprint gồm: title, description, sections[], questions[]
   - Mỗi question có: text, type, options[], required, helpText
   - Phát sự kiện `SURVEY_DESIGNED`

3. **Đánh giá chất lượng** (SurveyEvaluatorAgent)
   - Chấm điểm 1-10: Clarity, Completeness, Bias, Length, Actionability
   - Nếu avg score ≥ 7 → chuyển bước 4
   - Nếu avg score < 7 → gửi feedback → quay lại bước 2 (tối đa 2 lần)
   - Phát sự kiện `SURVEY_EVALUATED`

4. **Publish lên Google Forms** (SurveyPublisherAgent)
   - Kết nối Google Forms API (OAuth 2.0)
   - Tạo form → thêm câu hỏi → lấy URL
   - Phát sự kiện `SURVEY_PUBLISHED`

5. **Trả kết quả** (Output)
   - Form URL (respondent link)
   - Edit URL (cho user chỉnh sửa trên Google Forms)
   - Evaluation scores

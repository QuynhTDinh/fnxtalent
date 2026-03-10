---
name: survey-generation
description: Kỹ năng tạo nội dung khảo sát (survey) phù hợp với nhóm đối tượng, sử dụng AI và publish lên Google Forms.
agents: [SurveyDesignerAgent, SurveyEvaluatorAgent, SurveyPublisherAgent]
---

# SKILL: Survey Generation

## Mục tiêu
Tạo survey chất lượng cao, phù hợp mục tiêu nghiên cứu, và publish tự động lên Google Forms.

## Nhóm survey hỗ trợ

| Category | Template | Đối tượng |
|---|---|---|
| `student_career` | Khảo sát nhu cầu việc làm sinh viên | SV sắp/mới tốt nghiệp |
| `enterprise_hr` | Khảo sát nhu cầu nhân sự doanh nghiệp | HR, nhà tuyển dụng |
| `working_pro` | Khảo sát nhu cầu người đi làm | Người đi làm 1-10 năm |

## Quy trình

1. **Tiếp nhận brief**: Nhóm survey, mục tiêu, đối tượng, số câu hỏi (10-25)
2. **Thiết kế**: SurveyDesignerAgent tạo blueprint JSON
   - Sử dụng few-shot templates từ `templates/survey/`
   - Question types: RADIO, CHECKBOX, TEXT, PARAGRAPH_TEXT, SCALE, DROPDOWN
3. **Đánh giá**: SurveyEvaluatorAgent chấm 5 tiêu chí (Clarity, Completeness, Bias, Length, Actionability)
   - Score ≥ 7/10 → Pass
   - Score < 7 → Feedback → redesign (max 2 vòng)
4. **Publish**: SurveyPublisherAgent tạo Google Form qua API
5. **Trả kết quả**: Form URL + Edit URL + Evaluation scores

## Cấu trúc Blueprint (Output)

```json
{
  "title": "Khảo sát nhu cầu việc làm sinh viên 2026",
  "description": "Khảo sát nhằm...",
  "category": "student_career",
  "sections": [
    {
      "title": "Thông tin cá nhân",
      "questions": [
        {
          "text": "Bạn đang theo học chuyên ngành nào?",
          "type": "RADIO",
          "options": ["CNTT", "Kinh tế", "Kỹ thuật", "Khác"],
          "required": true,
          "helpText": ""
        }
      ]
    }
  ]
}
```

## Templates
- `templates/survey/student_career.json` — Mẫu khảo sát sinh viên
- `templates/survey/enterprise_hr.json` — Mẫu khảo sát doanh nghiệp
- `templates/survey/working_pro.json` — Mẫu khảo sát người đi làm

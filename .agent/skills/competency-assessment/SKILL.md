---
name: competency-assessment
description: Kỹ năng phân tích và ánh xạ kinh nghiệm làm việc sang khung năng lực Building 21.
agents: [AssessmentAgent]
---

# SKILL: Competency Assessment

## Mục tiêu
Phân tích văn bản kinh nghiệm (Resume/Yearbook) và định lượng hóa thành các cấp độ năng lực từ 1 đến 5 dựa trên khung Building 21.

## Quy trình (Workflow)
1. **Lắng nghe**: Sự kiện `PROFILE_READY`.
2. **Trích xuất**: Lấy các đoạn văn bản mô tả dự án và vai trò.
3. **Phân tích**: Đối chiếu với `framework_definition.md` để xác định Area và Level.
4. **Kiểm chứng**: Tìm kiếm các từ khóa và kết quả định lượng (ví dụ: "giảm 20% chi phí" -> Level 4 Systems Thinking).
5. **Ghi nhận**: Tạo ma trận năng lực kèm theo bằng chứng.

## Cấu trúc Phản hồi (Output Template)
Sử dụng template tại `./templates/assessment_result.json`.

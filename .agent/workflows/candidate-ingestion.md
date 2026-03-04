---
name: candidate-ingestion-workflow
description: Quy trình từ việc nhận hồ sơ thô đến khi có ma trận năng lực số hóa.
---

# WORKFLOW: Candidate Ingestion & Assessment

Quy trình này được sử dụng khi có ứng viên mới gia nhập hệ thống FNX.

## Các bước thực hiện
1. **[Skill: yearbook-parsing]**: Trích xuất dữ liệu từ file PDF kỷ yếu hoặc CV.
2. **[Skill: data-normalization]**: Chuẩn hóa các thông tin cá nhân.
3. **[Skill: mcp-enrichment]**: Truy vấn LinkedIn/Scholar để cập nhật thêm các thành tựu mới nhất.
4. **[Skill: b21-mapping]**: AI thực hiện ánh xạ toàn bộ kinh nghiệm sang khung Building 21.
5. **[Skill: evidence-audit]**: Kiểm chứng các bằng chứng và tính toán điểm tin cậy (Trust Score).

## Vai trò các Agent
- **SourcingAgent**: Thực hiện bước 1, 2, 3.
- **AssessmentAgent**: Thực hiện bước 4, 5.

---
name: active-sourcing-workflow
description: Quy trình tìm kiếm ứng viên chủ động khi không có sẵn nguồn dữ liệu nội bộ.
---

# WORKFLOW: Active Sourcing & Talent Hunting

Sử dụng quy trình này khi Database hiện tại không đủ đáp ứng yêu cầu của JD.

## Các bước thực hiện
1. **[Skill: jd-analysis]**: Lấy các từ khóa và tiêu chí quan trọng từ JD.
2. **[Skill: active-hunting]**: Kích hoạt bộ máy tìm kiếm bên ngoài để quét danh sách ứng viên tiềm năng.
3. **[Skill: mcp-search]**: Thu thập thông tin chi tiết cho từng Lead tìm được.
4. **[Skill: data-normalization]**: Làm sạch dữ liệu thu được về chuẩn FNX.
5. **[Skill: candidate-ingestion-workflow]**: Đẩy các Lead chất lượng vào quy trình đánh giá (Assessment).

## Vai trò các Agent
- **JDDecoderAgent**: Cung cấp "bản đồ" tìm kiếm (Bước 1).
- **SourcingAgent**: Thực hiện săn lùng và thu thập (Bước 2, 3, 4).
- **FactoryCoordinator**: Điều phối việc chuyển Lead sang AssessmentAgent.

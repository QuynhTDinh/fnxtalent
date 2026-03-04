---
name: jd-analysis
category: matching
description: Kỹ năng sử dụng AI để bóc tách các yêu cầu kỹ thuật, tư duy và kỹ năng mềm từ JD của doanh nghiệp.
---

# SKILL: JD Analysis & Decoding

## Mục tiêu
Chuyển đổi một đoạn văn bản JD không cấu trúc thành một ma trận yêu cầu (Requirement Matrix) theo chuẩn Building 21.

## Quy trình xử lý
1. **Identify Explicit Reqs**: Tìm các yêu cầu đã ghi rõ (ví dụ: "Biết lập trình Python").
2. **Discover Implicit Reqs**: Sử dụng AI để suy luận các yêu cầu ngầm định (ví dụ: "Làm việc tại nhà máy lọc dầu" -> Cần HOS.1 Quản lý an toàn).
3. **Weighting**: Gán trọng số (Weight) cho từng năng lực dựa trên mức độ quan trọng trong JD.

## Templates
- `./templates/jd_matrix_schema.json`

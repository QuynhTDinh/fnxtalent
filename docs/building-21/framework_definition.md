# Khung năng lực Building 21 (FNX Mapping)

Tài liệu này định nghĩa cách hệ thống FNX sử dụng và ánh xạ khung năng lực từ Building 21 sang mô hình "Lõi nhân sự" của dự án.

## 1. Phân loại Nhóm năng lực

Hệ thống FNX chia năng lực thành 3 nhóm chính dựa trên taxonomy của Building 21:

| Nhóm FNX | Nguồn Building 21 (Areas) | Mô tả |
| :--- | :--- | :--- |
| **Mindset** (Tư duy) | Habits of Success (HOS), Personal Development (PD) | Tập trung vào khả năng tự quản lý, thiết lập mục tiêu, tư duy hệ thống và thích ứng. |
| **Skills** (Kỹ năng) | Workforce (WF), English Language Arts (ELA) | Kỹ năng thực thi, giao tiếp, viết lách chuyên môn và giải quyết vấn đề thực tế. |
| **Knowledge** (Kiến thức) | Science (SCI), Mathematics (MATH), Social Studies (SS) | Kiến thức nền tảng và chuyên sâu về ngành Hóa và các lĩnh vực liên quan. |

## 2. Ánh xạ Cấp độ (Level Mapping)

Building 21 sử dụng thang điểm từ 2-12 (tương ứng với các khối lớp học thuật). FNX chuyển đổi sang thang điểm 1-5 cho môi trường doanh nghiệp:

| Cấp độ FNX | Tên gọi | Ánh xạ B21 | Mô tả năng lực |
| :--- | :--- | :--- | :--- |
| **1** | Foundational (Nền tảng) | Level 2 - 4 | Có hiểu biết sơ bộ, cần sự hướng dẫn chi tiết khi thực hiện. |
| **2** | Developing (Đang phát triển) | Level 6 | Có thể thực hiện các nhiệm vụ cơ bản với sự giám sát ít hơn. |
| **3** | Proficient (Thành thạo) | Level 8 | Đạt chuẩn yêu cầu của doanh nghiệp, thực hiện độc lập tốt. |
| **4** | Advanced (Nâng cao) | Level 10 | Có khả năng giải quyết vấn đề phức tạp, tư duy hệ thống mạnh. |
| **5** | Mastery (Bậc thầy) | Level 12 | Chuyên gia đầu ngành, có khả năng dẫn dắt và bảo chứng chất lượng. |

## 3. Cấu trúc dữ liệu (Database Schema)

Hệ thống sẽ lưu trữ theo cấu trúc:
- **Area**: Nhóm lớn (ví dụ: HOS)
- **Competency**: Nhóm năng lực cụ thể (ví dụ: HOS.1 - Quản lý công việc)
- **Skill**: Kỹ năng chi tiết kèm rubric (ví dụ: HOS.1.1 - Thiết lập mục tiêu)
- **Rubric**: Mô tả hiệu suất (Performance Descriptors) cho từng cấp độ.

---
*Tài liệu này được tạo tự động dựa trên phân tích từ building21.org và Google Sheets bổ trợ.*

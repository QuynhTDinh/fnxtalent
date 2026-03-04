# FNX Factory Design System

## 1. Nguyên tắc thiết kế (Design Principles)
- **Modularization**: Mỗi Skill phải là một module độc lập, có thể tái sử dụng.
- **Strict Typing**: Mọi dữ liệu trao đổi giữa các Skill phải tuân thủ JSON Schema đã định nghĩa.
- **Fail-safe**: Mỗi Skill phải có cơ chế xử lý lỗi và trả về thông báo lỗi rõ ràng.

## 2. Tiêu chuẩn giao tiếp (Communication Standards)
- **Language**: Ưu tiên sử dụng tiếng Việt cho các báo cáo người dùng, tiếng Anh cho các định danh kỹ thuật.
- **Event Bus**: Mọi kết quả từ Skill phải được phát đi thông qua Event Bus với Payload chuẩn.

## 3. Cấu trúc Dữ liệu chuẩn (Shared Schemas)
- **Competency**: `{ "code": string, "level": 1-5, "evidence": string }`
- **Candidate**: `{ "id": string, "fullName": string, "competencies": Array<Competency> }`
- **JD**: `{ "id": string, "requirements": Array<Competency>, "weights": Object }`

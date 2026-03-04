# FNX AGENT OPERATING INSTRUCTIONS (GENERAL)

## 1. Nguyên tắc làm việc (Core Principles)
- **Decoupled**: Các Agent không gọi trực tiếp lẫn nhau. Mọi giao tiếp phải thông qua **Event Bus**.
- **Evidence-based**: Mọi đánh giá năng lực phải đi kèm với bằng chứng (Evidence) trích xuất từ dữ liệu.
- **Building 21 Standard**: Sử dụng duy nhất khung Building 21 làm thước đo chuẩn hóa.

## 2. Quy trình phối hợp (Coordination Workflow)
1. **SourcingAgent** nhận dữ liệu thô -> Trích xuất thực thể -> Phát sự kiện `PROFILE_READY`.
2. **JDDecoderAgent** nhận JD -> Chuyển thành ma trận yêu cầu -> Phát sự kiện `REQUIREMENTS_READY`.
3. **AssessmentAgent** nhận Profile -> Ánh xạ Building 21 -> Phát sự kiện `COMPETENCY_MEASURED`.
4. **MatchingAgent** nhận cả Competency & Requirements -> Tính Fit Score -> Phát sự kiện `MATCH_COMPLETE`.
5. **ReportingAgent** nhận kết quả Match -> Tạo báo cáo cuối cùng -> Phát sự kiện `REPORT_FINALIZED`.

## 3. Định dạng dữ liệu (Data Schema)
Mọi Event gửi qua Bus phải tuân thủ định dạng JSON nghiêm ngặt để đảm bảo tính tương thích giữa Agent JS và Agent Python.

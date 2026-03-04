---
name: jd-decoding
description: Phân tích mô tả công việc (JD) để trích xuất các yêu cầu cốt lõi và ánh xạ sang khung năng lực Building 21.
agents: [JDDecoderAgent]
---

# SKILL: JD Decoding

## Mục tiêu
Dịch từ ngôn ngữ "tuyển dụng" sang ngôn ngữ "năng lực số hóa" (Building 21).

## Quy trình (Workflow)
1. **Lắng nghe**: Sự kiện `JD_SUBMITTED`.
2. **Trích xuất**: Lấy các thông tin:
    - Core Responsibilities (Trách nhiệm chính).
    - Hard Skills (Kỹ năng cứng).
    - Soft Skills (Kỹ năng mềm).
    - Experience Requirements (Yêu cầu kinh nghiệm).
3. **Ánh xạ**: Đối chiếu với `framework_definition.md` để xác định:
    - Required Areas (Các mảng năng lực cần thiết).
    - Target Levels (Cấp độ kỳ vọng cho từng mảng, từ 1-5).
4. **Trọng số**: Gán trọng số (Priority: High/Medium/Low) cho từng mảng năng lực.
5. **Ghi nhận**: Tạo ma trận yêu cầu (Requirements Matrix).

## Cấu trúc Phản hồi (Output Template)
Sử dụng template tại `./templates/jd_requirements.json`.

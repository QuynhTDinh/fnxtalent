# Internal Competency Audit Workflow (Bi-annual)

**Luồng công việc (Workflow)** này quy định cách hệ thống FNX Talent Factory tiếp nhận và đánh giá năng lực của nhân sự nội bộ trong một doanh nghiệp. Khác với luồng Sourcing/Ingestion (tuyển dụng), quy trình này mang tính chất Batch Processing (xử lý hàng loạt) và đưa độ sâu của test nghiệp vụ (Combat) lên mức cao nhất.

## 1. Đầu vào (Inputs)
- **Org Chart (CSV/Excel)**: Danh sách cán bộ nhân viên, phòng ban, và Unique ID.
- **Role Benchmarks**: Profile chuẩn cho từng vị trí (Kỳ vọng Bloom 1-6 ở từng trục năng lực T-L-D).
- **Historical Evidence**: Các báo cáo, dự án, bằng sáng chế hoặc file công việc cũ mà nhân sự upload làm bằng chứng.

## 2. Quy trình cốt lõi (The Pipeline)

### Phase 1: Setup & Mapping (Orchestration)
Hệ thống nhận diện file Org Chart, bóc tách ra danh sách các `Role Title`.
- Nếu có JD tương ứng: Hệ thống đọc JD.
- Nếu không có JD: Yêu cầu doanh nghiệp map JD cơ bản (tránh AI hallucination).

### Phase 2: Combat Generation (Asynchronous Survey Injection)
- Tool/Agent sử dụng: `CombatDesignerAgent` (kế thừa `SurveyDesignerAgent`).
- Nhiệm vụ: Tự động phân tích các rủi ro vận hành nổi cộm trong `Role Title` và kiến tạo ra một bài test tình huống mô phỏng (Combat Scenario). Bài test này được xuất ra Google Forms tĩnh. Nhân viên sẽ tự đăng nhập bằng Unique ID để làm bài tự luận hoặc upload phương án xử lý rủi ro đó.

### Phase 3: Audit & Validation (Evaluator)
- Chờ nhân viên nộp bài => Hệ thống kích hoạt `AuditAssessmentAgent`.
- Đánh giá chéo bằng chứng (Historical Evidence) kết hợp với bài test Combat.
- Trả về điểm Bloom 1-6 cho bộ 11 tiêu chí competency.
- Hệ thống áp dụng `tld_map` để tính ra điểm Technique, Language, Digital cho mỗi cá nhân.

### Phase 4: Output & Feedback Loop
- **Competency Heatmap**: Tạo ma trận nhiệt cho toàn bộ Org Chart để xem "điểm sáng / điểm mù" của doanh nghiệp.
- Nhận diện Gap: In ra lộ trình Training ROI cho những nhân sự bị hụt năng lực so với Target Benchmark.

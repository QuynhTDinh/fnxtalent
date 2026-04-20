# Đánh Giá Chuyển Đổi Taxonomy Sang Master Data (SSOT Protocol & Meta-Standard)

> **Dựa trên 2 tài liệu:** 
> 1. SINGLE SOURCE OF TRUTH (SSOT) PROTOCOL
> 2. META-STANDARD SPECIFICATION

## 1. Tổng quan chiến lược (Overview)
Việc chuyển đổi Taxonomy từ dạng tĩnh trong code/YAML sang mô hình **Master Excel Data** (tuân thủ giao thức SSOT và Meta-Standard) là một quyết định kiến trúc cực kỳ xuất sắc. Nó giải quyết triệt để điểm nghẽn lớn nhất trong việc mở rộng (scaling) hệ thống: **Sự phụ thuộc của chuyên gia nhân sự (SME) vào đội ngũ kỹ thuật/AI.**

Với kiến trúc này, Antigravity AI đóng vai trò là "Data Custodian" (Người giữ cửa & quản lý phiên bản), trong khi chuyên gia HR/Domain Expert đóng vai trò là "Data Creator" (Người sáng tạo thông số).

---

## 2. Đánh giá chi tiết: Ưu / Nhược / Rủi ro

### 🌟 Ưu điểm (Pros)
1. **Dân chủ hóa dữ liệu (Democratization):** Chuyên gia HR/L&D có thể thoải mái tuning (hiệu chỉnh) Benchmark, Combat Scenarios của khách hàng trên giao diện Excel quen thuộc mà không cần biết code hay cấu trúc YAML.
2. **"Single Source of Truth" linh hoạt:** Vòng lặp `Export -> Calibrate -> Ingest -> Overwrite` với Sync_ID đảm bảo không bao giờ xảy ra tình trạng "bản Excel một đằng, AI chạy một nẻo". Mọi Báo Cáo / Trình chiếu cuối cùng đều được bảo chứng từ một nguồn duy nhất.
3. **Quản trị đa khách hàng (Version Control):** Kiến trúc phân nhánh (Master Branch cho FNX gốc, Bespoke Branch cho Client A, Client B...) giúp hệ thống có thể scale ra mô hình B2B SaaS dễ dàng.
4. **Tối ưu chất lượng AI (Anti-Hallucination):** Trường dữ liệu `Negative Indicators (Red Flags)` là một vũ khí tuyệt vời. Việc cung cấp sẵn các biểu hiện kém cỏi giúp AI có bức tranh đối chiếu 2 chiều, giảm thiểu ảo giác khi chấm điểm gap rủi ro.

### ⚠️ Nhược điểm & Hạn chế (Cons)
1. **Phức tạp hóa luồng vận hành (Over-engineering):** Đòi hỏi phải xây dựng hẳn một đường ống ETL (Extract-Transform-Load) 2 chiều (JSON/YAML ↔ Excel) với bộ validator logic cực mạnh.
2. **Phụ thuộc tốc độ con người:** Việc có vòng lặp Human-in-the-loop (chuyên gia phải tải Excel xuống, sửa, rồi nạp lại) làm mất đi tính fully-automated vốn có của một Data pipeline khép kín.

### 🚨 Rủi ro tiềm ẩn (Risks)
1. **Excel Formatting Corruption:** Chuyên gia thao tác trên Excel rất dễ có thói quen gộp ô (merge cells), sửa tên Sheet, rỗng dòng (empty rows) hoặc xóa nhầm định dạng ID (`FNX-CHEM-L2-005`). Nếu rào chắn Ingestion không xử lý khéo, hệ thống sẽ sập hoặc gán nhầm ma trận.
2. **Xung đột sửa đổi (Merge Conflicts):** Điều gì xảy ra nếu Chuyên gia A và Chuyên gia B cùng tải xuống một file (cùng Sync_ID), sửa các phần khác nhau và cùng Upload lên? Giao thức SSOT (Tài liệu 1) chưa định nghĩa rõ quy tắc chống ghi đè đồng thời (Concurrent write locks).
3. **Mắc kẹt vòng lặp Validation:** Theo tài liệu 2, có quy định *Semantic Mapping (TLD phải ánh xạ về ít nhất 02 lớp ASK)*. Nếu chuyên gia chỉ ánh xạ 1, file bị reject liên tục, họ sẽ nản hoặc thấy hệ thống quá "bắt bẻ".

---

## 3. Các Tùy chọn Triển khai (Implementation Options)

Để tối ưu hóa kiến trúc này trên hệ thống FNX Talent Factory dùng Python (như đã nâng cấp), chúng ta có 2 phương án chính để xây dựng cổng Ingestion & Validation:

### Option 1: Rule-based (Pandas / OpenPyXL thuần)
*Sử dụng Python code tĩnh để làm Validation Rule Engine.*
- **Cách làm:** Khi user upload Excel, dùng thư viện Pandas quét các cột. Chạy Regex check ID (`FNX-[A-Z]+-L[1-3]-\d{3}`), check Bloom level (chỉ được 1-6), đếm số lượng mapping.
- **Ưu điểm:** Cực lỳ nhanh, chính xác tuyệt đối, tài nguyên rẻ.
- **Nhược điểm:** Không thể check quy tắc "Bloom Consistency" (Động từ phải chuẩn theo Bloom). VD: "Nhận biết" không thể map với Bloom cấp 5.

### Option 2: AI-Agentic Validation (LLM Data Validator)
*Sử dụng một AI Agent (như Gemini 3.1 Pro) để đọc cấu trúc Data Frame.*
- **Cách làm:** Parse Excel thành JSON/Markdown table, đưa cho AI Agent với prompt "Mày là Data Validator tuân thủ Meta-Standard Protocol...". AI check các Action Verb có logic với cấp Bloom hay không, và phát hiện những chỗ chuyên gia định nghĩa Red Flag quá mâu thuẫn.
- **Ưu điểm:** Kiểm soát được **ngữ nghĩa** (Semantic Validation) rất sâu.
- **Nhược điểm:** Chậm, tốn token, AI có thể từ chối file vì nhận biết nhầm từ lóng của thị trường.

### 💡 Khuyến nghị Triển khai (Hybrid Approach)
Nên kết hợp cả 2 theo **Pipeline 2-bước (Two-stage Ingestion)**:
1. **Lớp 1 (Syntax Barrier - Python logic tĩnh):** Kiểm tra cấu trúc 3 Sheets, kiểm tra sự tồn tại của các cột, regex của Unique ID, tính nguyên vẹn của dòng. Vượt qua lớp này mới sang Lớp 2.
2. **Lớp 2 (Semantic Barrier - AI Agent):** Chuyên gia AI quét qua cột `Bloom` và `Action Descriptor`, nếu thấy sai lệch, nó trả về một cái Error log nhỏ: *"Lỗi ở Hàng 15: Mô tả là 'Ứng dụng' mà Level Bloom lại báo cấp 6 (Sáng tạo), cần xem lại"*. 

---

## 4. Lộ trình triển khai đề xuất (Phased Rollout)

Để đảm bảo hệ thống không bị "gãy" khi đột ngột chuyển sang luồng SSOT mới, thay vì code song song toàn bộ đường ống Ingestion phức tạp, chúng ta nên triển khai theo cơ chế "gối đầu" (Progressive adoption) như sau:

### Phase 1: MVP - Vòng lặp phản hồi thủ công (Manual Feedback Loop)
*Mục tiêu: Chốt chuẩn định dạng (Meta-Standard format) và quan sát hành vi của Domain Expert.*
- **Action:** Xuất (Export) taxonomy dạng thô tĩnh từ code hiện tại sang đúng chuẩn 3-Sheet Master Excel. Đưa file này lên thư mục chung của Google Drive.
- **Tương tác:** Domain Expert (SME) và team L&D sẽ trực tiếp xem, góp ý và tiến hành điền, chỉnh sửa các thông số thực tế (Benchmark, Bloom, Red flags...).
- **Sync-Gate:** **Thủ công.** Quỳnh (hoặc Operator) sẽ là người trực tiếp verify (review) lại file Excel trên Drive. Sau khi mọi thứ ổn, Quỳnh sẽ thực hiện "cập nhật ngược lại" (update bằng tay) vào Factory/Codebase.
- **Giá trị:** Dò được lỗi UX của Excel form (vd: các field quá dài, chuyên gia lười viết), chốt được Template cuối cùng trước khi tốn nguồn lực code Auto-Ingestion.

### Phase 2: Bán tự động (One-Way Automation & Hard-Validation)
*Mục tiêu: Đóng băng chuẩn cấu trúc và tự động hóa khâu Ingestion để giảm thiểu lỗi Human-error nhập liệu.*
- **Action:** Phát triển một script Python nội bộ (vd: `scripts/ingest_taxonomy.py`) vận hành theo Option 1 (Rule-based) đã đề cập ở trên. 
- **Tương tác:** Chuyên gia vẫn sửa trên Drive báo xong.
- **Sync-Gate:** Script được trigger. Nó tải file từ Drive/Local về, bắn qua màng lọc Syntax Barrier (quét ID, cấu trúc, logic ô trống). Hệ thống sinh ra một "Báo cáo lỗi" (Error Log) nếu có. Nếu xanh (Pass), file tự động sinh mã hoặc build đè dữ liệu thẳng vào Database/YAML của Factory.
- **Giá trị:** Giải phóng Quỳnh khỏi việc "nhập liệu tay", hệ thống đã nắm được cơ chế kiểm soát Syntax. 

### Phase 3: Đồng bộ toàn tự động (Two-Way Sync & AI Validator)
*Mục tiêu: Đạt chuẩn SSOT cho sản phẩm B2B SaaS phân phối đại trà.*
- **Action:** Lên UI hoàn chỉnh trên Frontend (Dashboard). Có giao diện cho phép [Export Bespoke Branch] (Xuất template riêng cho Client A) và [Upload Expert Data].
- **Tương tác:** Master Data hoàn toàn luân chuyển trong hệ sinh thái của App (thay vì trên Drive trôi nổi).
- **Sync-Gate:** Tự động hoàn toàn (Full Pipeline). Đầu vào đi qua 2 màng lọc: **Syntax Check (Python) + Semantic Check (AI Agent)**. File bị reject sẽ pop-up tại UI cho chuyên gia sửa ngay. Pass sẽ commit đè lên Database của từng Tenant/Client một cách riêng biệt bảo vệ bởi Sync_ID.
- **Giá trị:** SSOT hoàn chỉnh, nhân bản hệ thống dễ dàng cho n+ khách hàng mà tỷ lệ lỗi = 0.

---
*Tài liệu phân tích này sẽ đóng vai trò tiền đề cho việc xây dựng Ingestion Node tiếp theo của C-Factory.*

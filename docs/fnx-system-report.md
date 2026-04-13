# FNX Talent Factory v2 — Báo cáo tổng thể hệ thống

> **Ngày:** 24/03/2026  
> **Version:** 2.2.0 (MVP)  
> **Trạng thái:** ✅ Live trên Vercel — chờ data thực tế để verify  
> **URL:** [fnx-talent-factory-v2.vercel.app](https://fnx-talent-factory-v2.vercel.app)

---

## 1. Tổng quan

FNX Talent Factory là hệ thống **đánh giá và phát triển năng lực kỹ sư** theo quy trình 5 bước, sử dụng khung năng lực ASK × Katz v2.2 gồm **11 năng lực** (K3 + S5 + A3).

### Mục tiêu hệ thống
| # | Mục tiêu | Trạng thái |
|---|---|---|
| 1 | Giải mã JD → Ma trận yêu cầu năng lực | ✅ MVP |
| 2 | Đánh giá CV ứng viên → Ma trận năng lực thực tế | ✅ MVP |
| 3 | So sánh Gap (yêu cầu vs thực tế) → Báo cáo bảo chứng | ✅ MVP |
| 4 | Đề xuất chương trình đào tạo Close Gap | ⬜ Chưa |
| 5 | Bàn giao & Bảo chứng | ⬜ Chưa |

---

## 2. Kiến trúc hệ thống

### 2.1 Kiến trúc tổng thể

```
┌──────────────────────────────────────────────────────────┐
│                   FRONTEND (Vercel Static)                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐          │
│  │  /demand   │→ │  /assess   │→ │  /report   │          │
│  │  JD Input  │  │  CV Input  │  │  Gap + Radar│          │
│  │  AI Decode │  │  AI Assess │  │  Fit Score  │          │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘          │
│        │               │               │                  │
│        └───── localStorage ─────────────┘                  │
│                                                            │
│  ┌────────────┐                                            │
│  │ /taxonomy  │  Khung năng lực ASK × Katz (tra cứu)      │
│  └────────────┘                                            │
├────────────────────────────────────────────────────────────┤
│                   BACKEND (Vercel Python)                  │
│  ┌────────────────────────────────────────────────┐        │
│  │  api/main.py (FastAPI)                         │        │
│  │  - /api/assess: Đánh giá CV                    │        │
│  │  - /api/decode-jd: Giải mã JD                  │        │
│  │  - /api/match: Matching                         │        │
│  └────────────────────────────────────────────────┘        │
├────────────────────────────────────────────────────────────┤
│                   CORE ENGINE (Python)                     │
│  core/agents/      → AI Agents (JD Decoder, Assessment..) │
│  core/taxonomy/    → Competency Taxonomy v2.2 (YAML)      │
│  core/pipeline/    → DAG Pipeline orchestration            │
│  core/integrations/→ Google Sheets, Survey                 │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Luồng dữ liệu (Data Flow)

```
/demand                    /assess                   /report
┌─────────┐               ┌─────────┐               ┌─────────┐
│ Upload  │               │ Upload  │               │ Auto-   │
│ JD (PDF)│               │ CV (PDF)│               │ load    │
│    ↓    │               │    ↓    │               │    ↓    │
│ PDF.js  │               │ PDF.js  │               │ Select  │
│ Extract │               │ Extract │               │ assess  │
│    ↓    │               │    ↓    │               │    ↓    │
│ AI      │  fnx_demands[]│ AI      │fnx_assessments│ Radar   │
│ Decode  │──────────────→│ Assess  │──────────────→│ Gap     │
│    ↓    │  localStorage │    ↓    │  localStorage │ Score   │
│ Matrix  │               │ Matrix  │               │ Table   │
│ Confirm │               │ Confirm │               │         │
└─────────┘               └─────────┘               └─────────┘
```

### 2.3 Tech Stack

| Layer | Công nghệ | Ghi chú |
|---|---|---|
| **Frontend** | HTML + CSS + Vanilla JS | Apple-inspired design system |
| **PDF Extraction** | PDF.js (CDN) + Mammoth.js (CDN) | Lazy-load, client-side |
| **Charts** | Canvas API (custom) | Radar chart vẽ thuần JS |
| **Data** | `localStorage` | MVP — cần nâng cấp DB |
| **Backend** | Python (FastAPI) | Vercel Serverless |
| **AI Engine** | Keyword-based (MVP) | Cần nâng lên Gemini API |
| **Hosting** | Vercel | Free tier, auto-deploy |
| **Taxonomy** | YAML (competency_taxonomy.yaml) | 11 năng lực, 5 levels |

---

## 3. Khung năng lực (Taxonomy v2.2)

### 3.1 Cấu trúc ASK × Katz

| Nhóm | Mã | Năng lực | Katz Zone |
|---|---|---|---|
| **Knowledge** | K1 | Kiến thức chuyên ngành | 🔵 Technical |
| | K2 | Kiến thức & Nghiệp vụ kỹ thuật | 🔵 Technical |
| | K3 | Công cụ & Công nghệ | 🔵 Technical |
| **Skill** | S1 | Giao tiếp kỹ thuật | 🟠 Interpersonal |
| | S2 | Phân tích & Giải quyết vấn đề | 🟣 Conceptual |
| | S3 | Quản lý & Lên kế hoạch | 🟣 Conceptual |
| | S4 | Tư duy hệ thống | 🟣 Conceptual |
| | S5 | Phối hợp & Giao việc | 🟠 Interpersonal |
| **Attitude** | A1 | Chủ động - Cải tiến | 🟣 Conceptual |
| | A2 | Hợp tác - Tin tưởng | 🟠 Interpersonal |
| | A3 | Quan tâm - Hỗ trợ | 🟠 Interpersonal |

### 3.2 Hệ thống Level (5 bậc)

| Level | Tên | Mô tả |
|---|---|---|
| 1 | Foundational | Hiểu cơ bản, cần hướng dẫn |
| 2 | Developing | Áp dụng được dưới giám sát |
| 3 | Competent | Tự chủ trong phạm vi quen thuộc |
| 4 | Proficient | Dẫn dắt, xử lý phức tạp |
| 5 | Expert | Chiến lược, mentor, đổi mới |

### 3.3 Phân bổ Katz

| Katz Zone | Năng lực | Tỷ trọng khuyến nghị (Junior) |
|---|---|---|
| 🔵 Technical | K1, K2, K3 | ~50% |
| 🟠 Interpersonal | S1, S5, A2, A3 | ~30% |
| 🟣 Conceptual | S2, S3, S4, A1 | ~20% |

---

## 4. Các trang chức năng

### 4.1 `/demand` — Giải mã yêu cầu tuyển dụng

| Tính năng | Mô tả | Trạng thái |
|---|---|---|
| Upload JD | Kéo thả PDF/DOCX → PDF.js extract → hiển thị text | ✅ |
| Paste JD | Paste text trực tiếp vào textarea | ✅ |
| Demo JD | Pre-fill dữ liệu mẫu (NSRP petrochemical) | ✅ |
| AI Decode | Phân tích JD → trích xuất 11 năng lực + level + evidence | ✅ (keyword MVP) |
| Ma trận | Hiển thị/chỉnh sửa level (1-5) và priority (High/Med/Low) | ✅ |
| Radar Preview | Biểu đồ radar real-time khi chỉnh level | ✅ |
| Katz Distribution | Phân bổ tỷ trọng Technical/Interpersonal/Conceptual | ✅ |
| Lưu Demand | Lưu vào `fnx_demands[]` (localStorage array) | ✅ |
| Demand List | Hiển thị danh sách demands đã tạo + link → Assess | ✅ |

### 4.2 `/assess` — Đánh giá ứng viên

| Tính năng | Mô tả | Trạng thái |
|---|---|---|
| Chọn Demand | Dropdown chọn demand đã tạo (auto-load từ URL param) | ✅ |
| Demand Context | Hiển thị yêu cầu tuyển dụng bên phải (vị trí, client, comps) | ✅ |
| Upload CV | Kéo thả PDF/DOCX → PDF.js extract | ✅ |
| Demo CV | Pre-fill CV mẫu (Trần Minh Khoa — BSR operator) | ✅ |
| AI Assess | Phân tích CV → 11 năng lực + evidence | ✅ (keyword MVP) |
| Gap Indicator | Mỗi năng lực hiện ✓ / -1 / -2 so với target | ✅ |
| Dual Radar | Biểu đồ radar 2 lớp: Ứng viên (xanh) vs Yêu cầu (hồng) | ✅ |
| Fit Score | Tính % phù hợp tổng thể | ✅ |
| Lưu Assessment | Lưu vào `fnx_assessments[]` + auto-redirect → Report | ✅ |

### 4.3 `/report` — Báo cáo đánh giá

| Tính năng | Mô tả | Trạng thái |
|---|---|---|
| Assessment List | Sidebar danh sách đánh giá đã thực hiện | ✅ |
| Score Hero | Vòng tròn điểm Fit Score + color coding (xanh/cam/đỏ) | ✅ |
| Gap Analysis | Liệt kê gaps giảm dần theo mức nghiêm trọng | ✅ |
| Competency Table | Bảng đầy đủ: Mã / Năng lực / Yêu cầu / Ứng viên / Gap / Evidence | ✅ |
| Dual Radar | Biểu đồ radar so sánh lớn (480px) | ✅ |
| Đề xuất đào tạo | Chương trình close gap cá nhân hóa | ⬜ Chưa |

### 4.4 `/taxonomy` — Tra cứu khung năng lực

| Tính năng | Mô tả | Trạng thái |
|---|---|---|
| Visualizer | Hiển thị toàn bộ 11 năng lực + levels + mô tả | ✅ |
| Katz Mapping | Phân loại theo Technical/Interpersonal/Conceptual | ✅ |

---

## 5. Backend & AI Agents

### 5.1 API Endpoints

| Endpoint | Method | Chức năng | Trạng thái |
|---|---|---|---|
| `/api/assess` | POST | Đánh giá CV ↔ JD | ✅ Có nhưng chưa kết nối FE |
| `/api/decode-jd` | POST | Giải mã JD | ✅ Có nhưng chưa kết nối FE |
| `/api/match` | POST | Matching ứng viên | ✅ Có nhưng chưa kết nối FE |
| `/api/taxonomy` | GET | Lấy taxonomy data | ✅ |

### 5.2 AI Agents (Python)

| Agent | File | Chức năng | Trạng thái |
|---|---|---|---|
| JD Decoder | `jd_decoder_agent.py` | Phân tích JD → competency matrix | ✅ Code sẵn |
| Assessment | `assessment_agent.py` | Đánh giá CV → competency levels | ✅ Code sẵn |
| Matching | `matching_agent.py` | So khớp ứng viên với JD | ✅ Code sẵn |
| Survey Designer | `survey_designer_agent.py` | Tạo survey đánh giá | ✅ Code sẵn |
| Survey Publisher | `survey_publisher_agent.py` | Publish lên Google Forms | ✅ Code sẵn |

> **Lưu ý:** Các agent đã có code nhưng frontend hiện dùng **keyword-based MVP** (chạy trên browser). Chưa kết nối FE ↔ Backend API.

---

## 6. Điểm mạnh ✅

| # | Điểm mạnh | Chi tiết |
|---|---|---|
| 1 | **End-to-end flow hoàn chỉnh** | Từ JD → CV → Report, 3 bước liền mạch |
| 2 | **Khung năng lực chuẩn** | ASK × Katz v2.2, 11 năng lực, 5 levels, có nguồn gốc (Building 21, ABB) |
| 3 | **Upload PDF/DOCX** | Hỗ trợ drag-and-drop, extract text client-side, không cần server |
| 4 | **Trực quan hóa** | Radar chart, Katz distribution bars, Fit Score, Gap indicators |
| 5 | **Modular architecture** | Mỗi page độc lập, scalable, dễ maintain |
| 6 | **Live trên cloud** | Deploy Vercel, team truy cập được ngay |
| 7 | **Design system nhất quán** | Apple-inspired, clean UI, interaction animations |
| 8 | **AI Agent sẵn sàng** | Backend agents đã code, chỉ cần wire FE ↔ BE |

---

## 7. Điểm hạn chế & Rủi ro ⚠️

### 7.1 Hạn chế kỹ thuật

| # | Hạn chế | Mức độ | Giải thích |
|---|---|---|---|
| 1 | **AI keyword-based** | 🔴 Cao | Hiện AI phân tích bằng keyword matching, chưa hiểu ngữ cảnh. Có thể sai khi JD/CV viết khác từ khóa mặc định |
| 2 | **localStorage** | 🟡 Trung bình | Data mất khi xóa cache browser. Không chia sẻ được giữa devices/users. Không phù hợp production |
| 3 | **Chưa có authentication** | 🟡 Trung bình | Bất kỳ ai có URL đều truy cập được. Không phân quyền Admin/HR/Manager |
| 4 | **PDF scan không đọc được** | 🟡 Trung bình | PDF.js chỉ đọc text-based PDF. CV scan từ ảnh → không extract được |
| 5 | **FE ↔ BE chưa kết nối** | 🟡 Trung bình | Backend API và agents có sẵn nhưng frontend chưa gọi API |
| 6 | **Chưa responsive mobile** | 🟢 Thấp | Layout grid-based chưa tối ưu cho mobile |

### 7.2 Hạn chế nghiệp vụ

| # | Hạn chế | Mức độ | Giải thích |
|---|---|---|---|
| 1 | **Chưa có data thực tế** | 🔴 Cao | Toàn bộ hệ thống mới test với demo data. Chưa verify với JD/CV thực từ khách hàng |
| 2 | **Chưa validate taxonomy** | 🟡 Trung bình | 11 năng lực và mô tả level chưa được review bởi chuyên gia HR/L&D |
| 3 | **Chưa có benchmark** | 🟡 Trung bình | Không có dữ liệu so sánh chất lượng AI assess vs đánh giá bởi chuyên gia |
| 4 | **Step 4-5 chưa build** | 🟡 Trung bình | Chương trình đào tạo & Bảo chứng chưa implementation |
| 5 | **Chưa export PDF/Excel** | 🟢 Thấp | Report chỉ xem online, chưa xuất được file gửi khách |

---

## 8. Lộ trình phát triển

### Phase 1: Verify & Validate (ưu tiên, 2-3 tuần)

| Task | Mô tả | Ai làm |
|---|---|---|
| **Thu thập JD thực** | 3-5 JD từ khách hàng (NSRP, BSR, Formosa) | Team BD/HR |
| **Thu thập CV thực** | 5-10 CV ứng viên đã từng đánh giá | Team HR |
| **Test end-to-end** | Chạy JD + CV thực qua hệ thống, so output với đánh giá manual | Team + AI |
| **Review taxonomy** | Mời chuyên gia HR/L&D review 11 năng lực + level descriptions | Chuyên gia |
| **Đo accuracy** | So sánh AI output vs đánh giá chuyên gia → tính % chính xác | Team |

### Phase 2: Nâng cấp AI (2-4 tuần)

| Task | Mô tả |
|---|---|
| **Kết nối Gemini API** | Thay keyword matching bằng Gemini cho cả JD decode và CV assess |
| **Kết nối FE ↔ BE** | Frontend gọi `/api/assess` và `/api/decode-jd` thay vì xử lý client-side |
| **Gemini Document AI** | Upload PDF trực tiếp lên Gemini → đọc cả file scan/ảnh |
| **Prompt Engineering** | Tối ưu prompt cho context Việt Nam, ngành kỹ thuật |

### Phase 3: Production Ready (4-6 tuần)

| Task | Mô tả |
|---|---|
| **Database** | Chuyển localStorage → Supabase/Firebase |
| **Authentication** | Google SSO cho team nội bộ |
| **Export PDF** | Xuất báo cáo bảo chứng PDF chuyên nghiệp |
| **Step 4: Đào tạo** | AI đề xuất chương trình close gap cá nhân hóa |
| **Step 5: Bảo chứng** | Mẫu bảo chứng + workflow ký duyệt |
| **Mobile responsive** | Tối ưu UI cho tablet/mobile |

### Phase 4: Scale (tùy nhu cầu)

| Task | Mô tả |
|---|---|
| **Multi-tenant** | Nhiều khách hàng/project cùng lúc |
| **Batch processing** | Upload nhiều CV → đánh giá hàng loạt |
| **Analytics dashboard** | Thống kê xu hướng năng lực, talent pool |
| **Survey 360°** | Khảo sát đánh giá 360 tự động qua Google Forms |

---

## 9. Cách truy cập & Demo

### URLs

| Trang | URL | Mô tả |
|---|---|---|
| Home | [fnx-talent-factory-v2.vercel.app](https://fnx-talent-factory-v2.vercel.app) | → Demand |
| Demand | [/demand](https://fnx-talent-factory-v2.vercel.app/demand) | Giải mã JD |
| Assess | [/assess](https://fnx-talent-factory-v2.vercel.app/assess) | Đánh giá CV |
| Report | [/report](https://fnx-talent-factory-v2.vercel.app/report) | Báo cáo |
| Taxonomy | [/taxonomy](https://fnx-talent-factory-v2.vercel.app/taxonomy) | Khung năng lực |

### Demo nhanh (3 phút)

1. Vào `/demand` → Click **"📄 Demo JD"** → Click **"🔍 Giải mã bằng AI"**
2. Review ma trận → Click **"✓ Xác nhận"** → Click **"→ Assess"**
3. Vào `/assess` → Click **"👤 Demo CV"** → Click **"🔍 Đánh giá bằng AI"**
4. Review kết quả + Fit Score → Click **"✓ Xác nhận & Xem Report"**
5. Xem báo cáo: Score Hero + Gap Analysis + Radar

> **Lưu ý:** Demo data sử dụng JD vị trí "Kỹ sư vận hành DCS" tại NSRP và CV "Trần Minh Khoa" — Kỹ sư Hóa học từ BSR.

---

## 10. Cấu trúc mã nguồn

```
fnx-talent-factory-v2/
├── dashboard/               # Frontend (HTML/CSS/JS)
│   ├── demand.html          # Giải mã JD (52KB)
│   ├── assess.html          # Đánh giá CV (50KB)
│   ├── index.html           # Report (27KB) — route: /report
│   ├── taxonomy.html        # Tra cứu taxonomy (44KB)
│   ├── styles.css           # Design system (23KB)
│   ├── wizard.html/js/css   # ⚠️ Legacy — sẽ retire
│   └── history.html         # ⚠️ Legacy — sẽ retire
├── api/
│   └── main.py              # FastAPI endpoints
├── core/
│   ├── agents/              # AI agents (5 agents)
│   ├── taxonomy/            # YAML taxonomy + loader
│   ├── pipeline/            # DAG orchestration
│   └── integrations/        # Google Sheets, Survey
├── data/                    # Sample data + templates
├── docs/                    # Documentation
├── .agent/                  # AI workflows & skills
└── vercel.json              # Routing config
```

---

## 11. Kết luận

### Đã làm được
- ✅ MVP end-to-end: JD → CV → Report trên cloud
- ✅ Khung năng lực 11 competencies theo chuẩn ASK × Katz
- ✅ Upload PDF/DOCX không cần server
- ✅ Trực quan: radar, gap, fit score
- ✅ Backend agents sẵn sàng kết nối

### Cần làm ngay
- 🔴 **Test với data thực** — đây là ưu tiên #1
- 🔴 **Nâng cấp AI** từ keyword → Gemini để tăng độ chính xác
- 🟡 Kết nối Frontend ↔ Backend API
- 🟡 Review taxonomy với chuyên gia

### Câu hỏi cho team
1. **Data thực:** Team có thể cung cấp 3-5 JD + 5-10 CV thực để test không?
2. **Taxonomy review:** Ai trong team sẽ review 11 năng lực + level descriptions?
3. **Ưu tiên Phase 2:** Nên tập trung Gemini AI trước hay Database/Auth trước?

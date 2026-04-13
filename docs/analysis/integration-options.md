bạn hãy xem sheet Mô tả kỹ năng & cấp độ và sheet Competency Matrix # FNX Talent Factory — Options kết hợp ABB × Building 21

> Mục đích: So sánh các phương án tích hợp 2 framework  
> Ngày: 2026-03-11

---

## Bối cảnh

**Building 21 (hiện tại)**: Framework giáo dục, mạnh về đo lường năng lực theo rubric.
- 3 nhóm: Mindset (HOS/PD) → Skills (WF/ELA) → Knowledge (SCI/MATH/SS)
- Thang 1-5 với performance descriptors chi tiết
- Focus: "Con người này BIẾT gì và LÀM ĐƯỢC gì?"

**ABB Competency Model**: Framework doanh nghiệp, mạnh về hành vi chuyên nghiệp.
- 5 Competency Pairs (2016): Safety, Customer Focus, Innovation, Ownership, Collaboration
- 4 Core Values (2024): Courage, Care, Curiosity, Collaboration
- 4 Role Levels: IC → Team Lead → Management → Leadership
- Focus: "Con người này HÀNH XỬ thế nào trong tổ chức?"

---

## Option A: "ABB as Add-on" — Bổ sung nhẹ
### Building 21 giữ nguyên làm trục chính, ABB chỉ thêm 1 lớp đánh giá phụ

```
┌─────────────────────────────────────────────┐
│           FNX ASSESSMENT REPORT             │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │   CORE ASSESSMENT (Building 21)      │  │  ← Giữ nguyên 100%
│  │   ┌──────────┬────────┬──────────┐   │  │
│  │   │ Mindset  │ Skills │Knowledge │   │  │
│  │   │  (HOS)   │  (WF)  │  (SCI)   │   │  │
│  │   └──────────┴────────┴──────────┘   │  │
│  │   Score: 1-5 per competency          │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │   CULTURE CHECK (ABB 4C)             │  │  ← Thêm mới (optional)
│  │   Courage | Care | Curiosity | Collab│  │
│  │   ○○○○○   ○○○○○  ○○○○○       ○○○○○  │  │
│  │   Qualitative only (Low/Med/High)    │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Fit Score = Building 21 Score (100%)       │
│  Culture Check = Bonus/Flag only            │
└─────────────────────────────────────────────┘
```

**Cách hoạt động:**
- Building 21 vẫn là nguồn tính Fit Score duy nhất
- ABB 4C Values thêm vào như "Culture Check" — chỉ mang tính tham khảo
- Nếu Culture Check thấp → báo cáo có cảnh báo "⚠️ Potential culture mismatch"
- Không thay đổi scoring algorithm

**Thay đổi code:**
| Component | Thay đổi |
|-----------|---------|
| `framework_definition.md` | Thêm section "Culture Indicators" |
| `assessment_agent.py` | Thêm 4 câu hỏi culture vào cuối prompt |
| `jd_decoder_agent.py` | Không đổi |
| `matching_agent.py` | Không đổi |
| Dashboard | Thêm 1 badge "Culture: ✅/⚠️" |

**Ưu điểm:**
- ✅ Rủi ro thấp, triển khai nhanh (1-2 ngày)
- ✅ Không phá vỡ hệ thống hiện tại
- ✅ Dễ rollback nếu không hiệu quả
- ✅ Phù hợp nếu FNX chủ yếu đánh giá technical talent

**Nhược điểm:**
- ❌ ABB model không được tận dụng triệt để
- ❌ Culture check quá đơn giản (chỉ 3 mức)
- ❌ Không có role-based expectations
- ❌ Fit Score không phản ánh behavioral competency

**Phù hợp khi:** FNX chỉ tuyển tech roles, culture là yếu tố phụ.

---

## Option B: "Dual Track" — Hai luồng đánh giá song song
### Building 21 cho Technical, ABB 5 Competencies cho Behavioral — VẪN TÁCH BIỆT

```
┌──────────────────────────────────────────────────────────┐
│              FNX ASSESSMENT REPORT                       │
│                                                          │
│  ┌────────────────────┐  ┌────────────────────────────┐  │
│  │  TRACK 1: TECHNICAL│  │  TRACK 2: BEHAVIORAL       │  │
│  │  (Building 21)     │  │  (ABB Competency Model)    │  │
│  ├────────────────────┤  ├────────────────────────────┤  │
│  │                    │  │                            │  │
│  │  Mindset    ■■■■□  │  │  Safety & Integrity ■■■□□ │  │
│  │  Skills     ■■■■■  │  │  Customer Focus     ■■■■□ │  │
│  │  Knowledge  ■■■□□  │  │  Innovation & Speed ■■■■■ │  │
│  │                    │  │  Ownership & Perf.  ■■■■□ │  │
│  │  Score: 4.0/5      │  │  Collaboration      ■■■□□ │  │
│  │                    │  │                            │  │
│  │                    │  │  Score: 3.8/5              │  │
│  └────────────────────┘  └────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────────┐│
│  │  COMPOSITE FIT SCORE                                ││
│  │  = Technical (60%) + Behavioral (40%) = 3.92/5      ││
│  │                                                     ││
│  │  ⚡ Role-based: Individual Contributor               ││
│  │  📊 Radar: [2 separate charts]                      ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

**Cách hoạt động:**
- **Track 1** (Building 21): Đánh giá Mindset/Skills/Knowledge → Technical Score
- **Track 2** (ABB 5 Competencies): Đánh giá 5 hành vi → Behavioral Score
- **Composite**: Weighted average (trọng số tùy chỉnh theo JD)
- ABB role-level tự động detect từ years of experience

**Trọng số tùy loại vị trí:**
| Loại vị trí | Technical (B21) | Behavioral (ABB) |
|------------|-----------------|-------------------|
| Junior Dev / Fresh grad | 70% | 30% |
| Mid-level / Specialist | 55% | 45% |
| Senior / Team Lead | 40% | 60% |
| Manager / Director | 25% | 75% |

**Thay đổi code:**
| Component | Thay đổi |
|-----------|---------|
| `framework_definition.md` | Thêm ABB 5 Competencies với rubric 1-5 |
| `assessment_agent.py` | Thêm `assess_behavioral()` method chạy song song |
| `jd_decoder_agent.py` | Decode thêm behavioral requirements từ JD |
| `matching_agent.py` | Matching 2 tracks, weighted composite |
| Dashboard | 2 radar charts cạnh nhau |
| `survey_prompts.py` | Thêm survey type "behavioral_assessment" |

**Ưu điểm:**
- ✅ Mỗi framework giữ nguyên tính toàn vẹn riêng
- ✅ Dễ giải thích cho stakeholder ("Technical vs Behavioral")
- ✅ Trọng số linh hoạt theo vị trí
- ✅ Có thể dùng Building 21 alone hoặc ABB alone khi cần
- ✅ Phù hợp cả tech và non-tech roles

**Nhược điểm:**
- ❌ Một số competencies bị overlap (VD: "Habits of Success" ≈ "Ownership")
- ❌ Đánh giá 2 lần → prompt dài hơn, tốn API cost hơn
- ❌ Candidate phải làm 2 phần → có thể quá tải
- ❌ Culture/Values (4C) không được tích hợp

**Phù hợp khi:** FNX cần assessment rõ ràng cho cả junior lẫn senior, muốn đo riêng từng chiều.

---

## Option C: "Three Pillars" — Ba trụ cột đầy đủ
### Building 21 (Technical) + ABB 2016 (Behavioral) + ABB 4C (Culture)

```
┌───────────────────────────────────────────────────────────────────────┐
│                    FNX ASSESSMENT REPORT v3                           │
│                                                                       │
│  ┌─────────────┐  ┌──────────────────┐  ┌──────────────────────────┐ │
│  │ 🔧 PILLAR 1 │  │ 💼 PILLAR 2      │  │ 🌱 PILLAR 3              │ │
│  │  TECHNICAL   │  │  BEHAVIORAL      │  │  CULTURE & VALUES        │ │
│  │ (Building 21)│  │  (ABB 2016)      │  │  (ABB 4C + Integrity)   │ │
│  ├─────────────┤  ├──────────────────┤  ├──────────────────────────┤ │
│  │ Mindset  4.2│  │ Safety       3.5 │  │ Courage        4.0      │ │
│  │ Skills   4.5│  │ Customer     4.0 │  │ Care           3.8      │ │
│  │ Knowledge3.8│  │ Innovation   4.2 │  │ Curiosity      4.5      │ │
│  │             │  │ Ownership    3.8 │  │ Collaboration  3.5      │ │
│  │             │  │ Collaboration4.0 │  │                          │ │
│  ├─────────────┤  ├──────────────────┤  ├──────────────────────────┤ │
│  │ Avg: 4.17   │  │ Avg: 3.90       │  │ Avg: 3.95               │ │
│  │ Weight: 40% │  │ Weight: 35%     │  │ Weight: 25%             │ │
│  └─────────────┘  └──────────────────┘  └──────────────────────────┘ │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐│
│  │  COMPOSITE FIT = 4.17×0.40 + 3.90×0.35 + 3.95×0.25 = 4.02/5    ││
│  │  Role Level: Team Leader / Specialist                            ││
│  │  Culture Alignment: ✅ Strong (3.95/5)                           ││
│  │  📊 3 Radar Charts | 🏅 12 competencies total                   ││
│  └───────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────────────┘
```

**Cách hoạt động:**
- **Pillar 1**: Building 21 (3 areas × skills) = Technical Profile
- **Pillar 2**: ABB 5 Competencies = Professional Behavior Profile
- **Pillar 3**: ABB 4C Values = Culture Alignment Score
- **Composite**: 3-way weighted (40/35/25 default, adjustable)
- Role-level detection + culture fit flag

**Thay đổi code:**
| Component | Thay đổi | Effort |
|-----------|---------|--------|
| `framework_definition.md` | Viết lại hoàn toàn — 3 pillars | 🔵 Medium |
| `assessment_agent.py` | Thêm 2 methods + prompt mới | 🔴 High |
| `assessment_prompts.py` (mới) | Prompt riêng cho behavioral + culture | 🔵 Medium |
| `jd_decoder_agent.py` | Decode 3 dimensions từ JD | 🔵 Medium |
| `matching_agent.py` | 3-dimensional matching algorithm | 🔴 High |
| `survey_prompts.py` | 2 survey types mới (behavioral, culture) | 🟢 Low |
| Dashboard | 3 radar charts, role badge, culture bar | 🔴 High |

**Ưu điểm:**
- ✅ Bao quát nhất — đánh giá 360° toàn diện
- ✅ Tách biệt rõ Technical / Behavioral / Culture
- ✅ Phù hợp mọi loại vị trí và cấp bậc
- ✅ Culture fit riêng biệt — rất giá trị cho matching
- ✅ Tận dụng tối đa cả 3 tài liệu ABB
- ✅ Output chuyên nghiệp, thuyết phục stakeholder

**Nhược điểm:**
- ❌ Phức tạp nhất — cần 2-3 tuần triển khai
- ❌ 12 competencies tổng → prompt lớn, cost cao
- ❌ Assessment quá sâu cho entry-level candidates
- ❌ Overlap giữa Pillar 2 "Collaboration & Trust" và Pillar 3 "Collaboration"
- ❌ Khó maintain 3 scoring systems song song
- ❌ Có thể over-engineer cho nhu cầu hiện tại

**Phù hợp khi:** FNX phục vụ enterprise clients cần assessment toàn diện, multi-level positions.

---

## Option D: "Unified Matrix" — Ma trận hợp nhất
### Merge Building 21 + ABB thành 1 framework duy nhất, loại bỏ overlap

```
┌────────────────────────────────────────────────────────────────┐
│              FNX UNIFIED COMPETENCY MATRIX                     │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DIMENSION 1: THINKING (Tư duy)                         │  │
│  │  ├── B21: Mindset (HOS) + ABB: Innovation & Speed       │  │
│  │  ├── Tự quản lý, thiết lập mục tiêu                     │  │
│  │  ├── Sáng tạo, tư duy "what if"                         │  │
│  │  └── Score: 4.0/5                                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  DIMENSION 2: EXECUTING (Thực thi)                       │  │
│  │  ├── B21: Skills (WF) + ABB: Ownership & Performance    │  │
│  │  ├── Kỹ năng nghề, problem solving                       │  │
│  │  ├── Chịu trách nhiệm, chủ động deliver                 │  │
│  │  └── Score: 4.3/5                                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  DIMENSION 3: RELATING (Kết nối)                         │  │
│  │  ├── B21: ELA + ABB: Collaboration & Trust + Customer    │  │
│  │  ├── Giao tiếp, viết, trình bày                          │  │
│  │  ├── Tin tưởng, làm việc nhóm, customer focus            │  │
│  │  └── Score: 3.8/5                                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  DIMENSION 4: GROWING (Phát triển)                       │  │
│  │  ├── B21: PD + Knowledge + ABB 4C: Curiosity + Courage  │  │
│  │  ├── Học tập liên tục, kiến thức chuyên ngành            │  │
│  │  ├── Tò mò, dám thử, dám thất bại                       │  │
│  │  └── Score: 4.1/5                                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  DIMENSION 5: LEADING (Dẫn dắt)                          │  │
│  │  ├── ABB: Safety & Integrity + 4C: Care + Collaboration │  │
│  │  ├── Đạo đức, quan tâm đồng nghiệp                      │  │
│  │  ├── Role modeling, mentoring                             │  │
│  │  └── Score: 3.5/5                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  Composite = Average of 5 Dimensions = 3.94/5                 │
│  Role Level: Proficient (Level 3)                              │
│  📊 1 Radar Chart (5 cánh) — clean & simple                   │
└────────────────────────────────────────────────────────────────┘
```

**Ma trận ánh xạ chi tiết:**

| FNX Dimension | Từ Building 21 | Từ ABB | Merge Logic |
|---------------|---------------|--------|-------------|
| **THINKING** 🧠 | HOS (Habits of Success) | Innovation & Speed, Curiosity | Tư duy hệ thống + sáng tạo |
| **EXECUTING** ⚡ | WF (Workforce Skills) | Ownership & Performance | Làm được + chịu trách nhiệm |
| **RELATING** 🤝 | ELA (Communication) | Customer Focus, Collaboration & Trust, Collab (4C) | Giao tiếp + kết nối |
| **GROWING** 🌱 | PD + SCI/MATH/SS (Knowledge) | Curiosity, Courage | Kiến thức + ham học + dám thử |
| **LEADING** 👑 | (không có) | Safety & Integrity, Care | Đạo đức + quan tâm + dẫn dắt |

**Level expectations per dimension:**

| Level | THINKING | EXECUTING | RELATING | GROWING | LEADING |
|-------|----------|-----------|----------|---------|---------|
| 1 Foundational | Làm theo hướng dẫn | Hoàn thành task cơ bản | Giao tiếp 1-1 | Đang học | Tuân thủ rules |
| 2 Developing | Đặt câu hỏi "why" | Tự giải quyết simple tasks | Làm việc nhóm nhỏ | Tự học thêm | Giúp đỡ peer |
| 3 Proficient | Đề xuất giải pháp | Deliver độc lập, đúng hạn | Cross-team collab | Chia sẻ kiến thức | Coach đồng nghiệp |
| 4 Advanced | Tư duy hệ thống | Lead projects phức tạp | Stakeholder mgmt | Mentor người khác | Lead by example |
| 5 Mastery | Định hướng chiến lược | Drive org outcomes | Build culture | Tạo learning org | Thought leader |

**Thay đổi code:**
| Component | Thay đổi | Effort |
|-----------|---------|--------|
| `framework_definition.md` | Viết lại — 5 dimensions mới | 🔵 Medium |
| `assessment_agent.py` | 1 prompt thống nhất, 5 scores | 🟢 Low-Med |
| `jd_decoder_agent.py` | Decode 5 dimensions từ JD | 🟢 Low-Med |
| `matching_agent.py` | 5-dimensional matching | 🟢 Low |
| Dashboard | 1 radar chart (5 cánh) | 🟢 Low |

**Ưu điểm:**
- ✅ Elegant — 1 framework duy nhất, không trùng lặp
- ✅ Dễ hiểu: 5 dimensions, 5 cánh radar chart
- ✅ Prompt gọn — 1 lần đánh giá cho tất cả
- ✅ Cost thấp (ít API calls)
- ✅ "LEADING" dimension — lần đầu FNX có đo leadership
- ✅ Scalable: dễ thêm competencies vào dimension có sẵn
- ✅ Unique — đây là framework RIÊNG của FNX, không copy

**Nhược điểm:**
- ❌ Mất tính nguyên bản của cả Building 21 lẫn ABB
- ❌ Khó reference ngược lại "đây là tiêu chí nào của ABB?"
- ❌ Cần thời gian thiết kế rubric mới cho mỗi dimension
- ❌ Không thể tắt/bật từng framework riêng

**Phù hợp khi:** FNX muốn xây dựng thương hiệu đánh giá RIÊNG, không bị ràng buộc vào framework nào.

---

## Option E: "Configurable Layers" — Lớp tùy chọn theo client
### Framework cơ bản (Building 21) + Các "layer" ABB bật tắt theo nhu cầu client

```
┌────────────────────────────────────────────────────────────────┐
│              FNX CONFIGURABLE ASSESSMENT                       │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  BASE LAYER: Building 21 (Always ON)                    │  │
│  │  Mindset | Skills | Knowledge                            │  │
│  │  Score: 4.0/5                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────┐  Config per client:  │
│  │  LAYER 2: ABB Behavioral   [ON/OFF] │  ☑ FPT Software     │
│  │  5 Competencies, role-based          │  ☑ VNG Corporation  │
│  │  Score: 3.8/5                        │  ☐ Startup X        │
│  └──────────────────────────────────────┘                      │
│                                                                │
│  ┌──────────────────────────────────────┐                      │
│  │  LAYER 3: ABB Culture 4C   [ON/OFF] │  ☐ FPT Software     │
│  │  Courage/Care/Curiosity/Collab       │  ☑ VNG Corporation  │
│  │  Score: 4.1/5                        │  ☑ Startup X        │
│  └──────────────────────────────────────┘                      │
│                                                                │
│  ┌──────────────────────────────────────┐                      │
│  │  LAYER 4: Custom (Future)  [ON/OFF] │  Client-specific     │
│  │  Doanh nghiệp tự định nghĩa tiêu chí │  competency model  │
│  └──────────────────────────────────────┘                      │
│                                                                │
│  Fit Score = Weighted avg of ACTIVE layers only                │
└────────────────────────────────────────────────────────────────┘
```

**Cách hoạt động:**
- **Base Layer** (Building 21): Luôn bật — đây là nền tảng
- **Layer 2** (ABB Behavioral): Bật khi client cần đánh giá behavioral
- **Layer 3** (ABB Culture 4C): Bật khi client cần culture fit
- **Layer 4** (Custom): Cho phép doanh nghiệp thêm tiêu chí riêng
- Fit Score chỉ tính trên các layers đang bật

**Config mẫu:**
```json
{
  "client": "FPT Software",
  "layers": {
    "building_21": { "enabled": true, "weight": 0.50 },
    "abb_behavioral": { "enabled": true, "weight": 0.50 },
    "abb_culture": { "enabled": false },
    "custom": { "enabled": false }
  }
}
```

**Thay đổi code:**
| Component | Thay đổi | Effort |
|-----------|---------|--------|
| `framework_definition.md` | Chia thành layers, mỗi layer 1 file | 🔵 Medium |
| `assessment_agent.py` | Accept config, run active layers only | 🔴 High |
| `jd_decoder_agent.py` | Decode theo active layers | 🔵 Medium |
| `matching_agent.py` | Dynamic weighted matching | 🔴 High |
| Config system (mới) | Client config management | 🔴 High |
| Dashboard | Dynamic radar (cánh thay đổi theo config) | 🔴 High |

**Ưu điểm:**
- ✅ Linh hoạt tối đa — mỗi client một cấu hình
- ✅ "Sell" được: package Basic (B21 only) → Pro (+ ABB) → Enterprise (+ Custom)
- ✅ Backward compatible — hệ thống hiện tại = Base Layer only
- ✅ Mở rộng được: future framework nào cũng thêm vào như 1 layer
- ✅ Pay-per-layer model (cho commercial)

**Nhược điểm:**
- ❌ Phức tạp nhất — cần architecture vững, 3-4 tuần dev
- ❌ Testing matrix lớn (mỗi tổ hợp layer cần test)
- ❌ Config management overhead
- ❌ UX phức tạp hơn cho end user
- ❌ Over-engineer cho giai đoạn hiện tại

**Phù hợp khi:** FNX hướng tới SaaS product phục vụ nhiều doanh nghiệp khác nhau.

---

## So sánh tổng quan

| Tiêu chí | Option A | Option B | Option C | Option D | Option E |
|----------|----------|----------|----------|----------|----------|
| **Tên** | Add-on | Dual Track | Three Pillars | Unified Matrix | Config Layers |
| **Độ phức tạp** | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Effort (ngày)** | 1-2 | 5-7 | 14-21 | 7-10 | 21-30 |
| **Tận dụng ABB** | 20% | 60% | 100% | 80% | 90% |
| **Giữ B21 nguyên** | ✅ 100% | ✅ 100% | ✅ 100% | ❌ Merged | ✅ 100% |
| **Overlap** | Không | Có ít | Có | Không | Không |
| **Fit Score** | B21 only | 2 tracks | 3 pillars | 5 dimensions | Dynamic |
| **Radar charts** | 1 + badge | 2 | 3 | 1 (5 cánh) | Dynamic |
| **Suitable for** | Tech only | Tech + Mid mgmt | All levels | All levels | Multi-client |
| **Risk** | Rất thấp | Thấp | Trung bình | Trung bình | Cao |
| **Scalability** | Thấp | Trung bình | Trung bình | Cao | Rất cao |
| **Brand identity** | B21 | B21 + ABB | B21 + ABB | FNX Own | FNX Platform |

---

## Khuyến nghị của tôi

### 🏆 Nếu chọn 1 option duy nhất → **Option D (Unified Matrix)**

Lý do:
- Tạo **thương hiệu FNX riêng** (THINKING/EXECUTING/RELATING/GROWING/LEADING)
- **1 radar chart 5 cánh** — clean, dễ hiểu cho mọi stakeholder
- Tận dụng tốt cả ABB lẫn Building 21 mà không overlap
- Effort hợp lý (7-10 ngày)
- Có dimension LEADING — differentiator so với các tool khác

### 🔄 Nếu muốn tiếp cận dần → **Option B trước → Option D sau**

- Sprint 1: Implement Option B (Dual Track) — 5-7 ngày
- Validate với 5-10 candidates thật
- Sprint 2: Nếu thấy overlap nhiều → consolidate thành Option D
- Lợi thế: học được từ data thật trước khi merge

### 🚀 Nếu hướng tới product/SaaS → **Option D + phần config từ Option E**

- Core framework = Option D (Unified Matrix)
- Thêm weight customization per client (từ E)
- Không cần full layer system, chỉ cần adjustable weights

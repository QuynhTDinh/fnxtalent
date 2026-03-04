/**
 * FNX Assessment Dashboard — Application Logic
 * 
 * Handles:
 * - Loading assessment data (from pipeline or demo)
 * - Rendering radar chart, domain bars, gap analysis
 * - Populating competency evidence table
 */

// ── Initialize ──
const radar = new RadarChart('radarCanvas');

// Set current date
document.getElementById('reportDate').textContent =
    new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });

// ── Area Names Lookup (Building 21 → Vietnamese) ──
const AREA_NAMES = {
    'HOS': { short: 'Tư duy', full: 'Habits of Success — Thói quen thành công', group: 'Mindset' },
    'PD': { short: 'Phát triển', full: 'Personal Development — Phát triển cá nhân', group: 'Mindset' },
    'WF': { short: 'Kỹ năng nghề', full: 'Workforce Readiness — Kỹ năng nghề nghiệp', group: 'Skills' },
    'ELA': { short: 'Giao tiếp', full: 'English Language Arts — Ngôn ngữ & Giao tiếp', group: 'Skills' },
    'SCI': { short: 'Khoa học KT', full: 'Science — Khoa học & Kỹ thuật', group: 'Knowledge' },
    'MATH': { short: 'Phân tích', full: 'Mathematics — Toán & Phân tích', group: 'Knowledge' },
    'SS': { short: 'Xã hội', full: 'Social Studies — Khoa học xã hội', group: 'Knowledge' },
};

const LEVEL_NAMES = {
    1: 'Nền tảng',
    2: 'Đang phát triển',
    3: 'Thành thạo',
    4: 'Nâng cao',
    5: 'Bậc thầy',
};

function getAreaLabel(code) {
    const area = code?.split('.')[0];
    return AREA_NAMES[area] || { short: area, full: area, group: '?' };
}

// ── Legend toggle ──
function toggleLegend() {
    const content = document.getElementById('legendContent');
    const toggle = document.getElementById('legendToggle');
    content.classList.toggle('collapsed');
    toggle.textContent = content.classList.contains('collapsed') ? 'Mở rộng ▼' : 'Thu gọn ▲';
}

// ── Demo Data (from actual Gemini LLM pipeline run) ──
const DEMO_ASSESSMENT = {
    candidateId: "cand_001",
    fullName: "Nguyễn Văn A",
    competencies: [
        {
            area: "WF",
            code: "WF.1",
            name: "Quản lý dự án",
            level: 3,
            evidence: "Quản lý dây chuyền sản xuất nhựa PP",
            reasoning: "Quản lý một dây chuyền sản xuất cho thấy khả năng quản lý dự án ở mức độ thành thạo."
        },
        {
            area: "SCI",
            code: "SCI.2",
            name: "Ứng dụng KHKT",
            level: 4,
            evidence: "Xây dựng hệ thống giám sát an toàn tự động",
            reasoning: "Xây dựng một hệ thống tự động đòi hỏi kiến thức chuyên sâu và khả năng ứng dụng KHKT ở mức cao."
        },
        {
            area: "SCI",
            code: "SCI.3",
            name: "Giải quyết vấn đề KT",
            level: 4,
            evidence: "Thiết kế các giải pháp xử lý nước thải công nghiệp",
            reasoning: "Thiết kế giải pháp cho thấy khả năng giải quyết vấn đề kỹ thuật phức tạp."
        },
        {
            area: "HOS",
            code: "HOS.4",
            name: "Tư duy hệ thống",
            level: 4,
            evidence: "Áp dụng tư duy hệ thống để giảm 20% chi phí vận hành",
            reasoning: "Áp dụng tư duy hệ thống và đạt được kết quả giảm chi phí cho thấy khả năng ở mức cao."
        },
        {
            area: "SCI",
            code: "SCI.4",
            name: "Sáng tạo & đổi mới",
            level: 4,
            evidence: "Bằng sáng chế: Hệ thống lọc khí thải đa tầng (2022)",
            reasoning: "Sở hữu bằng sáng chế chứng tỏ khả năng sáng tạo và đổi mới ở mức cao."
        },
        {
            area: "WF",
            code: "WF.2",
            name: "Lãnh đạo nhóm",
            level: 3,
            evidence: "Điều phối đội ngũ 15 kỹ sư",
            reasoning: "Điều phối một đội ngũ kỹ sư cho thấy khả năng lãnh đạo nhóm ở mức thành thạo."
        }
    ],
    overallStrength: "Ứng viên có kinh nghiệm quản lý và điều phối dự án, tư duy hệ thống tốt và khả năng sáng tạo cao thể hiện qua bằng sáng chế.",
    developmentAreas: "Để phát triển hơn nữa, ứng viên có thể tập trung vào việc nâng cao kỹ năng giao tiếp và thuyết trình."
};

const DEMO_JD_RESULT = {
    job_id: "job_001",
    role: "Trưởng phòng Kỹ thuật Hóa dầu",
    required_competencies: [
        { area: "WF", code: "WF.1", name: "Quản lý dự án và nguồn lực", target_level: 4, priority: "High" },
        { area: "SCI", code: "SCI.3", name: "Ứng dụng kiến thức chuyên ngành", target_level: 4, priority: "High" },
        { area: "HOS", code: "HOS.4", name: "Giải quyết vấn đề và ra quyết định", target_level: 4, priority: "High" },
        { area: "SCI", code: "SCI.5", name: "Tuân thủ quy định và tiêu chuẩn", target_level: 3, priority: "Medium" },
        { area: "ELA", code: "ELA.1", name: "Giao tiếp hiệu quả", target_level: 3, priority: "Medium" },
        { area: "WF", code: "WF.3", name: "Quản lý chất lượng", target_level: 3, priority: "Low" },
    ]
};

const DEMO_MATCH = {
    fitScore: 61.1,
    gaps: [
        { code: "WF.1", target: 4, actual: 3, gap: 1, priority: "High" },
        { code: "SCI.5", target: 3, actual: 0, gap: 3, priority: "Medium" },
        { code: "ELA.1", target: 3, actual: 0, gap: 3, priority: "Medium" },
        { code: "WF.3", target: 3, actual: 0, gap: 3, priority: "Low" },
    ]
};

const DEMO_CANDIDATE = {
    id: "cand_001",
    fullName: "Nguyễn Văn A",
    yearbook_info: { major: "Kỹ thuật Hóa học", graduation_year: 2015 }
};

// ── Rendering Functions ──

function renderDashboard(assessment, jdResult, matchResult, candidateInfo) {
    renderCandidateInfo(candidateInfo, assessment);
    renderRadarChart(assessment, jdResult);
    renderDomainBars(assessment);
    renderCompetencyTable(assessment);
    renderGapAnalysis(matchResult);
    renderFitScore(matchResult.fitScore);
}

function renderCandidateInfo(candidate, assessment) {
    document.getElementById('candidateId').textContent = candidate.id;
    document.getElementById('candidateName').textContent = candidate.fullName;
    document.getElementById('candidateMajor').textContent =
        `${candidate.yearbook_info?.major || 'N/A'} · ${candidate.yearbook_info?.graduation_year || ''}`;

    // Avatar initials
    const initials = candidate.fullName.split(' ').map(w => w[0]).join('').slice(-3);
    document.getElementById('candidateAvatar').querySelector('span').textContent = initials;

    // Summary
    document.getElementById('overallStrength').textContent = assessment.overallStrength || '—';
    document.getElementById('developmentAreas').textContent = assessment.developmentAreas || '—';
}

function renderRadarChart(assessment, jdResult) {
    // Build unified axis list from all competencies mentioned in either assessment or JD
    const codeMap = new Map();

    // Add assessment competencies
    assessment.competencies.forEach(c => {
        codeMap.set(c.code, { code: c.code, name: c.name, area: c.area, actual: c.level, target: 0 });
    });

    // Add/merge JD requirements
    jdResult.required_competencies.forEach(c => {
        if (codeMap.has(c.code)) {
            codeMap.get(c.code).target = c.target_level;
        } else {
            codeMap.set(c.code, { code: c.code, name: c.name, area: c.area, actual: 0, target: c.target_level });
        }
    });

    const entries = Array.from(codeMap.values());

    // Sort by area for visual grouping
    const areaOrder = { 'HOS': 0, 'PD': 1, 'WF': 2, 'ELA': 3, 'SCI': 4, 'MATH': 5, 'SS': 6 };
    entries.sort((a, b) => (areaOrder[a.area] ?? 99) - (areaOrder[b.area] ?? 99));

    const axes = entries.map(e => ({ code: e.code, name: e.name, area: e.area }));
    const candidateValues = entries.map(e => e.actual);
    const targetValues = entries.map(e => e.target);

    radar.setData(axes, candidateValues, targetValues);
}

function renderFitScore(score) {
    const el = document.getElementById('fitScoreValue');
    // Animate count up
    const duration = 1500;
    const start = performance.now();
    const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(score * eased) + '%';
        if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);

    // Color based on score
    if (score >= 80) {
        el.style.background = 'linear-gradient(135deg, #34d399, #22d3ee)';
    } else if (score >= 60) {
        el.style.background = 'linear-gradient(135deg, #6366f1, #22d3ee)';
    } else {
        el.style.background = 'linear-gradient(135deg, #fb7185, #fbbf24)';
    }
    el.style.webkitBackgroundClip = 'text';
    el.style.webkitTextFillColor = 'transparent';
    el.style.backgroundClip = 'text';
}

function renderDomainBars(assessment) {
    const domains = {
        'Mindset': { areas: ['HOS', 'PD'], color: 'var(--domain-mindset)', icon: '#a78bfa', items: [] },
        'Skills': { areas: ['WF', 'ELA'], color: 'var(--domain-skills)', icon: '#22d3ee', items: [] },
        'Knowledge': { areas: ['SCI', 'MATH', 'SS'], color: 'var(--domain-knowledge)', icon: '#34d399', items: [] },
    };

    assessment.competencies.forEach(c => {
        for (const [name, domain] of Object.entries(domains)) {
            if (domain.areas.includes(c.area)) {
                domain.items.push(c.level);
                break;
            }
        }
    });

    const container = document.getElementById('domainBars');
    container.innerHTML = '';

    for (const [name, domain] of Object.entries(domains)) {
        const avg = domain.items.length > 0
            ? domain.items.reduce((a, b) => a + b, 0) / domain.items.length
            : 0;
        const pct = (avg / 5) * 100;
        const areaLabels = domain.areas.join(', ');

        const el = document.createElement('div');
        el.className = 'domain-item';
        el.innerHTML = `
            <div class="domain-header">
                <div class="domain-name">
                    <span class="domain-icon" style="background: ${domain.icon}"></span>
                    <span class="domain-label">${name}</span>
                    <span class="domain-sublabel">(${areaLabels})</span>
                </div>
                <span class="domain-score" style="color: ${domain.icon}">${avg.toFixed(1)} / 5</span>
            </div>
            <div class="domain-bar-track">
                <div class="domain-bar-fill" style="background: linear-gradient(90deg, ${domain.icon}, ${domain.icon}88)" data-width="${pct}"></div>
            </div>
        `;
        container.appendChild(el);
    }

    // Animate bars
    requestAnimationFrame(() => {
        setTimeout(() => {
            container.querySelectorAll('.domain-bar-fill').forEach(bar => {
                bar.style.width = bar.dataset.width + '%';
            });
        }, 200);
    });
}

function renderCompetencyTable(assessment) {
    const tbody = document.getElementById('competencyTableBody');
    tbody.innerHTML = '';

    assessment.competencies.forEach((c, i) => {
        const tr = document.createElement('tr');
        tr.style.animationDelay = `${i * 0.05}s`;
        const areaInfo = getAreaLabel(c.code);
        const levelName = LEVEL_NAMES[c.level] || '';
        tr.innerHTML = `
            <td>
                <span class="competency-code">${c.code}</span>
                <span class="area-tag">${areaInfo.short}</span>
            </td>
            <td><span class="competency-name-cell">${c.name}</span></td>
            <td>
                <span class="level-badge level-${c.level}">${c.level}</span>
                <span class="level-name">${levelName}</span>
            </td>
            <td>
                <div class="evidence-text">${c.evidence}</div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderGapAnalysis(matchResult) {
    const container = document.getElementById('gapList');
    const countEl = document.getElementById('gapCount');
    const gaps = matchResult.gaps || [];

    countEl.textContent = `${gaps.length} khoảng cách`;
    container.innerHTML = '';

    if (gaps.length === 0) {
        container.innerHTML = '<div class="no-gap-message">✨ Không phát hiện khoảng cách năng lực. Ứng viên phù hợp hoàn toàn!</div>';
        return;
    }

    // Priority labels in Vietnamese
    const priorityLabels = { 'High': 'Cao', 'Medium': 'TB', 'Low': 'Thấp' };

    gaps.forEach((gap, i) => {
        const actualPct = (gap.actual / 5) * 100;
        const targetPct = (gap.target / 5) * 100;
        const areaInfo = getAreaLabel(gap.code);
        const gapName = gap.name || gap.code;
        const priLabel = priorityLabels[gap.priority] || gap.priority;

        const el = document.createElement('div');
        el.className = 'gap-item';
        el.style.animationDelay = `${i * 0.08}s`;
        el.innerHTML = `
            <div class="gap-item-info">
                <span class="gap-item-code">${gap.code}</span>
                <span class="gap-item-name">${gapName}</span>
            </div>
            <div class="gap-bar-container">
                <div class="gap-bar-labels">
                    <span class="gap-actual">Thực tế: ${gap.actual}</span>
                    <span class="gap-target">Yêu cầu: ${gap.target}</span>
                </div>
                <div class="gap-bar-track">
                    <div class="gap-bar-actual" data-width="${actualPct}"></div>
                    <div class="gap-bar-target-line" data-left="${targetPct}"></div>
                </div>
            </div>
            <span class="gap-priority priority-${gap.priority}">${priLabel}</span>
        `;
        container.appendChild(el);
    });

    // Animate gap bars
    requestAnimationFrame(() => {
        setTimeout(() => {
            container.querySelectorAll('.gap-bar-actual').forEach(bar => {
                bar.style.width = bar.dataset.width + '%';
            });
            container.querySelectorAll('.gap-bar-target-line').forEach(line => {
                line.style.left = line.dataset.left + '%';
            });
        }, 400);
    });
}

// ── Actions ──

function loadDemoData() {
    renderDashboard(DEMO_ASSESSMENT, DEMO_JD_RESULT, DEMO_MATCH, DEMO_CANDIDATE);
}

const API_BASE = 'http://localhost:8000';

const PIPELINE_CANDIDATE = {
    id: "cand_001",
    fullName: "Nguyễn Văn A",
    yearbook_info: { major: "Kỹ thuật Hóa học", graduation_year: 2015, class: "CH10A" },
    experience: [
        {
            title: "Kỹ sư quy trình",
            company: "PetroVietnam",
            duration: "2015-2020",
            description: "Quản lý dây chuyền sản xuất nhựa PP, tối ưu hóa quy trình nhiệt và áp suất. Xây dựng hệ thống giám sát an toàn tự động."
        },
        {
            title: "Trưởng phòng kỹ thuật",
            company: "Chemical Corp X",
            duration: "2020-Present",
            description: "Điều phối đội ngũ 15 kỹ sư, thiết kế các giải pháp xử lý nước thải công nghiệp. Áp dụng tư duy hệ thống để giảm 20% chi phí vận hành."
        }
    ],
    social_data: {
        linkedin_url: "linkedin.com/in/nguyen-van-a",
        patents: ["Hệ thống lọc khí thải đa tầng (2022)"]
    }
};

const PIPELINE_JOB = {
    id: "job_001",
    title: "Trưởng phòng Kỹ thuật Hóa dầu",
    company: "PetroVietnam Gas",
    industry: "Dầu khí",
    seniority: "Senior",
    content: `Mô tả công việc:
- Quản lý và điều phối đội ngũ 20 kỹ sư quy trình tại nhà máy lọc dầu.
- Thiết kế, tối ưu hóa các quy trình chế biến hydrocarbon, cracking xúc tác.
- Phân tích dữ liệu vận hành hệ thống, đề xuất giải pháp nâng cao hiệu suất.
- Đảm bảo tuân thủ các tiêu chuẩn an toàn môi trường ISO 14001.

Yêu cầu:
- Tốt nghiệp Đại học ngành Kỹ thuật Hóa học, Hóa dầu hoặc tương đương.
- Tối thiểu 8 năm kinh nghiệm trong ngành lọc hóa dầu.
- Có kinh nghiệm quản lý đội nhóm từ 10 người trở lên.
- Tư duy hệ thống, khả năng ra quyết định trong môi trường áp lực cao.
- Tiếng Anh giao tiếp tốt (IELTS 6.0+).
- Ưu tiên ứng viên có chứng chỉ PMP hoặc Six Sigma.`
};

async function runFullPipeline() {
    const btn = document.getElementById('runAssessmentBtn');
    btn.classList.add('loading');
    btn.textContent = 'Running DAG Pipeline...';

    try {
        const response = await fetch(`${API_BASE}/api/pipeline/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidate: PIPELINE_CANDIDATE,
                job: PIPELINE_JOB,
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Pipeline result:', data);

        // Extract results from DAG output
        const assessResult = data.results?.assess || DEMO_ASSESSMENT;
        const decodeResult = data.results?.decode || DEMO_JD_RESULT;
        const matchResult = data.results?.match || DEMO_MATCH;

        renderDashboard(assessResult, decodeResult, matchResult, PIPELINE_CANDIDATE);

    } catch (err) {
        console.error('Pipeline error:', err);
        alert(`Pipeline error: ${err.message}\n\nFalling back to demo data.`);
        loadDemoData();
    } finally {
        btn.classList.remove('loading');
        btn.innerHTML = `
            <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
            </svg>
            Run Full Pipeline
        `;
    }
}

// ── Auto-load demo on page load ──
window.addEventListener('DOMContentLoaded', () => {
    // Slight delay to let CSS animations settle
    setTimeout(loadDemoData, 300);
});

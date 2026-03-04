/**
 * FNX Wizard — 4-Step Assessment Flow
 *
 * Step 1: Input JD → call /api/jd/decode
 * Step 2: Input CV → call /api/cv/assess
 * Step 3: Run matching → call /api/pipeline/run
 * Step 4: Render report (radar, gaps, table)
 */

// ── State ──
let currentStep = 1;
let jdData = null;   // decoded JD result
let cvData = null;   // assessed CV result
let matchData = null; // matching result
let radar = null;

const API_BASE = '';

const AREA_INFO = {
    'HOS': { short: 'Tư duy', full: 'Habits of Success', group: 'Mindset' },
    'PD': { short: 'Phát triển', full: 'Personal Development', group: 'Mindset' },
    'WF': { short: 'Kỹ năng nghề', full: 'Workforce Readiness', group: 'Skills' },
    'ELA': { short: 'Ngôn ngữ', full: 'English Language Arts', group: 'Skills' },
    'SCI': { short: 'Khoa học KT', full: 'Science', group: 'Knowledge' },
    'MATH': { short: 'Toán học', full: 'Mathematics', group: 'Knowledge' },
    'SS': { short: 'Xã hội', full: 'Social Studies', group: 'Knowledge' },
};

const LEVEL_NAMES = {
    1: 'Nền tảng',
    2: 'Đang phát triển',
    3: 'Thành thạo',
    4: 'Nâng cao',
    5: 'Bậc thầy',
};

// ── Step Navigation ──

function goToStep(step) {
    // Validate before advancing
    if (step > currentStep) {
        if (currentStep === 1 && !validateStep1()) return;
        if (currentStep === 2 && !validateStep2()) return;
    }

    // Update stepper visual
    document.querySelectorAll('.step').forEach((el, i) => {
        el.classList.remove('active', 'done');
        if (i + 1 < step) el.classList.add('done');
        if (i + 1 === step) el.classList.add('active');
    });

    // Update panels
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    const target = document.getElementById(`panel-${step}`);
    if (target) target.classList.add('active');

    currentStep = step;

    // Update nav buttons
    document.getElementById('btnBack').style.visibility = step === 1 ? 'hidden' : 'visible';
    document.getElementById('stepIndicator').textContent = `Bước ${step} / 4`;

    const btnNext = document.getElementById('btnNext');
    if (step === 3) {
        btnNext.style.display = 'none';
        runMatching();
    } else if (step === 4) {
        btnNext.textContent = '🔄 Đánh giá mới';
        btnNext.style.display = '';
    } else {
        btnNext.textContent = 'Tiếp tục →';
        btnNext.style.display = '';
    }
}

function goNext() {
    if (currentStep === 4) {
        resetWizard();
        return;
    }
    goToStep(currentStep + 1);
}

function goBack() {
    if (currentStep > 1) goToStep(currentStep - 1);
}

function validateStep1() {
    const role = document.getElementById('jdRole').value.trim();
    const content = document.getElementById('jdContent').value.trim();
    if (!role || !content) {
        alert('Vui lòng nhập tên vị trí và nội dung JD.');
        return false;
    }
    // If JD not yet analyzed, analyze first
    if (!jdData) {
        analyzeJD();
        return false; // Will auto-advance after analysis
    }
    return true;
}

function validateStep2() {
    const name = document.getElementById('cvName').value.trim();
    const content = document.getElementById('cvContent').value.trim();
    if (!name || !content) {
        alert('Vui lòng nhập họ tên và nội dung CV.');
        return false;
    }
    if (!cvData) {
        analyzeCV();
        return false;
    }
    return true;
}

function resetWizard() {
    currentStep = 1;
    jdData = null;
    cvData = null;
    matchData = null;
    document.getElementById('jdRole').value = '';
    document.getElementById('jdContent').value = '';
    document.getElementById('jdCompany').value = '';
    document.getElementById('jdIndustry').value = '';
    document.getElementById('cvName').value = '';
    document.getElementById('cvContent').value = '';
    document.getElementById('cvMajor').value = '';
    document.getElementById('cvYear').value = '';
    document.getElementById('jdResult').style.display = 'none';
    document.getElementById('cvResult').style.display = 'none';
    goToStep(1);
}


// ── Step 1: Analyze JD ──

async function analyzeJD() {
    const role = document.getElementById('jdRole').value.trim();
    const content = document.getElementById('jdContent').value.trim();
    if (!role || !content) {
        alert('Vui lòng nhập tên vị trí và nội dung JD.');
        return;
    }

    const btnNext = document.getElementById('btnNext');
    btnNext.textContent = '⏳ Đang phân tích JD...';
    btnNext.disabled = true;

    try {
        const resp = await fetch(`${API_BASE}/api/jd/decode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content,
                role,
                company: document.getElementById('jdCompany').value.trim() || null,
                industry: document.getElementById('jdIndustry').value.trim() || null,
            }),
        });

        if (!resp.ok) throw new Error(`API error: ${resp.status}`);
        jdData = await resp.json();

        // Show result chips
        const comps = jdData.required_competencies || [];
        document.getElementById('jdCompCount').textContent = `${comps.length} năng lực yêu cầu`;
        document.getElementById('jdCompetencies').innerHTML = comps.map(c =>
            `<span class="comp-chip">
                <span class="chip-code">${c.code}</span>
                ${c.name || ''}
                <span class="chip-level l${c.target_level}">${c.target_level}</span>
            </span>`
        ).join('');
        document.getElementById('jdResult').style.display = '';

        btnNext.textContent = 'Tiếp tục →';
        btnNext.disabled = false;
    } catch (err) {
        console.error('JD decode error:', err);
        alert('Lỗi phân tích JD: ' + err.message);
        btnNext.textContent = 'Tiếp tục →';
        btnNext.disabled = false;
    }
}


// ── Step 2: Analyze CV ──

async function analyzeCV() {
    const name = document.getElementById('cvName').value.trim();
    const content = document.getElementById('cvContent').value.trim();
    if (!name || !content) {
        alert('Vui lòng nhập họ tên và nội dung CV.');
        return;
    }

    const btnNext = document.getElementById('btnNext');
    btnNext.textContent = '⏳ Đang đánh giá CV...';
    btnNext.disabled = true;

    try {
        const resp = await fetch(`${API_BASE}/api/cv/assess`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content,
                name,
                major: document.getElementById('cvMajor').value.trim() || null,
                graduation_year: parseInt(document.getElementById('cvYear').value) || null,
            }),
        });

        if (!resp.ok) throw new Error(`API error: ${resp.status}`);
        cvData = await resp.json();

        // Show result chips
        const comps = cvData.competencies || [];
        document.getElementById('cvCompCount').textContent = `${comps.length} năng lực phát hiện`;
        document.getElementById('cvCompetencies').innerHTML = comps.map(c =>
            `<span class="comp-chip">
                <span class="chip-code">${c.code}</span>
                ${c.name || ''}
                <span class="chip-level l${c.level}">${c.level}</span>
            </span>`
        ).join('');
        document.getElementById('cvResult').style.display = '';

        btnNext.textContent = 'Tiếp tục →';
        btnNext.disabled = false;
    } catch (err) {
        console.error('CV assess error:', err);
        alert('Lỗi đánh giá CV: ' + err.message);
        btnNext.textContent = 'Tiếp tục →';
        btnNext.disabled = false;
    }
}


// ── Step 3: Run Matching ──

async function runMatching() {
    // Update processing steps UI
    const steps = ['proc-decode', 'proc-assess', 'proc-validate', 'proc-match'];
    steps.forEach(id => {
        const el = document.getElementById(id);
        el.classList.remove('active', 'done');
        el.querySelector('.proc-icon').textContent = '⏳';
    });

    // Mark decode & assess as done (already done in steps 1-2)
    markProcDone('proc-decode');
    markProcDone('proc-assess');

    // Build pipeline request
    const candidateData = {
        id: 'wizard_cand',
        fullName: cvData.fullName || document.getElementById('cvName').value,
        yearbook_info: {
            major: document.getElementById('cvMajor').value || 'N/A',
            graduation_year: parseInt(document.getElementById('cvYear').value) || null,
        },
        experience: [{
            title: 'Toàn bộ kinh nghiệm',
            company: '',
            duration: '',
            description: document.getElementById('cvContent').value,
        }],
    };

    const jobData = {
        id: 'wizard_job',
        role: jdData.role || document.getElementById('jdRole').value,
        seniority: 'Senior',
        content: document.getElementById('jdContent').value,
    };

    // Mark validate as active
    const valEl = document.getElementById('proc-validate');
    valEl.classList.add('active');
    valEl.querySelector('.proc-icon').textContent = '🔄';

    try {
        const resp = await fetch(`${API_BASE}/api/pipeline/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate: candidateData, job: jobData }),
        });

        if (!resp.ok) throw new Error(`Pipeline error: ${resp.status}`);
        const result = await resp.json();

        markProcDone('proc-validate');
        markProcDone('proc-match');

        // Extract data from pipeline result
        const nodeResults = result.node_results || {};
        const assessResult = nodeResults.assess || cvData;
        const jdResult = nodeResults.decode || jdData;
        const matchResult = nodeResults.match || {};

        matchData = matchResult;

        // Small delay for visual effect then go to report
        setTimeout(() => {
            renderReport(assessResult, jdResult, matchResult);
            goToStep(4);
        }, 800);

    } catch (err) {
        console.error('Pipeline error:', err);
        alert('Lỗi pipeline: ' + err.message);
        goToStep(2);
    }
}

function markProcDone(id) {
    const el = document.getElementById(id);
    el.classList.remove('active');
    el.classList.add('done');
    el.querySelector('.proc-icon').textContent = '✅';
}


// ── Step 4: Render Report ──

function renderReport(assessment, jdResult, matchResult) {
    // Score
    const fitScore = matchResult.fit_score ?? matchResult.fitScore ?? 0;
    const scoreNum = document.querySelector('.score-number');
    animateNumber(scoreNum, fitScore);

    // Color score
    if (fitScore >= 80) scoreNum.style.color = '#34c759';
    else if (fitScore >= 60) scoreNum.style.color = '#0071e3';
    else scoreNum.style.color = '#ff3b30';

    // Title & meta
    document.getElementById('reportTitle').textContent =
        `${assessment.fullName || 'Ứng viên'} ↔ ${jdResult.role || 'Vị trí'}`;
    document.getElementById('reportMeta').textContent =
        `Đánh giá dựa trên khung Building 21 · ${new Date().toLocaleDateString('vi-VN')}`;

    // Tags
    const strengths = matchResult.strengths || [];
    const gaps = matchResult.gaps || [];
    document.getElementById('reportTags').innerHTML = [
        ...strengths.slice(0, 3).map(s => `<span class="score-tag tag-strength">✓ ${s.code}</span>`),
        ...gaps.slice(0, 3).map(g => `<span class="score-tag tag-gap">↓ ${g.code}</span>`),
    ].join('');

    // Candidate Profile
    renderCandidateProfile(assessment);

    // Domain Bars
    renderDomainBars(assessment);

    // Radar Chart
    renderRadarChart(assessment, jdResult);

    // Gap Analysis
    renderGapAnalysis(matchResult);

    // Competency Table
    renderCompetencyTable(assessment);
}

function renderCandidateProfile(assessment) {
    const name = assessment.fullName || document.getElementById('cvName').value || 'Ứng viên';
    const major = document.getElementById('cvMajor').value || '';
    const year = document.getElementById('cvYear').value || '';

    // Avatar initials
    const initials = name.split(' ').map(w => w[0]).filter(Boolean).slice(-2).join('').toUpperCase();
    document.getElementById('reportAvatar').textContent = initials || 'UV';

    document.getElementById('reportCandidateName').textContent = name;
    document.getElementById('reportCandidateMajor').textContent =
        [major, year].filter(Boolean).join(' · ') || '—';

    // Strength & Development
    document.getElementById('reportStrength').textContent = assessment.overallStrength || '—';
    document.getElementById('reportDevelopment').textContent = assessment.developmentAreas || '—';
}

function renderDomainBars(assessment) {
    const domains = {
        'Mindset': { areas: ['HOS', 'PD'], color: '#af52de', items: [] },
        'Skills': { areas: ['WF', 'ELA'], color: '#5ac8fa', items: [] },
        'Knowledge': { areas: ['SCI', 'MATH', 'SS'], color: '#34c759', items: [] },
    };

    (assessment.competencies || []).forEach(c => {
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
                    <span class="domain-icon" style="background: ${domain.color}"></span>
                    <span class="domain-label">${name}</span>
                    <span class="domain-sublabel">(${areaLabels})</span>
                </div>
                <span class="domain-score" style="color: ${domain.color}">${avg.toFixed(1)} / 5</span>
            </div>
            <div class="domain-bar-track">
                <div class="domain-bar-fill" style="background: linear-gradient(90deg, ${domain.color}, ${domain.color}88)" data-width="${pct}"></div>
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

function toggleLegend() {
    const content = document.getElementById('legendContent');
    const btn = document.getElementById('legendToggle');
    if (content.style.display === 'none') {
        content.style.display = '';
        btn.textContent = 'Thu gọn ▲';
    } else {
        content.style.display = 'none';
        btn.textContent = 'Mở rộng ▼';
    }
}

function animateNumber(el, target) {
    const duration = 1200;
    const start = performance.now();
    const tick = (now) => {
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        el.textContent = Math.round(target * eased);
        if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
}

function renderRadarChart(assessment, jdResult) {
    if (!radar) {
        radar = new RadarChart('radarCanvas', { width: 480, height: 480 });
    }

    const candidateComps = assessment.competencies || [];
    const jdComps = jdResult.required_competencies || [];

    // Merge into unified axes
    const codeMap = new Map();
    candidateComps.forEach(c => {
        codeMap.set(c.code, { code: c.code, name: c.name, area: c.area, actual: c.level, target: 0 });
    });
    jdComps.forEach(c => {
        if (codeMap.has(c.code)) {
            codeMap.get(c.code).target = c.target_level;
        } else {
            codeMap.set(c.code, { code: c.code, name: c.name, area: c.area, actual: 0, target: c.target_level });
        }
    });

    const entries = Array.from(codeMap.values());
    const areaOrder = { HOS: 0, PD: 1, WF: 2, ELA: 3, SCI: 4, MATH: 5, SS: 6 };
    entries.sort((a, b) => (areaOrder[a.area] ?? 99) - (areaOrder[b.area] ?? 99));

    radar.setData(
        entries.map(e => ({ code: e.code, name: e.name, area: e.area })),
        entries.map(e => e.actual),
        entries.map(e => e.target),
    );
}

function renderGapAnalysis(matchResult) {
    const gaps = matchResult.gaps || [];
    const card = document.getElementById('gapCard');
    const list = document.getElementById('gapList');

    if (gaps.length === 0) {
        card.style.display = 'none';
        return;
    }

    card.style.display = '';
    list.innerHTML = gaps.map(g => {
        const pClass = (g.priority || 'Medium').toLowerCase();
        const pLabel = { high: 'Cao', medium: 'TB', low: 'Thấp' }[pClass] || g.priority;
        return `
        <div class="gap-item">
            <span class="gap-code">${g.code}</span>
            <span class="gap-name">${g.name || ''}</span>
            <div class="gap-bar-wrap">
                <div class="gap-bar-labels">
                    <span class="gap-actual-label">Thực tế: ${g.actual ?? 0}</span>
                    <span class="gap-target-label">Yêu cầu: ${g.target ?? 0}</span>
                </div>
                <div class="gap-bar-track">
                    <div class="gap-bar-fill" style="width: ${((g.actual ?? 0) / 5) * 100}%"></div>
                    <div class="gap-bar-target" style="left: ${((g.target ?? 0) / 5) * 100}%"></div>
                </div>
            </div>
            <span class="gap-priority priority-${pClass}">${pLabel}</span>
        </div>`;
    }).join('');
}

function renderCompetencyTable(assessment) {
    const comps = assessment.competencies || [];
    const tbody = document.getElementById('compTableBody');

    tbody.innerHTML = comps.map(c => `
        <tr>
            <td>
                <span style="font-weight:600; color: var(--accent-blue); font-size: 0.72rem;">${c.code}</span>
                <br><span style="font-size: 0.58rem; color: var(--text-caption);">${AREA_INFO[c.area]?.short || c.area}</span>
            </td>
            <td style="font-weight:500; color: var(--text-primary);">${c.name || ''}</td>
            <td>
                <span class="level-badge level-${c.level}">${c.level}</span>
                <span style="font-size: 0.58rem; color: var(--text-caption); display:block; margin-top:2px;">${LEVEL_NAMES[c.level] || ''}</span>
            </td>
            <td style="font-size: 0.75rem; max-width: 250px;">${c.evidence || '—'}</td>
        </tr>
    `).join('');
}


// ── Export ──

function exportPDF() {
    window.print();
}


// ── Init ──

window.addEventListener('DOMContentLoaded', () => {
    goToStep(1);
});

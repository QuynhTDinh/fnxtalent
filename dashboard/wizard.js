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

let AREA_INFO = {
    'K': { short: 'Kiến thức', full: 'Knowledge — Kiến thức', group: 'Knowledge' },
    'S': { short: 'Kỹ năng', full: 'Skill — Kỹ năng', group: 'Skills' },
    'A': { short: 'Thái độ', full: 'Attitude — Thái độ', group: 'Attitude' },
};

let LEVEL_NAMES = {
    1: 'Nền tảng',
    2: 'Đang phát triển',
    3: 'Thành thạo',
    4: 'Nâng cao',
    5: 'Bậc thầy',
    6: 'Tiên phong'
};

let TOTAL_LEVELS = 6;
let TAXONOMY_DATA = null;

async function loadTaxonomy() {
    try {
        const resp = await fetch(`${API_BASE}/api/taxonomy`);
        if (!resp.ok) throw new Error('API Error');
        const data = await resp.json();
        TAXONOMY_DATA = data;
        
        // Dynamically rebuild LEVEL_NAMES
        LEVEL_NAMES = {};
        let maxLvl = 0;
        for (const [lvl, info] of Object.entries(data.levels)) {
            LEVEL_NAMES[lvl] = info.vi;
            if (parseInt(lvl) > maxLvl) maxLvl = parseInt(lvl);
        }
        TOTAL_LEVELS = maxLvl || 6;
        
        // Dynamically rebuild AREA_INFO
        AREA_INFO = {};
        data.ask_groups.forEach(g => {
            AREA_INFO[g.id] = {
                short: g.vi,
                full: `${g.name} — ${g.vi}`,
                group: g.id === 'K' ? 'Knowledge' : (g.id === 'S' ? 'Skills' : 'Attitude')
            };
        });
        
        console.log("✓ Taxonomy loaded successfully from API", TAXONOMY_DATA);
    } catch (err) {
        console.warn("⚠ Failed to load taxonomy from API, using fallback cache in memory.", err);
    }
}


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
        `Đánh giá dựa trên khung FNX Taxonomy · ${new Date().toLocaleDateString('vi-VN')}`;

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

    // Auto-save to history
    saveToHistory(assessment, jdResult, matchResult);
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
        'Knowledge': { areas: ['K'], color: '#34c759', items: [] },
        'Skills': { areas: ['S'], color: '#5ac8fa', items: [] },
        'Attitude': { areas: ['A'], color: '#af52de', items: [] },
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
        radar = new RadarChart('radarCanvas', { width: 480, height: 480, levels: TOTAL_LEVELS });
    }

    // ── SHADOW MAPPING: ASK (11) → TLD (3 Axes) ──
    const tldMapping = {
        'TECHNICAL': { name: 'Kỹ thuật (Technical)', ids: ['K1', 'K2', 'K2', 'S2'], color: '#34c759', area: 'K' },
        'INTERPERSONAL': { name: 'Giao tiếp (Interpersonal)', ids: ['S1', 'S5', 'A2', 'A3'], color: '#5ac8fa', area: 'S' },
        'CONCEPTUAL': { name: 'Tư duy (Conceptual)', ids: ['S3', 'S4', 'A1'], color: '#af52de', area: 'A' }
    };

    const axes = Object.values(tldMapping).map(m => ({ code: m.name, name: m.name, area: m.area }));
    
    // Calculate candidate values
    const candidateValues = Object.values(tldMapping).map(m => {
        const scores = (assessment.competencies || [])
            .filter(c => m.ids.includes(c.code))
            .map(c => c.level);
        return scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
    });

    // Calculate target values
    const targetValues = Object.values(tldMapping).map(m => {
        const scores = (jdResult.required_competencies || [])
            .filter(c => m.ids.includes(c.code))
            .map(c => c.target_level);
        return scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
    });

    radar.setData(axes, candidateValues, targetValues);
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

    tbody.innerHTML = comps.map(c => {
        const safeArea = c.area || (c.code ? c.code.charAt(0) : 'K');
        const areaLabel = AREA_INFO[safeArea]?.short || safeArea;
        return `
        <tr>
            <td>
                <span style="font-weight:600; color: var(--accent-blue); font-size: 0.72rem;">${c.code}</span>
                <br><span style="font-size: 0.58rem; color: var(--text-caption);">${areaLabel}</span>
            </td>
            <td style="font-weight:500; color: var(--text-primary);">${c.name || ''}</td>
            <td>
                <span class="level-badge level-${c.level}">${c.level}</span>
                <span style="font-size: 0.58rem; color: var(--text-caption); display:block; margin-top:2px;">${LEVEL_NAMES[c.level] || ''}</span>
            </td>
            <td style="font-size: 0.75rem; max-width: 250px;">${c.evidence || '—'}</td>
        </tr>
    `}).join('');
}


// ── History ──

async function saveToHistory(assessment, jdResult, matchResult) {
    try {
        const fitScore = matchResult.fit_score ?? matchResult.fitScore ?? 0;
        await fetch(`${API_BASE}/api/history/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidateName: assessment.fullName || document.getElementById('cvName').value || 'Ứng viên',
                role: jdResult.role || document.getElementById('jdRole').value || 'Vị trí',
                fitScore,
                assessment,
                jdResult,
                matchResult,
            }),
        });
    } catch (err) {
        console.warn('History save failed:', err);
    }
}


// ── Export ──

async function exportPDF() {
    const btn = document.querySelector('.report-actions .btn-action');
    const origText = btn.textContent;
    btn.textContent = '⏳ Đang tạo PDF...';
    btn.disabled = true;

    try {
        const reportEl = document.querySelector('.report-container');

        // Capture report as canvas
        const canvas = await html2canvas(reportEl, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#f5f5f7',
            logging: false,
        });

        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageW = 210;
        const pageH = 297;
        const margin = 10;
        const contentW = pageW - margin * 2;

        // Header branding
        pdf.setFillColor(0, 113, 227);
        pdf.rect(0, 0, pageW, 12, 'F');
        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(9);
        pdf.setFont(undefined, 'bold');
        pdf.text('FNX Talent Factory', margin, 8);
        pdf.setFont(undefined, 'normal');
        pdf.setFontSize(7);
        pdf.text(`Báo cáo đánh giá năng lực · ${new Date().toLocaleDateString('vi-VN')}`, pageW - margin, 8, { align: 'right' });

        // Add report image
        const imgData = canvas.toDataURL('image/jpeg', 0.92);
        const imgW = contentW;
        const imgH = (canvas.height * imgW) / canvas.width;
        const startY = 16;

        let y = startY;
        let remainH = imgH;
        let srcY = 0;

        while (remainH > 0) {
            const sliceH = Math.min(remainH, pageH - y - margin);
            const sliceRatio = sliceH / imgH;
            const srcSliceH = canvas.height * sliceRatio;

            // Create slice canvas
            const sliceCanvas = document.createElement('canvas');
            sliceCanvas.width = canvas.width;
            sliceCanvas.height = srcSliceH;
            const ctx = sliceCanvas.getContext('2d');
            ctx.drawImage(canvas, 0, srcY, canvas.width, srcSliceH, 0, 0, canvas.width, srcSliceH);

            const sliceImg = sliceCanvas.toDataURL('image/jpeg', 0.92);
            pdf.addImage(sliceImg, 'JPEG', margin, y, imgW, sliceH);

            remainH -= sliceH;
            srcY += srcSliceH;

            if (remainH > 0) {
                pdf.addPage();
                y = margin;
            }
        }

        // Footer on last page
        pdf.setTextColor(150, 150, 150);
        pdf.setFontSize(6);
        pdf.text('FNX Talent Factory v2 · Powered by Gemini AI · Framework: FNX Taxonomy', pageW / 2, pageH - 5, { align: 'center' });

        // Download
        const candName = document.getElementById('reportCandidateName')?.textContent || 'candidate';
        const date = new Date().toISOString().slice(0, 10);
        pdf.save(`FNX_Report_${candName.replace(/\s+/g, '_')}_${date}.pdf`);

    } catch (err) {
        console.error('PDF export error:', err);
        alert('Lỗi xuất PDF: ' + err.message);
    } finally {
        btn.textContent = origText;
        btn.disabled = false;
    }
}


// ── File Upload ──

function initDropZones() {
    document.querySelectorAll('.drop-zone').forEach(zone => {
        const input = zone.querySelector('.drop-input');
        const targetId = zone.dataset.target;

        // Click to browse
        zone.addEventListener('click', (e) => {
            if (e.target === input) return;
            input.click();
        });

        // File selected via input
        input.addEventListener('change', () => {
            if (input.files.length > 0) handleFileUpload(input.files[0], zone, targetId);
        });

        // Drag events
        zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('dragover'); });
        zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) handleFileUpload(e.dataTransfer.files[0], zone, targetId);
        });
    });
}

async function handleFileUpload(file, zone, targetTextareaId) {
    const content = zone.querySelector('.drop-zone-content');
    const loading = zone.querySelector('.drop-loading');
    const success = zone.querySelector('.drop-success');

    // Validate
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'doc'].includes(ext)) {
        alert('Chỉ hỗ trợ file .pdf hoặc .docx');
        return;
    }

    // Show loading
    content.style.display = 'none';
    success.style.display = 'none';
    loading.style.display = '';

    try {
        const formData = new FormData();
        formData.append('file', file);

        const resp = await fetch(`${API_BASE}/api/file/extract`, {
            method: 'POST',
            body: formData,
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || `Error ${resp.status}`);
        }

        const result = await resp.json();

        // Populate textarea
        document.getElementById(targetTextareaId).value = result.text;

        // Show success
        loading.style.display = 'none';
        success.style.display = '';
        success.querySelector('.drop-filename').textContent = `${file.name} (${result.chars} ký tự)`;

        // Clear any previous analysis since content changed
        if (targetTextareaId === 'jdContent') jdData = null;
        if (targetTextareaId === 'cvContent') cvData = null;

    } catch (err) {
        console.error('File upload error:', err);
        alert('Lỗi trích xuất file: ' + err.message);
        loading.style.display = 'none';
        content.style.display = '';
    }
}


// ── Init ──

window.addEventListener('DOMContentLoaded', async () => {
    await loadTaxonomy();
    goToStep(1);
    initDropZones();
});

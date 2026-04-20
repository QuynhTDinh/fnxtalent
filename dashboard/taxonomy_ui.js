const API_BASE = '';
let TAXONOMY_DATA = null;
let LEVELS = [];
let ASK_GROUPS = [];
let TLD_ZONES = {};
let ROLES = {};
let TOTAL_LEVELS = 6;
let currentRole = '';
let currentViewMode = 'ask';

async function initUI() {
    try {
        const resp = await fetch(`${API_BASE}/api/taxonomy`);
        if (!resp.ok) throw new Error('API Error');
        TAXONOMY_DATA = await resp.json();
        
        parseTaxonomyData();
        renderRoleSelector();
        renderLevels(); 
        renderLegend(); 
        renderCompetencyCards(currentViewMode);
        
        // Select first role
        const roleKeys = Object.keys(ROLES);
        if(roleKeys.length > 0) {
            selectRole(roleKeys[0]);
        } else {
            drawRadar(); 
        }
    } catch (err) {
        console.error("Failed to load taxonomy from API", err);
        document.querySelector('.taxonomy-layout').innerHTML = `<div style="text-align:center; padding: 50px;">Lỗi tải dữ liệu Taxonomy từ server: ${err.message}</div>`;
    }
}

function parseTaxonomyData() {
    const data = TAXONOMY_DATA;
    
    // 1. Parse Levels
    LEVELS = [];
    let maxLvl = 0;
    for (const [lvl, info] of Object.entries(data.levels)) {
        const lNum = parseInt(lvl);
        if (lNum > maxLvl) maxLvl = lNum;
        LEVELS.push({
            l: lNum,
            name: info.name,
            vi: info.vi,
            bloom: info.bloom || "",
            career: info.career_alias || "",
            abb: info.abb_role || "",
            exp: info.experience || "",
            desc: info.description || ""
        });
    }
    LEVELS.sort((a,b) => a.l - b.l);
    TOTAL_LEVELS = maxLvl || 6;
    
    // 2. Parse TLD Zones
    TLD_ZONES = {};
    for (const [key, zone] of Object.entries(data.tld_zones || {})) {
        TLD_ZONES[key] = {
            name: zone.name,
            vi: zone.vi,
            desc: zone.description,
            color: zone.color,
            ids: zone.competency_ids || [],
            ui_alias: zone.ui_alias || ""
        };
    }
    
    // 3. Parse ASK Groups
    ASK_GROUPS = [];
    data.ask_groups.forEach(g => {
        const comps = [];
        (g.competencies || []).forEach(c => {
            comps.push({
                id: c.id,
                name: c.vi || c.name,
                en: c.en,
                desc: c.description,
                lv: c.levels || {}
            });
        });
        
        ASK_GROUPS.push({
            id: g.id,
            name: g.name,
            vi: g.vi,
            train: "", 
            color: g.color || "#666",
            comps: comps
        });
    });
    
    // 4. Parse Roles
    ROLES = {};
    for (const [key, r] of Object.entries(data.role_profiles || {})) {
        let levelAvg = 3; 
        if (r.expected_level) {
            const cleanStr = r.expected_level.replace('–', '-').replace('a', '');
            const parts = cleanStr.split('-').map(str => parseFloat(str.trim()));
            if(parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
                levelAvg = (parts[0] + parts[1]) / 2;
            } else if (!isNaN(parts[0])) {
                levelAvg = parts[0];
            }
        }
        
        ROLES[key] = {
            name: r.vi || r.name,
            exp: r.expected_level ? `Level ${r.expected_level}` : "",
            katz: r.katz_weights || {}, // Still using katz_weights from YAML
            ask: r.ask_weights || {},
            levelAvg: levelAvg,
            desc: r.description || "",
            department_name: r.department_name || "General",
            job_title_name: r.job_title_name || r.name,
            competency_targets: r.competency_targets || {}
        };
    }
    
    // Update stats dynamically
    document.querySelectorAll('.stat-number')[0].textContent = ASK_GROUPS.length;
    let totalComps = 0; ASK_GROUPS.forEach(g => totalComps += g.comps.length);
    document.querySelectorAll('.stat-number')[1].textContent = totalComps;
    document.querySelectorAll('.stat-number')[2].textContent = totalComps * TOTAL_LEVELS;
    document.querySelectorAll('.stat-number')[3].textContent = TOTAL_LEVELS;
    document.querySelectorAll('.stat-number')[4].textContent = Object.keys(ROLES).length;
    
    const baselineText = document.querySelector('.legend-actual').nextSibling;
    if(baselineText) {
        baselineText.textContent = ` Baseline L${Math.max(1, Math.floor(TOTAL_LEVELS/2))}`;
    }
}

function getTldColor(compId) { 
    for (const [, z] of Object.entries(TLD_ZONES)) { 
        if (z.ids.includes(compId)) return z.color;
    } 
    return '#666'; 
}

function getTldName(compId) { 
    for (const [, z] of Object.entries(TLD_ZONES)) { 
        if (z.ids.includes(compId)) return z.vi; 
    } 
    return ''; 
}

function renderRoleSelector() {
    const sel = document.getElementById('roleSelector');
    if (!sel) return;
    sel.innerHTML = '';
    
    const depts = {};
    Object.entries(ROLES).forEach(([rid, r]) => {
        const dName = r.department_name;
        if (!depts[dName]) depts[dName] = [];
        depts[dName].push({ id: rid, role: r });
    });
    
    let html = '';
    for (const [dept, rolesList] of Object.entries(depts)) {
        html += `<optgroup label="${dept}">`;
        rolesList.forEach(item => {
            html += `<option value="${item.id}">${item.role.job_title_name} - ${item.role.name}</option>`;
        });
        html += `</optgroup>`;
    }
    sel.innerHTML = html;
}

function renderLevels() {
    const tb = document.getElementById('levelTableBody');
    tb.innerHTML = '';
    LEVELS.forEach(l => { 
        tb.innerHTML += `<tr><td><span class="level-badge level-${l.l}">${l.l}</span></td><td><strong>${l.vi}</strong><br><span style="font-size:.7rem;color:var(--text-caption)">${l.name}</span></td><td><span style="font-weight:600; color:var(--accent-blue); padding: 3px 8px; border-radius: 6px; background: rgba(0,113,227,0.08); font-size: 0.78rem;">${l.career}</span></td><td><span class="bloom-tag bloom-${l.l}">${l.bloom}</span></td><td style="font-size:.78rem">${l.abb}</td><td>${l.exp}</td><td>${l.desc}</td></tr>`;
    });
}

function renderCareer() {
    const grid = document.getElementById('careerGrid'); 
    if(!grid) return;
    grid.innerHTML = '';
    
    const tldLabels = {};
    const tldColors = {};
    const tldAlias = {};
    for (const [key, zone] of Object.entries(TLD_ZONES)) {
        tldLabels[key] = zone.vi || zone.name;
        tldColors[key] = zone.color;
        if (zone.ui_alias) tldAlias[zone.ui_alias.toUpperCase()] = key;
    }
    
    Object.entries(ROLES).forEach(([rid, r]) => {
        let bars = '';
        Object.entries(r.katz).forEach(([k, pct]) => { 
            const kUp = k.toUpperCase();
            const tKey = tldAlias[kUp] || kUp;
            bars += `<div class="career-bar"><div class="career-bar-top"><span class="career-bar-label">${tldLabels[tKey] || tKey}</span><span class="career-bar-pct">${pct}%</span></div><div class="career-bar-track"><div class="career-bar-fill" style="width:${pct}%;background:${tldColors[tKey] || '#666'}"></div></div></div>`;
        });
        grid.innerHTML += `<div class="career-card ${rid === currentRole ? 'active' : ''}" onclick="selectRole('${rid}')"><h4>${r.name}</h4><div class="career-exp">${r.exp || 'N/A'}</div><div style="font-size:.72rem;color:var(--text-secondary);margin-bottom:8px;font-style:italic">${r.desc}</div>${bars}</div>`;
    });
}

function renderLegend() {
    const el = document.getElementById('radarLegend'); 
    if(!el) return;
    el.innerHTML = '';
    ASK_GROUPS.forEach(g => {
        el.innerHTML += `<div class="legend-group-label" style="color:${g.color}">${g.vi || g.name} (${g.id})</div>`;
        g.comps.forEach(c => { 
            el.innerHTML += `<div class="legend-row"><div class="legend-dot-sm" style="background:${getTldColor(c.id)}"></div><span class="legend-cid">${c.id}</span><span class="legend-cname">${c.name}</span><span class="legend-katz">${getTldName(c.id)}</span></div>`;
        });
    });
}

function renderCompetencyCards(mode = 'ask') {
    const grid = document.getElementById('askGrid'); 
    if(!grid) return;
    grid.innerHTML = '';
    
    let groups = [];
    
    if (mode === 'ask') {
        groups = ASK_GROUPS;
    } else {
        const allComps = [];
        ASK_GROUPS.forEach(g => g.comps.forEach(c => allComps.push(c)));
        
        Object.entries(TLD_ZONES).forEach(([key, zone]) => {
            const compsInZone = allComps.filter(c => zone.ids.includes(c.id));
            if(compsInZone.length > 0) {
                // Add a formula string to the train field just to be cool
                const formulaStr = zone.name.includes("=") ? zone.name.split("(")[1].replace(")", "") : "";
                groups.push({
                    id: key,
                    name: zone.vi || zone.name,
                    vi: zone.vi,
                    desc: zone.desc,
                    train: formulaStr, 
                    color: zone.color,
                    comps: compsInZone
                });
            }
        });
    }

    groups.forEach(g => {
        let cl = '';
        g.comps.forEach(c => {
            let lvH = ''; 
            for (let i = 1; i <= TOTAL_LEVELS; i++) {
                if (c.lv[i]) {
                    lvH += `<div class="level-row"><span class="level-badge level-${i}" style="flex-shrink:0">${i}</span><span class="level-row-text">${c.lv[i]}</span></div>`;
                }
            }
            cl += `<div class="comp-row" onclick="this.classList.toggle('open')"><div class="comp-row-header"><span class="comp-id-tag" style="background:${getTldColor(c.id)}">${c.id}</span><span class="comp-row-name">${c.name}</span><span class="comp-katz-tag">${getTldName(c.id)}</span><span class="comp-chevron">&#9654;</span></div><div class="comp-detail"><div class="comp-desc">${c.desc || ''}<span class="comp-en">${c.en || ''}</span></div>${lvH}</div></div>`;
        });
        
        const formulaHtml = g.train ? `<div class="ask-train" style="margin-top:2px; font-weight:bold">${g.train}</div>` : '';
        const descHtml = g.desc ? `<div style="margin-top:6px; font-size:.75rem; color:var(--text-tertiary); max-width: 95%; line-height: 1.4; border-left: 2px solid ${g.color}; padding-left: 6px;">${g.desc}</div>` : '';
        grid.innerHTML += `<div class="ask-card"><div class="ask-card-header" style="align-items:flex-start"><div><div class="ask-title" style="color:${g.color}">${g.name}</div>${formulaHtml}${descHtml}</div><span class="ask-count" style="flex-shrink:0">${g.comps.length}</span></div><div class="comp-list">${cl}</div></div>`;
    });
}

function switchViewMode(mode) {
    if (currentViewMode === mode) return;
    currentViewMode = mode;
    document.querySelectorAll('.view-btn').forEach(b => b.classList.toggle('active', b.dataset.view === mode));
    renderCompetencyCards(mode);
}

function drawRadar() {
    const canvas = document.getElementById('radarCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const dpr = window.devicePixelRatio || 1; 
    canvas.width = 440 * dpr; 
    canvas.height = 440 * dpr; 
    canvas.style.width = '440px'; 
    canvas.style.height = '440px'; 
    
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
    
    const W = 440, H = 440, cx = W / 2, cy = H / 2, R = (Math.min(W,H)/2) - 60;
    
    const allComps = []; 
    ASK_GROUPS.forEach(g => g.comps.forEach(c => {
        allComps.push({ ...c, areaColor: getTldColor(c.id), areaId: g.id });
    }));
    
    const n = allComps.length;
    if (n === 0) return;
    
    const step = (Math.PI * 2) / n;
    ctx.clearRect(0, 0, W, H);
    
    for (let ring = 1; ring <= TOTAL_LEVELS; ring++) { 
        const r = R * (ring / TOTAL_LEVELS); 
        ctx.beginPath(); 
        for (let i = 0; i <= n; i++) { 
            const a = i * step - Math.PI / 2; 
            const x = cx + Math.cos(a) * r;
            const y = cy + Math.sin(a) * r; 
            if (i === 0) ctx.moveTo(x, y); 
            else ctx.lineTo(x, y);
        } 
        ctx.closePath(); 
        ctx.strokeStyle = 'rgba(0,0,0,.06)'; 
        ctx.lineWidth = 1; 
        ctx.stroke(); 
        
        ctx.fillStyle = 'rgba(0,0,0,.12)'; 
        ctx.font = '500 10px Inter,sans-serif'; 
        ctx.textAlign = 'right'; 
        ctx.textBaseline = 'middle'; 
        ctx.fillText(ring, cx - 6, cy - r);
    }
    
    allComps.forEach((_, i) => { 
        const a = i * step - Math.PI / 2; 
        ctx.beginPath(); 
        ctx.moveTo(cx, cy); 
        ctx.lineTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R); 
        ctx.strokeStyle = 'rgba(0,0,0,.04)'; 
        ctx.stroke();
    });
    
    ctx.beginPath(); 
    const baselineLvl = Math.max(1, Math.floor(TOTAL_LEVELS/2));
    allComps.forEach((_, i) => { 
        const a = i * step - Math.PI / 2;
        const r = R * (baselineLvl / TOTAL_LEVELS); 
        const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r; 
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }); 
    ctx.closePath(); 
    ctx.fillStyle = 'rgba(0,113,227,.06)'; 
    ctx.fill(); 
    ctx.strokeStyle = 'rgba(0,113,227,.35)'; 
    ctx.lineWidth = 1.5; 
    ctx.stroke();
    
    if (ROLES[currentRole]) {
        const rProfile = ROLES[currentRole];
        const baseLevel = rProfile.levelAvg || 3;
        
        let totalW = 0;
        let countW = 0;
        Object.values(rProfile.ask).forEach(w => { totalW += w; countW++; });
        const avgW = totalW / (countW || 1);
        
        const targets = allComps.map(c => {
            let targetLvl = rProfile.competency_targets[c.id];
            if (targetLvl === undefined || targetLvl === 0) {
                // Fallback algorithm
                const areaW = rProfile.ask[c.areaId] || avgW;
                const factor = areaW / avgW;
                targetLvl = baseLevel * factor;
            }
            return Math.min(TOTAL_LEVELS, Math.max(1, targetLvl));
        });
        
        ctx.beginPath(); 
        targets.forEach((lv, i) => { 
            const a = i * step - Math.PI / 2;
            const r = R * (lv / TOTAL_LEVELS); 
            const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r; 
            i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        }); 
        ctx.closePath(); 
        ctx.fillStyle = 'rgba(255,45,85,.06)'; 
        ctx.fill(); 
        ctx.strokeStyle = 'rgba(255,45,85,.5)'; 
        ctx.lineWidth = 2; 
        ctx.stroke();
        
        targets.forEach((lv, i) => { 
            const a = i * step - Math.PI / 2;
            const r = R * (lv / TOTAL_LEVELS); 
            const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r; 
            
            ctx.fillStyle = allComps[i].areaColor; 
            ctx.beginPath(); 
            ctx.arc(x, y, 3.5, 0, Math.PI * 2); 
            ctx.fill(); 
            
            const lx = cx + Math.cos(a) * (R + 18), ly = cy + Math.sin(a) * (R + 18); 
            ctx.fillStyle = allComps[i].areaColor; 
            ctx.font = "600 10px 'JetBrains Mono',monospace"; 
            ctx.textAlign = 'center'; 
            ctx.textBaseline = 'middle'; 
            ctx.fillText(allComps[i].id, lx, ly);
        });
    }
}

function selectRole(role) {
    if (!ROLES[role]) return;
    currentRole = role;
    
    const sel = document.getElementById('roleSelector');
    if (sel && sel.value !== role) sel.value = role;
    
    const roleLabel = document.getElementById('roleLabel');
    if (roleLabel) {
        roleLabel.textContent = ROLES[role].name + ' Target';
    }
    drawRadar(); 
    renderCareer();
}

window.addEventListener('DOMContentLoaded', initUI);

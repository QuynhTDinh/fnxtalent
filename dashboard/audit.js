let currentRoles = [];

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            processFile(e.target.files[0]);
            e.target.value = '';
        }
    });

    // Hidden drag drop
    document.addEventListener('dragover', (e) => {
        e.preventDefault();
    });
    document.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length > 0) {
            processFile(e.dataTransfer.files[0]);
        }
    });
});

async function processFile(file) {
    const nameExt = file.name.split('.').pop().toLowerCase();
    
    if (nameExt === 'csv') {
        uploadToServer(file, file.name);
    } else if (nameExt === 'xlsx' || nameExt === 'xls') {
        showLoading("Đang biên dịch tệp...");
        try {
            const data = await file.arrayBuffer();
            const workbook = XLSX.read(data, { type: 'array' });
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            const csvText = XLSX.utils.sheet_to_csv(worksheet);
            
            const csvBlob = new Blob([csvText], { type: 'text/csv' });
            const csvFile = new File([csvBlob], file.name.replace(/\.[^/.]+$/, "") + ".csv", { type: 'text/csv' });
            
            uploadToServer(csvFile, file.name);
        } catch (err) {
            hideLoading();
            alert("Lỗi đọc tệp: " + err.message);
        }
    } else {
        alert("Chỉ hỗ trợ tệp .csv hoặc .xlsx");
    }
}

async function uploadToServer(csvFile) {
    showLoading("Đang phân tích dữ liệu sơ đồ tổ chức...");
    const formData = new FormData();
    formData.append("file", csvFile);

    try {
        const response = await fetch("/api/audit/org-chart/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Lỗi kết nối máy chủ.");

        const data = await response.json();
        
        const groupTag = document.getElementById('departmentSelect').value;
        const newRoles = (data.roles || []).map(r => ({
            title: r.title,
            group_tag: groupTag, 
            status: 'pending'
        }));
        
        currentRoles = [...currentRoles, ...newRoles];
        renderGrid();
    } catch (err) {
        alert("Lỗi: " + err.message);
    } finally {
        hideLoading();
    }
}

function renderGrid() {
    const tbody = document.getElementById('gridBody');
    tbody.innerHTML = '';

    if (currentRoles.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4"><div class="empty-state">Chức danh trống. Bấm "Thêm chức danh" hoặc "Tải tệp sơ đồ tổ chức" để bắt đầu.</div></td></tr>`;
        return;
    }

    currentRoles.forEach((role, idx) => {
        const tr = document.createElement('tr');
        
        let statusBadge = '';
        let actionBtn = '';

        if (role.status === 'ready') {
            statusBadge = `<span class="badge badge-ready">Đang chờ thi</span>`;
            actionBtn = `<button class="btn-text" onclick="generateAssessment(${idx})" style="color: #64748b; margin-right: 10px;">📋 Copy Link</button> <button class="btn-text" onclick="checkStatus(${idx})">🔄 Kiểm tra</button>`;
        } else if (role.status === 'completed') {
            statusBadge = `<span class="badge" style="background: #e0e7ff; color: #4338ca;">Đợi chấm điểm</span>`;
            actionBtn = `<button class="btn-text" onclick="triggerEvaluation(${idx})" style="color: #ea580c; font-weight: bold;">⭐ Chấm bằng AI</button>`;
        } else if (role.status === 'evaluated') {
            statusBadge = `<span class="badge" style="background: #dcfce3; color: #166534;">Hoàn tất</span>`;
            actionBtn = `<button class="btn-text" onclick="showResult(${idx})">📊 Xem Báo cáo Radar</button>`;
        } else {
            statusBadge = `<span class="badge badge-pending">Chờ xử lý</span>`;
            actionBtn = `<button class="btn-text" onclick="generateAssessment(${idx})">Tạo bài đánh giá</button>`;
        }

        // Format label
        let groupLabel = role.group_tag;
        if(role.group_tag==="Operations/Technical") groupLabel="Khối Vận hành/Kỹ thuật";
        if(role.group_tag==="Support") groupLabel="Khối Hành chính/Hỗ trợ";
        if(role.group_tag==="Front-line") groupLabel="Khối Tiền tuyến/Kinh doanh";
        if(role.group_tag==="Ban QLDA") groupLabel="Khối Dự án";

        tr.innerHTML = `
            <td style="font-weight: 500;">${role.title}</td>
            <td style="color: #64748b; font-size: 0.85rem;">${groupLabel}</td>
            <td>${statusBadge}</td>
            <td>${actionBtn}</td>
        `;
        tbody.appendChild(tr);
    });
}

function toggleInlineAdd() {
    const row = document.getElementById('inlineAddRow');
    if (row.style.display === 'flex') {
        row.style.display = 'none';
    } else {
        row.style.display = 'flex';
        document.getElementById('inlineRoleName').focus();
    }
}

function addSingleRole() {
    const titleInput = document.getElementById('inlineRoleName');
    const title = titleInput.value.trim();
    if (!title) return;

    const groupTag = document.getElementById('departmentSelect').value;
    currentRoles.unshift({
        title: title,
        group_tag: groupTag,
        status: 'pending'
    });
    
    titleInput.value = '';
    toggleInlineAdd();
    renderGrid();
}

function generateStandardList() {
    const groupTag = document.getElementById('departmentSelect').value;
    
    let standard = [];
    if (groupTag === "Support") {
        standard = ["Kế toán trưởng", "Chuyên viên quản lý chi phí", "Chuyên viên pháp chế", "Chuyên viên nhân sự", "Chuyên viên thu mua"];
    } else if (groupTag === "Operations/Technical") {
        standard = ["Quản đốc xưởng", "Kỹ sư hệ thống điện", "Kỹ sư cơ khí trực ca", "Trưởng ca vận hành", "Cán bộ An toàn HSE"];
    } else if (groupTag === "Front-line") {
        standard = ["Giám đốc kinh doanh vùng", "Trưởng kênh phân phối", "Chuyên viên thị trường", "Nhân viên dịch vụ CSKH", "Kỹ sư nông nghiệp"];
    } else {
        standard = ["Giám đốc dự án", "Kỹ sư bóc tách khối lượng (QS)", "Chuyên viên hồ sơ đấu thầu", "Giám sát thi công", "Kỹ sư thiết kế"];
    }
    
    const newRoles = standard.map(r => ({
        title: r,
        group_tag: groupTag,
        status: 'pending'
    }));

    currentRoles = [...newRoles, ...currentRoles];
    renderGrid();
}

async function generateAssessment(index) {
    const role = currentRoles[index];
    
    // Nếu đã tạo rồi, mở luôn drawer từ data cũ (lưu cache nếu có thì tốt, tạm thời gọi lại hoặc mock)
    // Để cho flow mượt, mock luôn API call
    
    const industry = document.getElementById('industryContext').value;
    const company = document.getElementById('companyContext').value;

    showLoading();
    
    try {
        // Phân tích Seniority theo chức danh
        let seniority = "Chuyên viên (Specialist) - Bloom Core 2-3";
        const roleLower = role.title.toLowerCase();
        if (roleLower.includes("giám đốc") || roleLower.includes("trưởng phòng") || roleLower.includes("quản đốc")) {
            seniority = "Quản lý Cấp cao (Manager/Director) - Bloom Core 4-5";
        } else if (roleLower.includes("trưởng ca") || roleLower.includes("nhóm trưởng") || roleLower.includes("leader")) {
            seniority = "Quản lý Cấp trung (Leader/Supervisor) - Bloom Core 3-4";
        } else if (roleLower.includes("kỹ sư") || roleLower.includes("chuyên viên sâu") || roleLower.includes("senior")) {
            seniority = "Chuyên viên Bậc cao (Senior) - Bloom Core 3-4";
        }

        const payload = {
            roles: [{
                role: role.title,
                seniority: seniority,
                jd: "Hệ thống tự động tham chiếu theo ngành",
                group_tag: role.group_tag,
                industry: industry,
                company: company
            }]
        };

        const response = await fetch("/api/audit/combat/generate-batch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Máy chủ từ chối yêu cầu.");

        const data = await response.json();
        const scenarioInfo = data.scenarios[0];
        
        if (scenarioInfo.error) {
            alert("Lỗi hệ thống: " + scenarioInfo.error);
            return;
        }

        // Cập nhật trạng thái lưới
        currentRoles[index].status = 'ready';
        currentRoles[index].test_id = scenarioInfo.test_id;
        renderGrid();
        
        // Mở drawer
        openDrawer(scenarioInfo);
    } catch (err) {
        console.error(err);
        alert(err.message);
    } finally {
        hideLoading();
    }
}

async function checkStatus(index) {
    const role = currentRoles[index];
    if (!role.test_id) return;

    showLoading("Đang làm mới dữ liệu...");
    try {
        const res = await fetch(`/api/audit/test/${role.test_id}`);
        if (!res.ok) throw new Error("Không thể kiểm tra trạng thái.");
        const data = await res.json();
        
        if (data.status === 'completed') {
            currentRoles[index].status = 'completed';
        } else if (data.status === 'evaluated') {
            currentRoles[index].status = 'evaluated';
            currentRoles[index].evaluation = data.evaluation_result;
        }
        renderGrid();
    } catch(err) {
        alert(err.message);
    } finally {
        hideLoading();
    }
}

async function triggerEvaluation(index) {
    const role = currentRoles[index];
    if (!role.test_id) return;

    showLoading("Hệ thống FNX AI đang phân tích dữ liệu ứng viên. Vui lòng đợi...");
    try {
        const res = await fetch(`/api/audit/test/${role.test_id}/evaluate`, {
            method: "POST"
        });
        if (!res.ok) throw new Error("Chấm điểm thất bại.");
        const data = await res.json();
        
        currentRoles[index].status = 'evaluated';
        currentRoles[index].evaluation = data.evaluation;
        renderGrid();
        
        showResult(index);
    } catch(err) {
        alert(err.message);
    } finally {
        hideLoading();
    }
}

let currentChart = null;

function showResult(index) {
    const role = currentRoles[index];
    const drawer = document.getElementById('sideDrawer');
    const title = document.getElementById('drawerTitle');
    const content = document.getElementById('drawerContent');
    
    title.innerText = `Báo Cáo Năng Lực: ${role.title}`;
    
    const ev = role.evaluation;
    if (!ev) { alert("Thiếu dữ liệu kết quả chấm."); return; }

    const isStar = ev.eval_mode === "STAR";
    const modeLabel = isStar ? "Luồng Tư Duy Chiến Lược (STAR)" : "Luồng Tuân thủ Tiêu chuẩn (Red-Flag)";

    let html = `
        <div style="background:#f8fafc; padding:15px; border-radius:6px; border:1px solid #e2e8f0; margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-weight:600; color:#334155;">Độ Phù Hợp:</span>
                <span style="font-size:1.5rem; font-weight:700; color:${ev.fit_score_percentage > 70 ? '#10b981' : '#f59e0b'};">${ev.fit_score_percentage}%</span>
            </div>
            <div style="font-size:0.85rem; color:#64748b;">Chế độ chấm: ${modeLabel}</div>
        </div>

        <div style="width: 100%; height: 300px; margin-bottom: 2rem;">
            <canvas id="radarChart"></canvas>
        </div>

        <div style="margin-bottom: 1.5rem;">
            <h4 style="margin-bottom:0.5rem;">Kết luận từ FNX AI Evaluator:</h4>
            <div style="font-style:italic; border-left:3px solid #2563eb; padding-left:10px; color:#334155;">${ev.executive_summary}</div>
        </div>
    `;

    // Hybrid Render UI
    if (isStar && ev.star_analysis) {
        html += `
            <div style="background:#fff; border:1px solid #cbd5e1; border-radius:6px; overflow:hidden;">
                <div style="background:#f1f5f9; padding:10px 15px; font-weight:600; color:#0f172a; border-bottom:1px solid #cbd5e1;">Phân Tích Cấu Trúc STAR</div>
                <div style="padding:15px; display:flex; flex-direction:column; gap:10px;">
                    <div><strong style="color:#2563eb">S - Situation:</strong> <span style="color:#475569">${ev.star_analysis.situation_understanding}</span></div>
                    <div><strong style="color:#2563eb">T - Task:</strong> <span style="color:#475569">${ev.star_analysis.task_definition}</span></div>
                    <div><strong style="color:#2563eb">A - Action:</strong> <span style="color:#475569">${ev.star_analysis.action_quality}</span></div>
                    <div><strong style="color:#2563eb">R - Result:</strong> <span style="color:#475569">${ev.star_analysis.result_orientation}</span></div>
                </div>
            </div>
        `;
    } else {
        let rfHtml = ev.red_flags && ev.red_flags.length > 0
            ? ev.red_flags.map(r => `<li style="color:#b91c1c;">${r}</li>`).join('')
            : '<li style="color:#15803d;">Tuyệt vời, không có Cờ đỏ nghiêm trọng.</li>';

        html += `
            <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:15px; margin-bottom:1rem;">
                <h4 style="margin-top:0; color:#b91c1c;">🚩 Cảnh báo Cờ Đỏ (Red Flags)</h4>
                <ul style="margin:0; padding-left:20px;">${rfHtml}</ul>
            </div>
            
            <div style="display:flex; justify-content:space-between; align-items:center; background:#f8fafc; padding:10px; border:1px solid #e2e8f0; border-radius:4px;">
                <span style="font-size:0.85rem; color:#475569;">Skin-in-the-game Index:</span>
                <span style="font-weight:600; font-size:0.9rem;">${ev.skin_in_the_game_index || "N/A"}</span>
            </div>
        `;
    }

    content.innerHTML = html;
    drawer.classList.add('open');

    // Mất 1 chút delay để canvas render DOM trước khi init Chart.js
    setTimeout(() => {
        const ctx = document.getElementById('radarChart').getContext('2d');
        if (currentChart) currentChart.destroy();
        
        currentChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['SOP', 'Technical', 'Leadership', 'Delivery', 'Crisis Prevention'],
                datasets: [{
                    label: 'Điểm năng lực Ứng viên',
                    data: [
                        ev.radar_scores.SOP,
                        ev.radar_scores.Technical,
                        ev.radar_scores.Leadership,
                        ev.radar_scores.Delivery,
                        ev.radar_scores.Crisis_Prevention
                    ],
                    backgroundColor: 'rgba(37, 99, 235, 0.2)',
                    borderColor: 'rgba(37, 99, 235, 1)',
                    pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(0, 0, 0, 0.1)' },
                        grid: { color: 'rgba(0, 0, 0, 0.1)' },
                        pointLabels: { font: { size: 12, family: 'Inter' } },
                        min: 0,
                        max: 5,
                        ticks: { stepSize: 1, display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }, 50);
}

function openDrawer(scenario) {
    const drawer = document.getElementById('sideDrawer');
    const title = document.getElementById('drawerTitle');
    const content = document.getElementById('drawerContent');
    
    title.innerText = scenario.role;
    
    let html = `
        <div style="display: flex; gap: 10px; margin-bottom: 1.5rem;">
            <input type="text" id="testLinkCopy" readonly style="flex: 1; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px; background: #f1f5f9; font-size: 0.85rem;" value="${window.location.origin}/test?id=${scenario.test_id || ''}">
            <button onclick="copyTestLink()" style="background: #10b981; color: white; border: none; border-radius: 4px; padding: 0 1rem; font-weight: 500; cursor: pointer;">Copy Link</button>
        </div>
        <h4>Bối cảnh sự cố</h4>
        <pre>${scenario.background_context}</pre>
        <h4>Nhiệm vụ kiểm tra năng lực</h4>
    `;
    
    if (scenario.questions && scenario.questions.length > 0) {
        scenario.questions.forEach((q, i) => {
            html += `
                <div class="q-card">
                    <div class="q-meta">
                        <span>Câu ${i + 1}</span>
                        <span>Mục tiêu: ${q.targeted_competency}</span>
                        <span>Độ khó (Bloom): ${q.expected_bloom_level}</span>
                    </div>
                    <div class="q-text">${q.question_text}</div>
                </div>
            `;
        });
    } else {
        html += "<p>Hệ thống không thể phát sinh bài tập.</p>";
    }
    
    content.innerHTML = html;
    drawer.classList.add('open');
}

function copyTestLink() {
    const input = document.getElementById('testLinkCopy');
    input.select();
    document.execCommand("copy");
    alert("Đã sao chép đường dẫn bài kiểm tra!");
}

function closeDrawer() {
    document.getElementById('sideDrawer').classList.remove('open');
}

function showLoading(text = "Đang xử lý...") {
    const l = document.getElementById('loader');
    l.innerText = text;
    l.style.display = 'block';
}

function hideLoading() {
    document.getElementById('loader').style.display = 'none';
}

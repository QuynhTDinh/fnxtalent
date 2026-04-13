// Internal Audit Dashboard Logic

let currentRoles = [];

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('auditDropZone');
    const fileInput = document.getElementById('fileInput');

    // Drag & Drop handlers
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary-color)';
        dropZone.style.background = 'rgba(175, 82, 222, 0.05)';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '';
        dropZone.style.background = '';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '';
        dropZone.style.background = '';
        if (e.dataTransfer.files.length > 0) {
            processFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            processFile(e.target.files[0]);
            // reset input
            e.target.value = '';
        }
    });
});

async function processFile(file) {
    const nameExt = file.name.split('.').pop().toLowerCase();
    
    if (nameExt === 'csv') {
        // Direct upload if already CSV
        uploadToServer(file, file.name);
    } else if (nameExt === 'xlsx' || nameExt === 'xls') {
        // Convert Excel to CSV via SheetJS
        showLoading("Đang biên dịch tệp Excel sang định dạng hệ thống (CSV)...");
        try {
            const data = await file.arrayBuffer();
            const workbook = XLSX.read(data, { type: 'array' });
            
            // Assume the first worksheet has the data
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            
            // Convert to CSV
            const csvText = XLSX.utils.sheet_to_csv(worksheet);
            
            // Create a pseudo File object representing the CSV
            const csvBlob = new Blob([csvText], { type: 'text/csv' });
            const csvFile = new File([csvBlob], file.name.replace(/\.[^/.]+$/, "") + ".csv", { type: 'text/csv' });
            
            uploadToServer(csvFile, file.name);
        } catch (err) {
            hideLoading();
            alert("Lỗi khi đọc file Excel nội bộ: " + err.message);
        }
    } else {
        alert("Định dạng file không được hỗ trợ. Vui lòng tải lên .csv hoặc .xlsx");
    }
}

async function uploadToServer(csvFile, originalName) {
    showLoading("Đang phân tích và gom cụm Org Chart (AI Matrix)...");
    
    const formData = new FormData();
    formData.append("file", csvFile);

    try {
        const response = await fetch("/api/audit/org-chart/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Lỗi khi gửi file lên Server");

        const data = await response.json();
        currentRoles = data.roles || [];
        
        renderRolesTable(currentRoles);
        document.getElementById('dropText').innerText = `Đã đối chiếu thành công: ${originalName}`;
        
    } catch (err) {
        console.error(err);
        alert(err.message);
    } finally {
        hideLoading();
    }
}

function renderRolesTable(roles) {
    const container = document.getElementById('rolesContainer');
    const tbody = document.getElementById('rolesBody');
    tbody.innerHTML = '';

    if (roles.length === 0) {
        alert("Không tìm thấy cấu trúc nhân sự / chức danh hợp lệ trong file.");
        return;
    }

    roles.forEach((role, idx) => {
        const tr = document.createElement('tr');
        
        const tdTitle = document.createElement('td');
        tdTitle.innerText = role.title;
        tdTitle.style.fontWeight = '500';
        
        const tdCount = document.createElement('td');
        tdCount.innerHTML = `<span style="background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; color: #5ac8fa;">${role.employee_count} thành viên</span>`;
        
        const tdAction = document.createElement('td');
        const btn = document.createElement('button');
        btn.className = 'btn-gen';
        btn.innerHTML = '⚡ Auto-Gen Combat';
        btn.onclick = () => generateCombatForRole(idx);
        
        tdAction.appendChild(btn);
        
        tr.appendChild(tdTitle);
        tr.appendChild(tdCount);
        tr.appendChild(tdAction);
        
        tbody.appendChild(tr);
    });

    container.style.display = 'block';
}

async function generateCombatForRole(roleIndex) {
    const roleData = currentRoles[roleIndex];
    
    showLoading(`Đang khởi tạo Combat Matrix cho vị trí: ${roleData.title}...`);
    
    try {
        const payload = {
            roles: [
                {
                    role: roleData.title,
                    seniority: "Junior", 
                    jd: roleData.jd || ""
                }
            ]
        };

        const response = await fetch("/api/audit/combat/generate-batch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Server từ chối tính toán Combat Scenario.");

        const data = await response.json();
        const scenarioInfo = data.scenarios[0];
        
        if (scenarioInfo.error) {
            alert("Lỗi AI: " + scenarioInfo.error);
            return;
        }

        showModal(scenarioInfo);
    } catch (err) {
        console.error(err);
        alert(err.message);
    } finally {
        hideLoading();
    }
}

function showModal(scenario) {
    const modal = document.getElementById('combatModal');
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');
    
    title.innerText = scenario.scenario_title || "Tình huống Audit";
    
    let html = `
        <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 3px solid #af52de;">
            <strong style="color: #af52de;">Target Role:</strong> <span style="color:#fff;">${scenario.role}</span>
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <h4 style="color: #5ac8fa; margin-bottom: 0.5rem; font-size: 1.05rem;">Bối cảnh Sự cố (Background)</h4>
            <pre>${scenario.background_context}</pre>
        </div>
        
        <div>
            <h4 style="color: #5ac8fa; margin-bottom: 0.5rem; font-size: 1.05rem;">Barem Câu hỏi (Combat Tasks)</h4>
    `;
    
    if (scenario.questions && scenario.questions.length > 0) {
        scenario.questions.forEach((q, i) => {
            html += `
                <div style="padding: 1.25rem; border: 1px solid rgba(255,255,255,0.1); border-left: 4px solid #34c759; background: rgba(52, 199, 89, 0.05); margin-bottom: 1rem; border-radius: 6px;">
                    <div style="margin-bottom: 8px; font-size: 0.85rem; display: flex; gap: 8px;">
                        <span style="background: #34c759; color: #000; padding: 2px 6px; border-radius: 4px; font-weight: bold;">Câu ${i + 1}</span>
                        <span style="border: 1px solid rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px; color: #ddd;">Target: ${q.targeted_competency}</span>
                        <span style="border: 1px solid #af52de; color: #af52de; padding: 2px 6px; border-radius: 4px;">Bloom Level: ${q.expected_bloom_level}</span>
                    </div>
                    <div style="color: #fff; font-size: 1.05rem; margin-top: 10px;">${q.question_text}</div>
                </div>
            `;
        });
    } else {
        html += "<p>AI không thể phát sinh câu hỏi rủi ro, vui lòng thử lại.</p>";
    }
    
    html += `</div>`;
    
    body.innerHTML = html;
    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('combatModal').style.display = 'none';
}

function showLoading(text) {
    document.getElementById('loadingText').innerText = text;
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

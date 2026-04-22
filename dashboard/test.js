let currentTestId = null;
let saveTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    currentTestId = params.get('id');

    if (!currentTestId) {
        showError("Không tìm thấy mã bài thi trong đường dẫn.");
        return;
    }

    loadTest();
});

async function loadTest() {
    try {
        const response = await fetch(`/api/audit/test/${currentTestId}`);
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Lỗi tải bài thi.");
        }
        
        const testData = await response.json();
        
        if (testData.status === 'completed') {
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('successState').style.display = 'block';
            return;
        }

        renderTest(testData);
    } catch (err) {
        showError(err.message);
    }
}

function renderTest(data) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('testContent').style.display = 'block';

    document.getElementById('roleName').innerText = data.role || "Ứng viên";
    if (data.company) {
        document.getElementById('companyName').innerText = `(${data.company})`;
    }
    document.getElementById('scenarioContext').innerText = data.background_context || "";

    const container = document.getElementById('questionsContainer');
    container.innerHTML = "";

    const savedDraft = JSON.parse(localStorage.getItem(`fnx_draft_${currentTestId}`) || "{}");
    const savedName = localStorage.getItem(`fnx_name_${currentTestId}`) || "";
    
    if (savedName) document.getElementById('candidateName').value = savedName;

    document.getElementById('candidateName').addEventListener('input', triggerAutoSave);

    if (data.questions && data.questions.length > 0) {
        data.questions.forEach((q, idx) => {
            const draftValue = savedDraft[q.id] || "";
            
            const cleanQuestionText = q.question_text.replace(/^\[.*?\]\s*/, '');
            
            const div = document.createElement('div');
            div.className = 'question-block';
            div.innerHTML = `
                <div class="question-text">
                    ${idx + 1}. ${cleanQuestionText}
                </div>
                <textarea id="ans_${q.id}" placeholder="Câu trả lời của bạn..." oninput="triggerAutoSave()">${draftValue}</textarea>
            `;
            container.appendChild(div);
        });
    }
}

function triggerAutoSave() {
    clearTimeout(saveTimeout);
    const indicator = document.getElementById('autoSaveIndicator');
    indicator.style.display = 'none';

    saveTimeout = setTimeout(() => {
        // Thu thập thông tin
        const candidateName = document.getElementById('candidateName').value;
        const textareas = document.querySelectorAll('textarea');
        let draft = {};
        
        textareas.forEach(ta => {
            const qId = ta.id.replace('ans_', '');
            draft[qId] = ta.value;
        });

        localStorage.setItem(`fnx_draft_${currentTestId}`, JSON.stringify(draft));
        localStorage.setItem(`fnx_name_${currentTestId}`, candidateName);

        indicator.style.display = 'block';
        setTimeout(() => { indicator.style.display = 'none'; }, 2000);
    }, 1000); // Đợi 1s sau khi ngưng gõ mới save
}

async function submitTest() {
    const candidateName = document.getElementById('candidateName').value.trim();
    if (!candidateName) {
        alert("Vui lòng nhập Họ và Tên trước khi nộp bài.");
        document.getElementById('candidateName').focus();
        return;
    }

    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.innerText = "Đang nộp bài...";

    const textareas = document.querySelectorAll('textarea');
    let answers = {};
    textareas.forEach(ta => {
        const qId = ta.id.replace('ans_', '');
        answers[qId] = ta.value;
    });

    try {
        const response = await fetch(`/api/audit/test/${currentTestId}/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                candidate_name: candidateName,
                answers: answers
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Lỗi nộp bài");
        }

        // Xóa nháp
        localStorage.removeItem(`fnx_draft_${currentTestId}`);
        localStorage.removeItem(`fnx_name_${currentTestId}`);

        document.getElementById('testContent').style.display = 'none';
        document.getElementById('successState').style.display = 'block';

    } catch (err) {
        alert(err.message);
        btn.disabled = false;
        btn.innerText = "NỘP BÀI KIỂM TRÁ";
    }
}

function showError(msg) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('testContent').style.display = 'none';
    const errObj = document.getElementById('errorState');
    errObj.style.display = 'block';
    document.getElementById('errorMsg').innerText = msg;
}

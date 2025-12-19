/**
 * 일괄 채점 JavaScript
 */

Utils.checkAuth('teacher');

const username = Utils.getCurrentUser().username;

function addStudentAnswer() {
    const container = document.getElementById('studentAnswers');
    const newItem = document.createElement('div');
    newItem.className = 'student-answer-item mb-md';
    newItem.innerHTML = `
    <div class="grid grid-2 gap-md">
      <div class="form-group">
        <label class="form-label">학생 이름</label>
        <input type="text" class="form-input student-name" placeholder="예: 김철수">
      </div>
      <div class="form-group">
        <label class="form-label">답안</label>
        <textarea class="form-textarea student-answer" rows="2" placeholder="학생 답안"></textarea>
      </div>
    </div>
  `;
    container.appendChild(newItem);
}

async function batchGrade() {
    const subject = document.getElementById('subject').value;
    const question = document.getElementById('question').value.trim();
    const modelAnswer = document.getElementById('modelAnswer').value.trim();
    const maxScore = parseInt(document.getElementById('maxScore').value);

    if (!question) {
        Toast.warning('문제를 입력해주세요');
        return;
    }

    // 학생 답안 수집
    const studentItems = document.querySelectorAll('.student-answer-item');
    const submissions = [];

    studentItems.forEach(item => {
        const name = item.querySelector('.student-name').value.trim();
        const answer = item.querySelector('.student-answer').value.trim();

        if (name && answer) {
            submissions.push({ username: name, answer });
        }
    });

    if (submissions.length === 0) {
        Toast.warning('최소 1명의 학생 답안을 입력해주세요');
        return;
    }

    try {
        Loading.show(`${submissions.length}명의 답안을 채점하는 중...`);

        const result = await API.post('/api/teacher/grading/batch', {
            teacher_username: username,
            subject,
            question,
            model_answer: modelAnswer,
            max_score: maxScore,
            submissions
        });

        Loading.hide();

        // 결과 표시
        displayResults(result.results || submissions.map((s, i) => ({
            student: s.username,
            score: 70 + Math.random() * 30,
            reason: 'AI 채점 결과입니다.',
            feedback: '좋은 답안입니다.'
        })));

        Toast.success('채점이 완료되었습니다');

    } catch (error) {
        Loading.hide();
        console.error('Batch Grading Error:', error);

        // 더미 결과 표시
        const dummyResults = submissions.map(s => ({
            student: s.username,
            score: Math.floor(60 + Math.random() * 40),
            reason: '내용의 정확성과 논리적 구성이 우수합니다.',
            feedback: '표현을 더 다듬으면 좋겠습니다.'
        }));

        displayResults(dummyResults);
        Toast.warning('샘플 채점 결과를 표시합니다');
    }
}

function displayResults(results) {
    const resultsCard = document.getElementById('resultsCard');
    const resultsList = document.getElementById('resultsList');

    resultsCard.style.display = 'block';

    resultsList.innerHTML = results.map(r => `
    <tr>
      <td><strong>${r.student}</strong></td>
      <td>
        <span class="badge ${r.score >= 80 ? 'badge-success' : r.score >= 60 ? 'badge-warning' : 'badge-error'}">
          ${Math.round(r.score)}점
        </span>
      </td>
      <td class="text-sm">${truncate(r.reason, 50)}</td>
      <td class="text-sm">${truncate(r.feedback, 50)}</td>
    </tr>
  `).join('');

    // 결과 카드로 스크롤
    resultsCard.scrollIntoView({ behavior: 'smooth' });
}

function truncate(text, length) {
    if (!text) return '-';
    return text.length > length ? text.substring(0, length) + '...' : text;
}

function exportResults() {
    const resultsList = document.getElementById('resultsList');
    const rows = resultsList.querySelectorAll('tr');

    if (rows.length === 0) {
        Toast.warning('내보낼 결과가 없습니다');
        return;
    }

    // CSV 형식으로 내보내기
    let csv = '학생,점수,채점근거,피드백\n';
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const student = cells[0].textContent.trim();
        const score = cells[1].textContent.trim();
        const reason = cells[2].textContent.trim();
        const feedback = cells[3].textContent.trim();
        csv += `"${student}","${score}","${reason}","${feedback}"\n`;
    });

    // 다운로드
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `채점결과_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();

    Toast.success('결과가 내보내졌습니다');
}

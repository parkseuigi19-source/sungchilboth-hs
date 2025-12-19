/**
 * 서술형 답안 제출 및 채점 JavaScript
 */

Utils.checkAuth('student');

const username = Utils.getCurrentUser().username;

// 페이지 로드 시 이력 불러오기
document.addEventListener('DOMContentLoaded', () => {
  loadHistory();
});

// 글자 수 카운터 업데이트
function updateCharCount() {
  const textarea = document.getElementById('studentAnswerInput');
  const counter = document.getElementById('charCounter');
  counter.textContent = `${textarea.value.length}자`;
}

// 답안 제출 및 채점
async function submitGrading() {
  const subject = document.getElementById('subjectInput').value;
  const question = document.getElementById('questionInput').value.trim();
  const modelAnswer = document.getElementById('modelAnswerInput').value.trim();
  const studentAnswer = document.getElementById('studentAnswerInput').value.trim();

  // 유효성 검사
  if (!question) {
    Toast.warning('문제를 입력해주세요');
    return;
  }

  if (!studentAnswer) {
    Toast.warning('답안을 작성해주세요');
    return;
  }

  try {
    Loading.show('AI가 채점하는 중...');

    const response = await API.post('/api/grading/essay', {
      username,
      subject,
      question,
      student_answer: studentAnswer,
      model_answer: modelAnswer || undefined,
      max_score: 100
    });
    const result = response.success ? response.data : response;

    Loading.hide();

    // 채점 결과 표시
    showGradingResult(result);

    // 폼 초기화
    document.getElementById('questionInput').value = '';
    document.getElementById('modelAnswerInput').value = '';
    document.getElementById('studentAnswerInput').value = '';
    updateCharCount();

    // 이력 새로고침
    loadHistory();

  } catch (error) {
    Loading.hide();
    console.error('Grading Error:', error);
    Toast.error('채점에 실패했습니다');
  }
}

// 채점 결과 표시
function showGradingResult(result) {
  const scoreClass = result.score >= 80 ? 'success' : result.score >= 60 ? 'warning' : 'error';
  const percentage = result.percentage || ((result.score / result.max_score) * 100).toFixed(1);

  Modal.create('📊 채점 결과', `
    <div style="padding: 20px;">
      <!-- 점수 -->
      <div style="text-align: center; margin-bottom: 32px;">
        <div style="font-size: 4rem; font-weight: 700; color: var(--${scoreClass});">
          ${result.score}점
        </div>
        <div style="color: var(--text-medium); font-size: var(--font-lg);">
          ${result.max_score}점 만점 (${percentage}%)
        </div>
        <div class="progress mt-md" style="max-width: 300px; margin: 16px auto;">
          <div class="progress-bar" style="width: ${percentage}%;"></div>
        </div>
      </div>
      
      <!-- 채점 근거 -->
      <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; margin-bottom: 16px;">
        <h4 style="margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
          <span>📝</span> 채점 근거
        </h4>
        <p style="line-height: 1.8; color: var(--text-dark); white-space: pre-wrap;">${result.reason || result.grading_reason}</p>
      </div>
      
      <!-- 피드백 -->
      <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; margin-bottom: 24px;">
        <h4 style="margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
          <span>💬</span> 개선 피드백
        </h4>
        <p style="line-height: 1.8; color: var(--text-dark); white-space: pre-wrap;">${result.feedback}</p>
      </div>
      
      <!-- 버튼 -->
      <div style="display: flex; gap: 12px;">
        <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()" style="flex: 1;">
          확인
        </button>
        <button class="btn btn-outline" onclick="viewDetail(${result.id})" style="flex: 1;">
          상세 보기
        </button>
      </div>
    </div>
  `, { closeOnOverlay: false });
}

// 채점 이력 불러오기
async function loadHistory() {
  try {
    const response = await API.post('/api/grading/history', {
      username: username,
      limit: 10
    });
    const history = response.success ? response.data : [];
    renderHistory(history);
  } catch (error) {
    console.error('History Error:', error);
    document.getElementById('historyList').innerHTML =
      '<p class="text-center text-medium">이력을 불러올 수 없습니다</p>';
  }
}

// 이력 렌더링
function renderHistory(history) {
  const container = document.getElementById('historyList');

  if (!history || history.length === 0) {
    container.innerHTML = '<p class="text-center text-medium">아직 채점 이력이 없습니다</p>';
    return;
  }

  container.innerHTML = history.map(item => {
    const scoreClass = item.score >= 80 ? 'success' : item.score >= 60 ? 'warning' : 'error';

    return `
      <div class="history-item" onclick="viewDetail(${item.id})">
        <div class="flex-between mb-sm">
          <div>
            <span class="badge badge-purple">${item.subject}</span>
            <span class="badge badge-${scoreClass}">${item.score}점</span>
          </div>
          <span class="text-sm text-light">${Utils.formatDate(item.created_at)}</span>
        </div>
        <div class="text-bold mb-xs">${truncate(item.question, 80)}</div>
        <div class="text-sm text-medium">${truncate(item.student_answer, 100)}</div>
      </div>
    `;
  }).join('');
}

// 상세 보기
async function viewDetail(gradingId) {
  try {
    Loading.show();
    const response = await API.get(`/api/grading/detail/${gradingId}`);
    const detail = response.success ? response.data : response;
    Loading.hide();

    const scoreClass = detail.score >= 80 ? 'success' : detail.score >= 60 ? 'warning' : 'error';

    Modal.create('📄 채점 상세 정보', `
      <div style="padding: 20px;">
        <!-- 헤더 -->
        <div class="flex-between mb-lg">
          <div>
            <span class="badge badge-purple">${detail.subject}</span>
            <span class="badge badge-${scoreClass}">${detail.score}점</span>
          </div>
          <span class="text-sm text-light">${Utils.formatDateTime(detail.created_at)}</span>
        </div>
        
        <!-- 문제 -->
        <div class="mb-md">
          <h4 class="mb-sm">📝 문제</h4>
          <div style="background: var(--bg-card); padding: 16px; border-radius: 8px; line-height: 1.8;">
            ${detail.question}
          </div>
        </div>
        
        <!-- 모범 답안 -->
        ${detail.model_answer && detail.model_answer !== '모범답안 없음' ? `
          <div class="mb-md">
            <h4 class="mb-sm">💡 모범 답안</h4>
            <div style="background: #e8f5e9; padding: 16px; border-radius: 8px; line-height: 1.8;">
              ${detail.model_answer}
            </div>
          </div>
        ` : ''}
        
        <!-- 나의 답안 -->
        <div class="mb-md">
          <h4 class="mb-sm">✍️ 나의 답안</h4>
          <div style="background: var(--bg-card); padding: 16px; border-radius: 8px; line-height: 1.8;">
            ${detail.student_answer}
          </div>
        </div>
        
        <!-- 채점 근거 -->
        <div class="mb-md">
          <h4 class="mb-sm">📊 채점 근거</h4>
          <div style="background: var(--bg-card); padding: 16px; border-radius: 8px; line-height: 1.8;">
            ${detail.grading_reason}
          </div>
        </div>
        
        <!-- 피드백 -->
        <div class="mb-lg">
          <h4 class="mb-sm">💬 피드백</h4>
          <div style="background: var(--bg-card); padding: 16px; border-radius: 8px; line-height: 1.8;">
            ${detail.feedback}
          </div>
        </div>
        
        <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()" style="width: 100%;">
          닫기
        </button>
      </div>
    `);

  } catch (error) {
    Loading.hide();
    console.error('Detail Error:', error);
    Toast.error('상세 정보를 불러올 수 없습니다');
  }
}

// 텍스트 자르기
function truncate(text, length) {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
}

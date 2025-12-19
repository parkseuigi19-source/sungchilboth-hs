/**
 * 성취도 대시보드 JavaScript
 */

// 권한 확인
Utils.checkAuth('student');

const username = Utils.getCurrentUser().username;

// username이 없으면 로그인 페이지로 리다이렉트
if (!username) {
  console.error('Username not found in localStorage');
  window.location.href = '/login';
}

let subjectChart = null;
let trendChart = null;

// 페이지 로드 시 데이터 가져오기
document.addEventListener('DOMContentLoaded', async () => {
  await loadDashboardData();
});

// 대시보드 데이터 로드
async function loadDashboardData() {
  try {
    Loading.show('성취도 분석 중...');

    const response = await API.get(`/api/dashboard?username=${encodeURIComponent(username)}`);
    const data = response.success ? response : response;

    // 통계 카드 업데이트
    updateStatCards(data);

    // 차트 렌더링
    renderCharts(data);

    // 강점/약점 표시
    renderStrengthsWeaknesses(data);

    // 최근 활동 표시
    try {
      await renderRecentActivity();
    } catch (activityError) {
      console.error('Recent Activity Load Error:', activityError);
    }

    Loading.hide();
    Toast.success('대시보드를 불러왔습니다');

  } catch (error) {
    Loading.hide();
    console.error('Dashboard Error:', error);
    Toast.error('데이터를 불러오는데 실패했습니다');

    // 더미 데이터로 대체
    loadDummyData();
  }
}

function updateStatCards(data) {
  // achievement_scores에서 유효한 숫자값만 추출
  const rawScores = data.achievement_scores ? Object.values(data.achievement_scores) : [];
  const scores = rawScores.map(s => parseFloat(s)).filter(s => !isNaN(s));

  const totalScore = scores.length > 0
    ? scores.reduce((a, b) => a + b, 0) / scores.length
    : 0;

  const totalScoreEl = document.getElementById('totalScore');
  const totalQuestionsEl = document.getElementById('totalQuestions');
  const avgScoreEl = document.getElementById('avgScore');
  const studyDaysEl = document.getElementById('studyDays');

  // 값이 NaN인 경우를 대비한 최종 방어
  const displayTotalScore = isNaN(totalScore) ? 0 : Math.round(totalScore);
  const displayTotalQuestions = data.total_questions || 0;
  const displayAvgScore = isNaN(parseFloat(data.average_score)) ? 0 : Math.round(data.average_score);
  const displayStudyDays = data.study_days || 0;

  if (totalScoreEl) totalScoreEl.textContent = `${displayTotalScore}%`;
  if (totalQuestionsEl) totalQuestionsEl.textContent = displayTotalQuestions;
  if (avgScoreEl) avgScoreEl.textContent = `${displayAvgScore}점`;
  if (studyDaysEl) studyDaysEl.textContent = `${displayStudyDays}일`;

  console.log('Dashboard Stats Updated:', { displayTotalScore, displayTotalQuestions, displayAvgScore, displayStudyDays });
}

// 차트 렌더링
function renderCharts(data) {
  // 과목별 성취도 차트
  if (data.achievement_scores) {
    const labels = Object.keys(data.achievement_scores);
    const values = Object.values(data.achievement_scores);

    const ctx = document.getElementById('subjectChart');
    if (subjectChart) subjectChart.destroy();

    subjectChart = ChartHelper.createBar(ctx, {
      labels: labels,
      values: values,
      label: '성취도 (%)'
    });
  }

  // 성취도 추이 차트 (더미 데이터)
  const trendCtx = document.getElementById('trendChart');
  if (trendChart) trendChart.destroy();

  trendChart = ChartHelper.createLine(trendCtx, {
    labels: ['1주차', '2주차', '3주차', '4주차', '5주차'],
    values: [65, 70, 68, 75, 80],
    label: '성취도 (%)'
  });
}

// 강점/약점 렌더링
function renderStrengthsWeaknesses(data) {
  const strengthList = document.getElementById('strengthList');
  const weaknessList = document.getElementById('weaknessList');

  // 강점
  if (strengthList) {
    if (data.strong_areas && data.strong_areas.length > 0) {
      strengthList.innerHTML = data.strong_areas.map(area => `
        <div class="strength-item">
          <div class="text-bold">${area.concept || area}</div>
          <div class="text-sm text-medium">${area.score ? `점수: ${area.score}점` : '잘하고 있어요!'}</div>
        </div>
      `).join('');
    } else {
      strengthList.innerHTML = '<p class="text-center text-medium">아직 데이터가 없습니다</p>';
    }
  }

  // 약점
  if (weaknessList) {
    if (data.weak_points && data.weak_points.length > 0) {
      weaknessList.innerHTML = data.weak_points.map(point => `
        <div class="weakness-item">
          <div class="text-bold">${point.weak_concept || point.concept || point}</div>
          <div class="text-sm text-medium">${point.recommendation || '추가 학습이 필요합니다'}</div>
        </div>
      `).join('');
    } else {
      weaknessList.innerHTML = '<p class="text-center text-medium">약점이 발견되지 않았습니다 👍</p>';
    }
  }
}



// 최근 활동 렌더링
async function renderRecentActivity() {
  try {
    const response = await API.post('/api/grading/history', {
      username: username,
      limit: 5
    });
    const history = response.success ? response.data : [];
    const timeline = document.getElementById('activityTimeline');
    if (!timeline) return;

    if (history && history.length > 0) {
      timeline.innerHTML = history.map(item => {
        let icon = '📝';
        let badgeClass = 'badge-success';

        if (item.type === 'chat') {
          icon = '💬';
          badgeClass = 'badge-purple';
        } else if (item.type === 'analysis') {
          icon = '🔍';
          badgeClass = 'badge-warning';
        } else if (item.score < 80) {
          badgeClass = item.score >= 60 ? 'badge-warning' : 'badge-error';
        }

        return `
            <div class="timeline-item">
                <div class="activity-icon-container" style="font-size: 1.2rem; margin-right: 15px;">${icon}</div>
                <div style="flex: 1;">
                    <div class="flex-between mb-xs">
                        <span class="text-bold">${item.title}</span>
                        <span class="timeline-time">${Utils.timeAgo(item.time)}</span>
                    </div>
                    <div class="text-sm text-medium mb-xs text-truncate" style="max-width: 250px;">${item.content}</div>
                    <div class="flex-between">
                        <span class="badge ${badgeClass}">${item.type === 'chat' ? '질문' : item.type === 'analysis' ? '분석' : '채점'}</span>
                        ${item.score > 0 ? `<span class="text-bold text-purple">${item.score}점</span>` : ''}
                    </div>
                </div>
            </div>
        `;
      }).join('');
    } else {
      timeline.innerHTML = '<p class="text-center text-medium">아직 학습 활동이 없습니다</p>';
    }
  } catch (error) {
    console.error('Activity Error:', error);
    document.getElementById('activityTimeline').innerHTML =
      '<p class="text-center text-medium">활동 내역을 불러올 수 없습니다</p>';
  }
}

// 학습 시작
function startLearning(code) {
  Toast.info('학습을 시작합니다');
  window.location.href = `/student/routine?code=${code}`;
}

// 더미 데이터 로드 (API 실패 시)
function loadDummyData() {
  const dummyData = {
    achievement_scores: {
      '문법': 75,
      '문학': 82,
      '독서': 68,
      '화법과 작문': 70
    },
    total_questions: 45,
    average_score: 73.75,
    study_days: 12,
    strong_areas: [
      { concept: '문학 작품 분석', score: 85 },
      { concept: '문법 규칙 이해', score: 80 }
    ],
    weak_points: [
      { weak_concept: '비문학 독해', recommendation: '다양한 지문을 읽어보세요' },
      { weak_concept: '어휘력', recommendation: '어휘 학습을 강화하세요' }
    ],
    recommended_areas: [
      { title: '비문학 독해 연습', description: '약점 보완을 위한 추천', code: 'reading-01' },
      { title: '어휘력 향상', description: '기초 어휘 학습', code: 'vocab-01' }
    ]
  };

  updateStatCards(dummyData);
  renderCharts(dummyData);
  renderStrengthsWeaknesses(dummyData);

  Toast.warning('샘플 데이터를 표시하고 있습니다');
}

/**
 * E-포트폴리오 JavaScript
 */

Utils.checkAuth('student');

const username = Utils.getCurrentUser().username;
let progressChart = null;
let areaChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadPortfolio();
});

async function loadPortfolio() {
  try {
    Loading.show('포트폴리오를 불러오는 중...');

    const response = await API.post('/api/portfolio/data', {
      username: username,
      subject: '국어'
    });
    const data = response.success ? response.data : response;

    renderPortfolio(data);

    Loading.hide();
    Toast.success('포트폴리오를 불러왔습니다');

  } catch (error) {
    Loading.hide();
    console.error('Portfolio Error:', error);
    Toast.warning('샘플 데이터를 표시합니다');
    renderDummyPortfolio();
  }
}

function renderPortfolio(data) {
  // 통계
  document.getElementById('totalQuestions').textContent = data.total_questions || 0;
  document.getElementById('avgScore').textContent = (data.average_score || 0).toFixed(1);
  document.getElementById('totalScore').textContent = data.total_score || 0;

  // 차트
  renderCharts(data);

  // 강점/약점
  renderStrengthsWeaknesses(data);

  // 학습 기록
  renderLearningRecords(data);
}

function renderCharts(data) {
  // 성취도 추이
  const progressData = data.learning_progress || null;
  if (progressData) {
    const ctx = document.getElementById('progressChart');
    if (progressChart) progressChart.destroy();
    progressChart = ChartHelper.createLine(ctx, progressData);
  }

  // 영역별 성취도
  const strongAreas = data.strong_areas || [];
  const weakAreas = data.weak_areas || [];

  const areas = [...strongAreas, ...weakAreas];
  if (areas.length > 0) {
    const ctx = document.getElementById('areaChart');
    if (areaChart) areaChart.destroy();
    areaChart = ChartHelper.createRadar(ctx, {
      labels: areas.map(a => a.concept || a),
      values: areas.map(a => a.score || 70)
    });
  }
}

function renderStrengthsWeaknesses(data) {
  const strongAreas = data.strong_areas || [];
  const weakAreas = data.weak_areas || [];

  document.getElementById('strongAreas').innerHTML = strongAreas.length > 0
    ? strongAreas.map(area => `
        <div class="strength-item mb-sm">
          <div class="text-bold">${area.concept || area}</div>
          <div class="text-sm text-medium">점수: ${area.score || 'N/A'}</div>
        </div>
      `).join('')
    : '<p class="text-center text-medium">데이터가 없습니다</p>';

  document.getElementById('weakAreas').innerHTML = weakAreas.length > 0
    ? weakAreas.map(area => `
        <div class="weakness-item mb-sm">
          <div class="text-bold">${area.concept || area}</div>
          <div class="text-sm text-medium">${area.recommendation || '추가 학습 필요'}</div>
        </div>
      `).join('')
    : '<p class="text-center text-medium">약점이 없습니다 👍</p>';
}

function renderLearningRecords(data) {
  // 최근 학습 기록 표시 (더미)
  const records = [
    { date: '2025-12-01', subject: '문법', topic: '주어와 서술어', score: 85 },
    { date: '2025-12-02', subject: '문학', topic: '시의 표현 기법', score: 90 },
    { date: '2025-12-03', subject: '독서', topic: '비문학 독해', score: 75 }
  ];

  document.getElementById('learningRecords').innerHTML = `
    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>날짜</th>
            <th>과목</th>
            <th>주제</th>
            <th>점수</th>
          </tr>
        </thead>
        <tbody>
          ${records.map(r => `
            <tr>
              <td>${r.date}</td>
              <td><span class="badge badge-purple">${r.subject}</span></td>
              <td>${r.topic}</td>
              <td><span class="badge ${r.score >= 80 ? 'badge-success' : 'badge-warning'}">${r.score}점</span></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

async function generatePDF() {
  try {
    Loading.show('PDF를 생성하는 중...');

    const result = await API.post('/api/portfolio/generate-pdf', {
      username: username,
      subject: '국어'
    });

    Loading.hide();

    if (result.pdf_path) {
      Toast.success('PDF가 생성되었습니다');
      // 백엔드에서 받은 상대 경로를 사용하여 다운로드
      const downloadUrl = result.pdf_path.startsWith('/') ? result.pdf_path : '/' + result.pdf_path;
      window.open(downloadUrl, '_blank');
    } else {
      Toast.error('PDF를 생성할 수 없습니다. 잠시 후 다시 시도해 주세요.');
    }

  } catch (error) {
    Loading.hide();
    console.error('PDF Error:', error);
    Toast.error('PDF 생성에 실패했습니다');
  }
}

function renderDummyPortfolio() {
  const dummyData = {
    total_questions: 45,
    average_score: 78.5,
    total_score: 3532,
    strong_areas: [
      { concept: '문법', score: 85 },
      { concept: '문학', score: 82 }
    ],
    weak_areas: [
      { concept: '독서', score: 68, recommendation: '비문학 독해 연습 필요' }
    ],
    learning_progress: {
      labels: ['1주', '2주', '3주', '4주', '5주'],
      values: [65, 70, 75, 77, 78.5]
    }
  };

  renderPortfolio(dummyData);
}

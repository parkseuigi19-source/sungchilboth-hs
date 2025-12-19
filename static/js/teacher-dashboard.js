/**
 * 교사 대시보드 JavaScript
 */

Utils.checkAuth('teacher');

const username = Utils.getCurrentUser().username;

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

async function loadDashboard() {
    try {
        Loading.show();

        // API에서 실제 데이터 가져오기
        const response = await fetch('/api/teacher/dashboard-stats?teacher_username=teacher1'); // TODO: 실제 로그인된 교사 ID 사용
        const result = await response.json();

        if (result.success) {
            renderRecentQuestions(result.questions);
            renderPendingGrading(result.pending);
            renderClassChart(result.chart);
        } else {
            console.error("데이터 로드 실패:", result.message);
        }

        Loading.hide();

    } catch (error) {
        Loading.hide();
        console.error('Dashboard Error:', error);
    }
}

function renderRecentQuestions(questions) {
    const container = document.getElementById('recentQuestions');
    if (!container) return;

    if (!questions || questions.length === 0) {
        container.innerHTML = '<p class="text-center text-medium" style="padding:20px;">최근 질문이 없습니다.</p>';
        return;
    }

    container.innerHTML = questions.map(q => `
    <div style="padding: 12px; border-bottom: 1px solid var(--border-light);">
      <div class="flex-between mb-xs">
        <span class="text-bold">${q.student}</span>
        <span class="badge badge-purple">${q.subject || '일반'}</span>
      </div>
      <div class="text-sm text-medium mb-xs">${q.question}</div>
      <div class="text-xs text-light">${q.time}</div>
    </div>
  `).join('');
}

function renderPendingGrading(pending) {
    const container = document.getElementById('pendingGrading');
    if (!container) return;

    if (!pending || pending.length === 0) {
        container.innerHTML = '<p class="text-center text-medium" style="padding:20px;">채점 대기 항목이 없습니다.</p>';
        return;
    }

    container.innerHTML = pending.map(p => `
    <div style="padding: 12px; border-bottom: 1px solid var(--border-light);">
      <div class="flex-between mb-xs">
        <span class="text-bold">${p.student}</span>
        <span class="badge badge-warning">${p.subject}</span>
      </div>
      <div class="text-sm text-light">${p.submitted} 제출</div>
    </div>
  `).join('');
}

function renderClassChart(chartData) {
    const ctx = document.getElementById('classChart');
    if (!ctx) return;

    if (!chartData || !chartData.labels) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: '평균 성취도',
                data: chartData.data,
                backgroundColor: '#a88bff',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: '#f0f0f0'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

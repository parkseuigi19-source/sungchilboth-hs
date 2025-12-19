/**
 * 학급 리포트 JavaScript
 */

Utils.checkAuth('teacher');

const username = Utils.getCurrentUser().username;

document.addEventListener('DOMContentLoaded', () => {
    loadReports();
});

async function generateReport() {
    const className = document.getElementById('className').value.trim();
    const subject = document.getElementById('subject').value;
    const reportType = document.getElementById('reportType').value;
    const studentListText = document.getElementById('studentList').value.trim();

    if (!className || !studentListText) {
        Toast.warning('학급명과 학생 목록을 입력해주세요');
        return;
    }

    const studentList = studentListText.split(',').map(s => s.trim()).filter(s => s);

    try {
        Loading.show('리포트를 생성하는 중...');

        const result = await API.post('/api/teacher/class-report/generate', {
            teacher_username: username,
            class_name: className,
            subject,
            report_type: reportType,
            student_list: studentList
        });

        Loading.hide();
        Toast.success('리포트가 생성되었습니다');

        // 폼 초기화
        document.getElementById('className').value = '';
        document.getElementById('studentList').value = '';

        // 목록 새로고침
        loadReports();

    } catch (error) {
        Loading.hide();
        console.error('Report Error:', error);
        Toast.error('리포트 생성에 실패했습니다');
    }
}

async function loadReports() {
    try {
        const response = await API.get(`/api/teacher/class-report/list?teacher_username=${username}`);
        const reports = response.success ? response.data : [];
        renderReports(reports);

    } catch (error) {
        console.error('Load Reports Error:', error);
        document.getElementById('reportList').innerHTML =
            '<tr><td colspan="7" class="text-center text-medium">리포트를 불러올 수 없습니다</td></tr>';
    }
}

function renderReports(reports) {
    const tbody = document.getElementById('reportList');

    if (!reports || reports.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-medium">생성된 리포트가 없습니다</td></tr>';
        return;
    }

    tbody.innerHTML = reports.map(r => `
    <tr>
      <td>${r.class_name}</td>
      <td><span class="badge badge-purple">${r.subject}</span></td>
      <td>${getReportTypeText(r.report_type)}</td>
      <td>${r.total_students}명</td>
      <td><span class="badge ${r.average_score >= 80 ? 'badge-success' : 'badge-warning'}">${r.average_score.toFixed(1)}점</span></td>
      <td>${Utils.formatDate(r.created_at)}</td>
      <td>
        <button class="btn btn-sm btn-primary" onclick="downloadReport(${r.id})">
          📥 다운로드
        </button>
      </td>
    </tr>
  `).join('');
}

function getReportTypeText(type) {
    const types = {
        weekly: '주간',
        monthly: '월간',
        unit: '단원별'
    };
    return types[type] || type;
}

async function downloadReport(reportId) {
    try {
        Loading.show('다운로드 준비 중...');

        // API 호출
        const result = await API.get(`/api/teacher/class-report/download/${reportId}`);

        Loading.hide();

        if (result.success && result.pdf_path) {
            window.open(result.pdf_path, '_blank');
            Toast.success('리포트 다운로드가 시작되었습니다');
        } else {
            Toast.error('생성된 PDF 파일을 찾을 수 없습니다');
        }

    } catch (error) {
        Loading.hide();
        console.error('Download Error:', error);
        Toast.error('다운로드에 실패했습니다');
    }
}

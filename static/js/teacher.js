// static/js/teacher.js
document.addEventListener("DOMContentLoaded", () => {
  const recordTable = document.getElementById("recordTable");
  const refreshBtn = document.getElementById("refreshBtn");

  async function loadRecords() {
    try {
      const res = await fetch("/api/teacher/records");
      if (!res.ok) throw new Error(`서버 응답 오류: ${res.status}`);

      const data = await res.json();
      if (!Array.isArray(data)) throw new Error("데이터 형식이 잘못되었습니다.");

      if (data.length === 0) {
        recordTable.innerHTML = `<tr><td colspan="6" class="empty">아직 등록된 학습 기록이 없습니다.</td></tr>`;
        return;
      }

      recordTable.innerHTML = data.map(r => `
        <tr>
          <td>${r.student_name}</td>
          <td>${r.subject}</td>
          <td>${r.question || "-"}</td>
          <td>${r.score ?? "-"}</td>
          <td>${r.feedback || "-"}</td>
          <td>${r.created_at}</td>
        </tr>
      `).join("");

    } catch (err) {
      console.error(err);
      recordTable.innerHTML = `<tr><td colspan="6" class="empty">⚠️ 데이터를 불러오지 못했습니다.</td></tr>`;
    }
  }

  refreshBtn.addEventListener("click", loadRecords);
  loadRecords(); // 초기 자동 호출
});

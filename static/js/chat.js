const API_BASE = window.location.origin;

document.addEventListener("DOMContentLoaded", () => {
  // 0. 가장 먼저 사용자 이름 업데이트 (우선순위 최상)
  try {
    const studentNameEl = document.getElementById("studentName");
    if (studentNameEl) {
      // 1. Utils 시도
      let name = window.Utils && window.Utils.getCurrentUser().username;

      // 2. Utils 실패 시 직접 localStorage 시도
      if (!name) {
        name = localStorage.getItem("user");
      }

      // 3. 업데이트
      if (name) {
        studentNameEl.innerText = name;
        // console.log("Updated name to:", name);
      }
    }
  } catch (e) {
    console.error("Name update failed:", e);
  }

  const questionInput = document.getElementById("questionInput");
  const askBtn = document.getElementById("askBtn");
  const essayInput = document.getElementById("essayInput");
  const analyzeBtn = document.getElementById("analyzeBtn");

  const questionResult = document.getElementById("questionResult");
  const essayResult = document.getElementById("essayResult");
  const progressCircle = document.getElementById("progressCircle");
  const scoreText = document.getElementById("score");
  const feedbackList = document.getElementById("feedbackList");

  const stdTagQ = document.getElementById("stdTagQ");
  const stdTagA = document.getElementById("stdTagA");
  const tipBox = document.getElementById("teacherTips");

  // Auth/Logout Check
  if (window.Utils) {
    Utils.checkAuth('student');
  }

  // const studentNameEl = document.getElementById("studentName"); // Already defined above
  const logoutBtn = document.getElementById("logoutBtn");

  // (기존 업데이트 로직 제거됨)

  // 로그아웃 이벤트 (HTML inline onclick 사용 권장, 여기서는 보조적으로 유지하거나 제거 가능)
  // HTML에서 onclick="Utils.logout()"을 추가했으므로, JS 리스너는 선택사항입니다.
  // 중복 실행 방지를 위해 제거하거나, 안전망으로 놔둘 수 있습니다. 
  // 여기서는 깔끔하게 기존 로직을 유지하되 디버그 로그만 제거합니다.
  if (logoutBtn) {
    // 기존 리스너 제거 효과를 위해 cloneNode 사용 (선택사항)
    const newLogoutBtn = logoutBtn.cloneNode(true);
    logoutBtn.parentNode.replaceChild(newLogoutBtn, logoutBtn);

    newLogoutBtn.addEventListener("click", () => {
      Utils.logout();
    });
  }

  function username() {
    return Utils.getCurrentUser().username || "학생";
  }

  // ✅ 성취도 원형 그래프
  function updateProgress(score) {
    const radius = 50;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;
    if (progressCircle) progressCircle.style.strokeDashoffset = offset;
    if (scoreText) scoreText.textContent = `${score}%`;
  }

  // ✅ GPT-4o LangChain Agent로 “질문하기”
  askBtn?.addEventListener("click", async () => {
    const q = (questionInput?.value || "").trim();
    if (!q) return alert("질문을 입력해주세요!");

    questionResult.textContent = "🤖 AI가 생각 중이에요...";

    try {
      const res = await fetch(`${API_BASE}/api/agent/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: q, thread_id: username() }),
      });

      if (!res.ok) throw new Error("서버 응답 오류");

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      questionResult.innerHTML = "";

      // ✅ Streaming 출력 (GPT 타이핑 효과)
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter((l) => l.startsWith("data:"));
        for (const line of lines) {
          const data = JSON.parse(line.replace("data: ", ""));
          if (data.token) questionResult.innerHTML += data.token;
          if (data.error)
            questionResult.innerHTML = `<span class="text-red-500">⚠ ${data.error}</span>`;
        }
      }

      if (stdTagQ) stdTagQ.textContent = "📘 GPT-4o LangChain Agent 응답 완료";
    } catch (e) {
      console.error(e);
      questionResult.textContent = "⚠️ AI 응답을 가져오지 못했습니다.";
    }
  });

  // ✅ 서술형 답안 분석 (기존 Analyzer 유지)
  analyzeBtn?.addEventListener("click", async () => {
    const essay = (essayInput?.value || "").trim();
    if (!essay) return alert("답안을 입력해주세요!");

    essayResult.textContent = "🔍 AI가 분석 중입니다...";

    try {
      const res = await fetch(`${API_BASE}/api/student/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username(), essay }),
      });

      if (!res.ok) throw new Error("서버 오류");
      const data = await res.json();

      essayResult.innerHTML = `
        ${data.related_standard ? `<p>📘 <b>관련 성취기준</b>: [${data.related_standard.id}] ${data.related_standard.title}</p>` : ""}
        <p><b>점수</b>: ${data.score ?? "-"}점</p>
        <p><b>피드백</b>: ${data.feedback || "분석 결과 없음"}</p>
      `;

      if (feedbackList)
        feedbackList.innerHTML = `<li>${data.feedback || "AI 피드백 없음"}</li>`;
      if (tipBox && data.teacher_tips)
        tipBox.textContent = data.teacher_tips;

      updateProgress(data.score || 0);
    } catch (e) {
      console.error(e);
      essayResult.textContent = "⚠️ 분석 중 오류가 발생했습니다.";
    }
  });
});

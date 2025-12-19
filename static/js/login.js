const API_URL = "http://127.0.0.1:8000/api/auth";

document.getElementById("loginBtn")?.addEventListener("click", async () => {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await res.json();
  if (data.success) {
    // 로그인 성공 시 사용자 정보를 localStorage에 저장
    localStorage.setItem('user', username);
    localStorage.setItem('role', data.role);

    if (data.role === "teacher") location.href = "/teacher";
    else location.href = "/student";
  } else {
    alert(data.message || "로그인 실패");
  }
});

document.getElementById("registerBtn")?.addEventListener("click", async () => {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const role = document.getElementById("role").value;

  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, role }),
  });

  const data = await res.json();
  if (data.success) {
    alert("회원가입 완료! 로그인 페이지로 이동합니다.");
    location.href = "/login";
  } else {
    alert(data.message || "회원가입 실패");
  }
});

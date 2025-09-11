document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById("loginModal");
    const closeBtn = modal.querySelector(".close");
    const loginBtn = document.querySelector(".login_btn");
    const loginForm = document.getElementById("loginForm");
    const loginError = document.getElementById("loginError");

    function openLoginModal() {
        modal.style.display = "block";
        setTimeout(() => modal.classList.add("show"), 10);
        loginError.style.display = "none"; // 이전 에러 초기화
    }

    function closeLoginModal() {
        modal.classList.remove("show");
        setTimeout(() => modal.style.display = "none", 500);
    }

    closeBtn.onclick = () => closeLoginModal();
    loginBtn.onclick = () => openLoginModal();

    window.onclick = function(event) {
        if (event.target === modal && modal.style.display === "block") {
            closeLoginModal();
        }
    }

    // 로그인 처리
    loginForm.addEventListener("submit", async function(e) {
        e.preventDefault(); // 페이지 이동 방지

        const formData = new FormData(loginForm);

        try {
            const res = await fetch("/login", {
                method: "POST",
                body: formData
            });
            const data = await res.json();

            if (data.success) {
                // ✅ 로그인 성공 시 원하는 페이지로 이동
                window.location.href = "/"; // 메인 페이지로 이동
                // 👉 만약 상품 목록으로 가고 싶으면 "/product" 로 변경
            } else {
                // 실패 시 에러 표시
                loginError.innerText = data.message;
                loginError.style.display = "block";
            }
        } catch (err) {
            loginError.innerText = "서버와 연결할 수 없습니다.";
            loginError.style.display = "block";
        }
    });
});

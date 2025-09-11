document.addEventListener('DOMContentLoaded', () => {
    // ==============================
    // 이메일 자동완성
    // ==============================
    const emailSelect = document.getElementById('email_select');
    const email1 = document.getElementById('email1');
    const email2 = document.getElementById('email2');
    const emailHidden = document.getElementById('email');

    if (emailSelect) {
        emailSelect.addEventListener('change', () => {
            email2.value = emailSelect.value;
        });
    }

    // ==============================
    // 주소찾기
    // ==============================
    const findAddressBtn = document.getElementById('findAddress');
    if (findAddressBtn) {
        findAddressBtn.addEventListener('click', execDaumPostcode);
    }

    function execDaumPostcode() {
        new daum.Postcode({
            oncomplete: function(data) {
                document.getElementById('postcode').value = data.zonecode;
                document.getElementById('address').value = data.roadAddress || data.jibunAddress;
                document.getElementById('address_detail').focus();
            }
        }).open();
    }

    // ==============================
    // 회원가입 폼 유효성 검사
    // ==============================
    const form = document.getElementById('signupForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            // 이메일 합치기
            emailHidden.value = `${email1.value}@${email2.value}`;

            // 이메일 형식 체크
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(emailHidden.value)) {
                alert('유효한 이메일을 입력해주세요.');
                e.preventDefault();
                return false;
            }

            // 비밀번호 확인
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm_password').value;
            if (password !== confirm) {
                alert('비밀번호가 일치하지 않습니다.');
                e.preventDefault();
                return false;
            }

            // 필수 약관 체크
            const agreeTerms = document.getElementById('agree_terms');
            const agreePrivacy = document.getElementById('agree_privacy');
            if (!agreeTerms.checked || !agreePrivacy.checked) {
                alert('필수 약관에 동의해주세요.');
                e.preventDefault();
                return false;
            }

            // 제출 허용
        });
    }
});

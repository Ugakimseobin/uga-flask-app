document.addEventListener('DOMContentLoaded', () => {
    const agreeAll = document.getElementById('agree_all');
    const requiredChecks = document.querySelectorAll('input.agree_required');
    const optionalChecks = document.querySelectorAll('input.agree_optional');
    const termsForm = document.getElementById('termsForm');

    // 전체 동의 클릭
    agreeAll?.addEventListener('click', (e) => {
        const checked = agreeAll.checked;
        requiredChecks.forEach(cb => cb.checked = checked);
        optionalChecks.forEach(cb => cb.checked = checked);
    });

    // 개별 체크 클릭 시 전체 동의 상태 업데이트
    [...requiredChecks, ...optionalChecks].forEach(cb => {
        cb.addEventListener('click', () => {
            const allChecked = [...requiredChecks, ...optionalChecks].every(c => c.checked);
            agreeAll.checked = allChecked;
        });
    });

    // 폼 제출 시 필수 체크 확인
    termsForm?.addEventListener('submit', (e) => {
        const allRequiredChecked = [...requiredChecks].every(cb => cb.checked);
        if (!allRequiredChecked) {
            e.preventDefault(); // 제출 막기
            alert('필수 약관에 모두 동의하셔야 회원가입이 가능합니다.');
            return false;
        }
    });
});

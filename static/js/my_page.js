// 탭 클릭 이벤트
document.querySelectorAll('.menu-item').forEach(item=>{
    item.addEventListener('click', ()=>{
        document.querySelectorAll('.menu-item').forEach(i=>i.classList.remove('active'));
        item.classList.add('active');

        const tab = item.dataset.tab;
        document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
        document.getElementById(tab).classList.add('active');
    });
});

// 기본으로 개인정보 탭 열기
document.querySelector('.menu-item.active').click();

// 장바구니 로드
function loadCart(){
    fetch('/cart_items')
    .then(res=>res.json())
    .then(items=>{
        const list = document.getElementById('cart-items-list-page');
        const totalEl = document.getElementById('cart-total-page');
        list.innerHTML='';
        let total=0;
        items.forEach(item=>{
            total += item.price*item.quantity;
            list.innerHTML += `<li>${item.name} × ${item.quantity}개 (${item.price}원)</li>`;
        });
        totalEl.textContent = total;
    });
}
loadCart();

// 비밀번호 변경 처리
document.getElementById('change-password-form').addEventListener('submit', e=>{
    e.preventDefault();
    const form = e.target;
    const newPwd = form.new_password.value;
    const confirmPwd = form.confirm_password.value;
    if(newPwd !== confirmPwd){
        alert('비밀번호가 일치하지 않습니다.');
        return;
    }
    fetch('/reset_password', {
        method:'POST',
        headers:{'Content-Type':'application/x-www-form-urlencoded'},
        body:`usermail={{ user.email }}&new_password=${newPwd}`
    }).then(res=>{
        alert('비밀번호가 변경되었습니다.');
        form.reset();
    });
});

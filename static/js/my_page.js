// ================== 탭 메뉴 ==================
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

// ================== 장바구니 로드 ==================
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

// ================== 비밀번호 변경 ==================
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

// ================== 배너 업로드 ==================
const bannerForm = document.getElementById('banner-upload-form');
if (bannerForm) {
    bannerForm.addEventListener('submit', e => {
        e.preventDefault();
        const formData = new FormData(bannerForm);
        fetch('/upload_banner', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                const msgEl = document.getElementById('banner-upload-msg');
                msgEl.textContent = data.message;
                msgEl.style.color = data.success ? 'green' : 'red';
                if (data.success) bannerForm.reset();
            }).catch(err => console.error(err));
    });
}

// ================== 프로모션 영상 업로드 ==================
const videoForm = document.getElementById('video-upload-form');
if (videoForm) {
    videoForm.addEventListener('submit', e => {
        e.preventDefault();
        const formData = new FormData(videoForm);
        fetch('/upload_video', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                const msgEl = document.getElementById('video-upload-msg');
                msgEl.textContent = data.message;
                msgEl.style.color = data.success ? 'green' : 'red';
                if (data.success) videoForm.reset();
            }).catch(err => console.error(err));
    });
}

// ================== 장바구니 구매 ==================
const checkoutBtn = document.getElementById('checkout-btn-page');
if(checkoutBtn){
    checkoutBtn.addEventListener('click', async () => {
        const res = await fetch('/cart_items');
        const items = await res.json();

        if(items.length === 0){
            alert('장바구니에 상품이 없습니다.');
            return;
        }

        const checkoutRes = await fetch('/checkout', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({items})
        });

        const data = await checkoutRes.json();

        if(checkoutRes.ok && data.success){
            window.location.href = `/checkout_page?total=${data.total}`;
        } else {
            alert(data.message || '주문 처리 중 오류가 발생했습니다.');
        }
    });
}

// ================== 일반 사용자 주문취소 ==================
document.addEventListener('click', async (e) => {
    if(e.target.classList.contains('btn-cancel-user')){
        if(!confirm('주문을 취소하시겠습니까?')) return;

        const orderId = e.target.dataset.id;
        try {
        //    const res = await fetch(`/order/${orderId}/cancel`, {method:'POST'});
            const res = await fetch(`/user/cancel_order/${orderId}`, {method:'POST'});
            const data = await res.json();
            if(data.success){
                alert('주문이 취소되었습니다.');
                location.reload();
            } else {
                alert(data.message || '취소 중 오류 발생');
            }
        } catch(err){
            console.error(err);
            alert('서버와 통신 중 오류가 발생했습니다.');
        }
    }
});

// ================== 관리자 주문 버튼 ==================
document.addEventListener('click', async e => {
    const btn = e.target;
    if (!btn.classList.contains('btn-ship') && !btn.classList.contains('btn-deliver') && !btn.classList.contains('btn-cancel')) return;

    const orderId = btn.dataset.id;
    let action = '';
    if (btn.classList.contains('btn-ship')) action = 'ship';
    if (btn.classList.contains('btn-deliver')) action = 'deliver';
    if (btn.classList.contains('btn-cancel')) action = 'cancel';
    if (!action) return;

    try {
        const res = await fetch(`/admin/update_order/${orderId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            alert(`주문 상태가 '${data.status}'로 변경되었습니다.`);
            updateOrderRow(orderId, data.status);
            location.reload();
        } else {
            alert(data.message || '주문 처리 중 오류가 발생했습니다.');
        }
    } catch (err) {
        console.error(err);
        alert('서버와 통신 중 오류가 발생했습니다.');
    }
});

// ================== 주문 상태 업데이트 ==================
function updateOrderRow(orderId, newStatus) {
    const row = document.querySelector(`#order-${orderId}`);
    if (!row) return;

    // 상태 텍스트 갱신
    const statusEl = row.querySelector('.order-status');
    if (statusEl) statusEl.textContent = newStatus;

    // 버튼 모두 선택
    const shipBtn = row.querySelector('.btn-ship');
    const deliverBtn = row.querySelector('.btn-deliver');
    const cancelBtn = row.querySelector('.btn-cancel');

    // 상태에 따른 버튼 표시
    if(newStatus === '결제완료') {
        shipBtn?.style.setProperty('display', 'inline-block');
        deliverBtn?.style.setProperty('display', 'none');
        cancelBtn?.style.setProperty('display', 'inline-block');
    } else if(newStatus === '배송중') {
        shipBtn?.style.setProperty('display', 'none');
        deliverBtn?.style.setProperty('display', 'inline-block');
        cancelBtn?.style.setProperty('display', 'none');
    } else if(newStatus === '배송 완료' || newStatus === '취소됨') {
        shipBtn?.style.setProperty('display', 'none');
        deliverBtn?.style.setProperty('display', 'none');
        cancelBtn?.style.setProperty('display', 'none');
    }

    // 배송 시작/완료 시간 표시
    const now = new Date();
    if(newStatus === 'shipped'){
        let shippedEl = row.querySelector('.shipped-time');
        if(!shippedEl){
            shippedEl = document.createElement('p');
            shippedEl.classList.add('shipped-time');
            row.appendChild(shippedEl);
        }
        shippedEl.textContent = `배송 시작: ${now.toLocaleString()}`;
    }
    if(newStatus === 'delivered'){
        let deliveredEl = row.querySelector('.delivered-time');
        if(!deliveredEl){
            deliveredEl = document.createElement('p');
            deliveredEl.classList.add('delivered-time');
            row.appendChild(deliveredEl);
        }
        deliveredEl.textContent = `배송 완료: ${now.toLocaleString()}`;
    }
}
// 주문내역 로드
document.addEventListener("DOMContentLoaded", function() {
    function loadOrders(page = 1) {
        fetch(`/my_page/orders_data?page=${page}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    document.getElementById("order-list").innerHTML = `<li>${data.error}</li>`;
                    return;
                }

                // 주문내역 렌더링
                let html = "";
                data.orders.forEach(order => {
                    html += `<li id="order-${order.id}">
                        <strong>주문번호:</strong> ${order.id} |
                        <strong>총 금액:</strong> ${order.total_price}원 |
                        <strong>상태:</strong> <span class="order-status">${order.status}</span> |
                        <strong>날짜:</strong> ${order.created_at}`;

                    if (order.user) html += ` | <strong>주문자:</strong> ${order.user}`;
                    if (order.notes) html += ` | <strong>메모:</strong> ${order.notes}`;

                    html += `<ul>`;
                    order.items.forEach(item => {
                        html += `<li>${item.name} × ${item.quantity}개 (${item.price}원)`;
                        if (item.image_url) html += `<img src="${item.image_url}" width="50">`;
                        html += `</li>`;
                    });
                    html += `</ul></li>`;
                    // 사용자 취소 버튼
                    if(order.can_cancel && !order.is_admin && (order.status === '결제완료' || order.status === '배송중')){
                        html += `<button class="btn-cancel-user" data-id="${order.id}">주문 취소</button>`;
                    }
                    if(!order.is_admin){
                        html += `<button class="btn-reorder" data-id="${order.id}">카트 담기</button>`;
                    }

                    // 관리자 버튼
                    if(order.is_admin){
                        if(order.can_ship) html += `<button class="btn-ship" data-id="${order.id}">배송 시작</button>`;
                        if(order.can_deliver) html += `<button class="btn-deliver" data-id="${order.id}">배송 완료</button>`;
                        if(order.can_cancel) html += `<button class="btn-cancel" data-id="${order.id}">주문 취소</button>`;
                    }

                    html += `</li>`;
                });
                document.getElementById("order-list").innerHTML = html;

                // 페이지네이션 렌더링
                let pagHtml = "";
                if (data.pagination.has_prev) {
                    pagHtml += `<a href="#" class="page-link" data-page="${data.pagination.page - 1}"><</a>`;
                }

                for (let i = 1; i <= data.pagination.pages; i++) {
                    if (i === data.pagination.page) {
                        pagHtml += `<span class="page-link active">${i}</span>`;
                    } else {
                        pagHtml += `<a href="#" class="page-link" data-page="${i}">${i}</a>`;
                    }
                }

                if (data.pagination.has_next) {
                    pagHtml += `<a href="#" class="page-link" data-page="${data.pagination.page + 1}">></a>`;
                }
                document.getElementById("pagination").innerHTML = pagHtml;

                document.querySelectorAll("#pagination .page-link").forEach(el => {
                    el.addEventListener("click", function(e) {
                        e.preventDefault();
                        loadOrders(this.dataset.page);
                    });
                });
            });
    }

    // 첫 로드
    loadOrders();
    window.loadOrders = loadOrders; // 다른 함수에서도 호출 가능
});

// 클릭 이벤트
document.addEventListener('click', async e => {
    if(e.target.classList.contains('btn-reorder')){
        const orderId = e.target.dataset.id;
        try {
            const res = await fetch(`/reorder/${orderId}`, { method:'POST' });
            const data = await res.json();
            if(data.success){
                alert(data.message);
            } else {
                alert(data.message || '장바구니 추가 실패');
            }
        } catch(err){
            console.error(err);
            alert('서버와 통신 중 오류가 발생했습니다.');
        }
    }
});
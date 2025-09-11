document.addEventListener('DOMContentLoaded', async () => { 
    const checkoutItems = document.getElementById('checkout-items');
    const totalPriceEl = document.getElementById('checkout-total');
    const payBtn = document.getElementById('pay-btn');
    let total = 0;

    async function loadCart() {
        const res = await fetch('/cart_items');
        const items = await res.json();

        checkoutItems.innerHTML = '';
        total = 0;

        if (items.length === 0) {
            checkoutItems.innerHTML = '<p>장바구니에 상품이 없습니다.</p>';
            totalPriceEl.innerText = '0원';
            return;
        }

        items.forEach(item => {
            total += item.price * item.quantity;
            const div = document.createElement('div');
            div.classList.add('checkout-item');
            div.innerHTML = `
                <img src="${item.image}" alt="${item.name}" class="checkout-item-img">
                <div class="checkout-item-info">
                    <p>${item.name}</p>
                    <p>수량 ${item.quantity}개</p>
                </div>
                <p>${item.price * item.quantity}원</p>
            `;
            checkoutItems.appendChild(div);
        });

        totalPriceEl.innerText = total + '원';
    }

    payBtn.addEventListener('click', async () => {
        const res = await fetch('/cart_items');
        const items = await res.json();
        if (items.length === 0) {
            alert('카트에 상품이 없습니다.');
            return;
        }

        const method = document.querySelector('input[name="payment_method"]:checked')?.value || 'card';
        const buyer_addr = document.getElementById("delivery-address").value;

        IMP.init("imp84085058"); // 아임포트 가맹점 식별코드

        const isMobile = /iphone|ipad|ipod|android/i.test(navigator.userAgent);

        IMP.request_pay({
            pg: "kakaopay",
            pay_method: method,
            merchant_uid: "order_" + new Date().getTime(),
            name: "상품 결제",
            amount: total,
            buyer_email: "test@example.com",
            buyer_name: "홍길동",
            buyer_tel: "010-1234-5678",
            buyer_addr: buyer_addr,
            buyer_postcode: "123-456",
            m_redirect_url: window.location.origin + "/order_complete_mobile"
        }, function (rsp) {
            if (rsp.success) {
                if (!isMobile) {
                    // PC: 서버에 결제 검증 후 주문 생성
                    fetch("/pay", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(rsp)
                    })
                    .then(res => res.json())
                    .then(result => {
                        if (result.success) {
                            window.location.href = '/order_complete/' + result.order_id;
                        } else {
                            alert("결제 검증 실패: " + result.message);
                        }
                    });
                }
                // 모바일은 m_redirect_url로 처리되므로 여기서는 끝
            } else {
                alert("결제 실패: " + rsp.error_msg);
            }
        });
    });

    loadCart();
});

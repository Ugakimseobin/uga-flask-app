// =====================
// 수량 +/- 버튼 (메인/상세 모두 사용)
// =====================
document.querySelectorAll('.qty-wrapper').forEach(wrapper => {
    const input = wrapper.querySelector('.product-qty');
    wrapper.querySelector('.minus')?.addEventListener('click', () => {
        if (parseInt(input.value) > 1) input.value = parseInt(input.value) - 1;
    });
    wrapper.querySelector('.plus')?.addEventListener('click', () => {
        input.value = parseInt(input.value) + 1;
    });
});

// =====================
// 카트 추가 함수
// =====================
function addToCart(productId, qty, callback){
    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ product_id: productId, quantity: qty })
    })
    .then(res => res.json())
    .then(data => {
        if(data.success){
            const cartCount = document.querySelector('#cart-count');
            if(cartCount) cartCount.textContent = data.cart_total_items;
            if(callback) callback(); // 성공 시 콜백 실행
        } else {
            alert('카트 추가 실패: ' + (data.message || ''));
        }
    })
    .catch(err => console.error(err));
}

// =====================
// 메인페이지 카트 담기 + 이미지 애니메이션
// =====================
document.querySelectorAll('.add-to-cart').forEach(btn => {
    btn.addEventListener('click', e => {
        e.stopPropagation();
        const card = btn.closest('.product-card');
        const productId = parseInt(btn.dataset.id);
        const qty = parseInt(card.querySelector('.product-qty').value);

        // 이미지 애니메이션
        const img = card.querySelector('img');
        const flyingImg = img.cloneNode(true);
        const rect = img.getBoundingClientRect();
        flyingImg.style.position = 'fixed';
        flyingImg.style.left = rect.left+'px';
        flyingImg.style.top = rect.top+'px';
        flyingImg.style.width = rect.width+'px';
        flyingImg.style.height = rect.height+'px';
        flyingImg.style.transition = 'all 0.8s ease-in-out';
        flyingImg.style.zIndex = 1000;
        document.body.appendChild(flyingImg);

        const cartIcon = document.querySelector('#cart-icon');
        const cartRect = cartIcon.getBoundingClientRect();
        setTimeout(() => {
            flyingImg.style.left = cartRect.left+'px';
            flyingImg.style.top = cartRect.top+'px';
            flyingImg.style.width = '30px';
            flyingImg.style.height = '30px';
            flyingImg.style.opacity = 0.5;
        }, 10);
        flyingImg.addEventListener('transitionend', ()=>flyingImg.remove());

        addToCart(productId, qty);
    });
});

// =====================
// 상세페이지 카트 담기
// =====================
document.getElementById('add-detail-cart')?.addEventListener('click', () => {
    const productId = parseInt(document.getElementById('add-detail-cart').dataset.id);
    const qty = parseInt(document.getElementById('detail-qty').value);

    addToCart(productId, qty, () => {
        // 상품 페이지로 이동
        window.location.href = "/product";
    });
});

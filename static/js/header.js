document.addEventListener('DOMContentLoaded', () => {

    // ----------------------------
    // 햄버거 메뉴
    // ----------------------------
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.querySelector('#header .menu');

    // 햄버거 클릭 → 메뉴 토글 + X 아이콘
    hamburger?.addEventListener('click', () => {
        if(window.innerWidth <= 992){
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
        }
    });

    // 모바일 아코디언 드롭다운
    document.querySelectorAll('.menu li.dropdown > a').forEach(toggle => {
        toggle.addEventListener('click', e => {
            if(window.innerWidth <= 992){
                e.preventDefault();
                const dropdown = toggle.nextElementSibling;
                dropdown.classList.toggle('show');
            }
        });
    });

    // =====================
    // 드롭다운 (데스크탑 클릭)
    // =====================
    const dropdownToggles = document.querySelectorAll('.menu li.dropdown > a');

    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const parentLi = toggle.parentElement;
            const dropdown = toggle.nextElementSibling;

            // 다른 드롭다운은 닫기
            document.querySelectorAll('.menu li.dropdown .dropdown-menu').forEach(menu => {
                if(menu !== dropdown) menu.classList.remove('show');
            });

            // 현재 드롭다운 토글
            dropdown.classList.toggle('show');
        });
    });

    // 외부 클릭 시 닫기
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
        }
    });

    // 윈도우 리사이즈 시 초기화
    window.addEventListener('resize', () => {
        if(window.innerWidth > 992){
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
            document.querySelectorAll('.menu li .dropdown-menu').forEach(menu => menu.classList.remove('show'));
            document.querySelectorAll('.menu li .dropdown-menu .category').forEach(cat => cat.classList.remove('active'));
        }
    });

    // ----------------------------
    // 사용자 메뉴 (로그인 후)
    // ----------------------------
    const userToggle = document.getElementById('userMenuToggle');
    const userMenu = document.getElementById('userDropdownMenu');
    userToggle?.addEventListener('click', function(e) {
        e.preventDefault();
        userMenu.classList.toggle('show');
    });

    // ----------------------------
    // 더보기 메뉴
    // ----------------------------
    const moreMenuButton = document.getElementById('moreMenu');
    const moreMenuModal = document.getElementById('moreMenuModal');
    if (moreMenuButton && moreMenuModal) {
        const closeMoreMenuBtn = moreMenuModal.querySelector('.close');
        function openMoreMenu() {
            moreMenuModal.style.display = "block";
            setTimeout(() => moreMenuModal.classList.add("show"), 10);
        }
        function closeMoreMenu() {
            moreMenuModal.classList.remove("show");
            setTimeout(() => moreMenuModal.style.display = "none", 500);
        }
        moreMenuButton.addEventListener('click', openMoreMenu);
        closeMoreMenuBtn.addEventListener('click', closeMoreMenu);
        window.addEventListener('click', function(event) {
            if (event.target === moreMenuModal) closeMoreMenu();
        });
    }

    // ----------------------------
    // 외부 클릭 시 메뉴 닫기
    // ----------------------------
    document.addEventListener('click', function(event) {
        if (userMenu && !userMenu.contains(event.target) && !userToggle.contains(event.target)) {
            userMenu.classList.remove('show');
        }
    });

    // ----------------------------
    // 카트 드롭다운
    // ----------------------------
    const cartBtn = document.getElementById('cartBtn');
    const cartDropdown = document.getElementById('cartDropdown');

    cartBtn?.addEventListener('click', () => {
        cartDropdown.style.display = cartDropdown.style.display === 'none' ? 'block' : 'none';
        loadCartItems();
    });

    async function loadCartItems() {
        const response = await fetch('/cart_items');
        const data = await response.json();
        const cartList = document.getElementById('cart-items-list');
        cartList.innerHTML = '';
        let total = 0;

        if (data.length === 0) {
            cartList.innerHTML = '<li>카트가 비어있습니다.</li>';
        } else {
            data.forEach(item => {
                total += item.price * item.quantity;
                const li = document.createElement('li');
                li.classList.add('cart-item');
                li.innerHTML = `
                    <div class="cart-item-info">
                        <span class="name">${item.name}</span>
                        <span class="price">${item.price}원</span>
                    </div>
                    <input type="number" min="1" value="${item.quantity}" data-id="${item.cart_id}" class="cart-qty">
                    <button data-id="${item.cart_id}" class="remove-cart">삭제</button>
                `;
                cartList.appendChild(li);
            });
        }

        document.getElementById('cart-count').innerText = data.length;
        document.getElementById('cart-total').innerText = total;

        // 수량 변경 이벤트
        document.querySelectorAll('.cart-qty').forEach(input => {
            input.addEventListener('change', async (e) => {
                const cartId = e.target.dataset.id;
                await fetch(`/update_cart/${cartId}`, {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({quantity: parseInt(e.target.value)})
                });
                loadCartItems();
                updateHeaderCart();
            });
        });

        // 삭제 버튼 이벤트
        document.querySelectorAll('.remove-cart').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const cartId = e.target.dataset.id;
                await fetch(`/remove_cart/${cartId}`, {method:'POST'});
                await loadCartItems();
                updateHeaderCart();
            });
        });
    }

    async function updateHeaderCart() {
        const res = await fetch('/cart_items');
        const data = await res.json();
        document.getElementById('cart-count').innerText = data.length;
    }

    // ----------------------------
    // 상품 카드 이벤트
    // ----------------------------
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('click', e => {
            if (['add-to-cart','qty-btn','product-qty'].some(c => e.target.classList.contains(c))) return;
            const detailUrl = card.dataset.detailUrl;
            if(e.target.tagName === 'IMG' && detailUrl) window.location.href = detailUrl;
        });
    });

    // ----------------------------
    // 상품 카트 담기
    // ----------------------------
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const productId = btn.dataset.id;
            const qtyInput = document.querySelector(`.product-qty[data-id="${productId}"]`);
            const quantity = parseInt(qtyInput.value);
            await fetch('/add_cart', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({product_id: productId, quantity})
            });
            updateHeaderCart();
            loadCartItems();
        });
    });

    // 상세페이지 카트
    const detailBtn = document.getElementById('add-detail-cart');
    if(detailBtn){
        detailBtn.addEventListener('click', async (e)=>{
            e.preventDefault();
            const productId = detailBtn.dataset.id;
            const quantity = parseInt(document.getElementById('detail-qty').value);
            await fetch('/add_cart', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({product_id: productId, quantity})
            });
            alert('장바구니에 추가되었습니다!');
            updateHeaderCart();
            loadCartItems();
        });
    }

    // 체크아웃
    document.getElementById('checkout-btn')?.addEventListener('click', (e) => {
        e.preventDefault();

        // 서버에서 장바구니 가져오기
        fetch('/cart_items')
            .then(res => res.json())
            .then(items => {
                if (items.length === 0) {
                    alert('카트에 상품이 없습니다.');
                    return;
                }
                // ✅ 단순히 checkout 페이지로 이동
                window.location.href = '/checkout_page';
            })
            .catch(err => {
                console.error(err);
                alert('서버와 통신 중 오류가 발생했습니다.');
            });
    });

    // 초기 카트 갱신
    updateHeaderCart();
});

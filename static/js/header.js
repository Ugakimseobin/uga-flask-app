document.addEventListener('DOMContentLoaded', () => {
    // 햄버거 메뉴
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.querySelector('#header .menu');
    hamburger?.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        hamburger.classList.toggle('active');
    });

    // 사용자 메뉴
    const userToggle = document.getElementById('userMenuToggle');
    const userMenu = document.getElementById('userDropdownMenu');
    userToggle?.addEventListener('click', e => {
        e.preventDefault();
        userMenu.classList.toggle('show');
    });

    document.addEventListener('click', e => {
        if(userMenu && !userMenu.contains(e.target) && !userToggle.contains(e.target)) {
            userMenu.classList.remove('show');
        }
    });

    // 상품/카테고리/제품 영역
    const productLeft = document.getElementById('product-left');
    const productRight = document.getElementById('product-right');

    // 더미 카테고리/서브카테고리 로드 (DB에서 fetch 나중에)
    const categories = [
        {id:1,name:'카테고리1', subs:[{id:11,name:'항목1-1'},{id:12,name:'항목1-2'}]},
        {id:2,name:'카테고리2', subs:[{id:21,name:'항목2-1'},{id:22,name:'항목2-2'}]}
    ];

    function renderCategories() {
        productLeft.innerHTML = '';
        const ul = document.createElement('ul');
        categories.forEach(cat=>{
            const li = document.createElement('li');
            li.textContent = cat.name;
            li.dataset.id = cat.id;
            li.addEventListener('click', ()=>renderSubcategories(cat));
            ul.appendChild(li);
        });
        productLeft.appendChild(ul);
    }

    function renderSubcategories(cat) {
        productLeft.innerHTML = '';
        const backBtn = document.createElement('li');
        backBtn.textContent = '← 카테고리로 돌아가기: '+cat.name;
        backBtn.style.fontWeight = 'bold';
        backBtn.addEventListener('click', ()=>renderCategories());
        productLeft.appendChild(backBtn);

        const ul = document.createElement('ul');
        cat.subs.forEach(sub=>{
            const li = document.createElement('li');
            li.textContent = sub.name;
            li.dataset.id = sub.id;
            li.addEventListener('click', ()=>renderProducts(sub));
            ul.appendChild(li);
        });
        productLeft.appendChild(ul);
    }

    function renderProducts(sub) {
        productRight.style.display = 'block';
        productRight.innerHTML = `<h3>${sub.name} 제품 리스트</h3>`;
        // 여기에 DB fetch 해서 제품 리스트 넣기
        const ul = document.createElement('ul');
        for(let i=1;i<=3;i++){
            const li = document.createElement('li');
            li.textContent = `${sub.name} 제품 ${i}`;
            ul.appendChild(li);
        }
        productRight.appendChild(ul);
    }

    renderCategories();
});

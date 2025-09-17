// order_complete.js

// 예를 들어, 주문 완료 페이지에서 애니메이션 효과 추가
document.addEventListener('DOMContentLoaded', () => {
    const orderCard = document.querySelector('.order-card');
    if(orderCard){
        orderCard.style.opacity = 0;
        orderCard.style.transform = "translateY(20px)";
        setTimeout(() => {
            orderCard.style.transition = "all 0.5s ease";
            orderCard.style.opacity = 1;
            orderCard.style.transform = "translateY(0)";
        }, 100);
    }
});

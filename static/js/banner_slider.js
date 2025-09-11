document.addEventListener('DOMContentLoaded', function() {
    let currentIndex = 0;
    const slides = document.querySelectorAll(".slide");
    const dots = document.querySelectorAll(".dot");
    let slideInterval = null;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove("active");
            if (i === index) slide.classList.add("active");
        });
        dots.forEach((dot, i) => {
            dot.classList.remove("active");
            if (i === index) dot.classList.add("active");
        });
        currentIndex = index;
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        showSlide(currentIndex);
    }

    function startSlide() {
        if (slideInterval) clearInterval(slideInterval);
        slideInterval = setInterval(nextSlide, 3000);
    }

    function stopSlide() {
        if (slideInterval) {
            clearInterval(slideInterval);
            slideInterval = null;
        }
    }

    // 인디케이터 클릭
    window.goToSlide = function(index) {
        showSlide(index);
        startSlide(); // 클릭 시 interval 초기화
    }

    // 마우스 오버 시 정지
    const slider = document.querySelector(".slider");
    slider.addEventListener("mouseenter", stopSlide);
    slider.addEventListener("mouseleave", startSlide);

    showSlide(currentIndex);
    startSlide();

    // 윈도우 리사이즈 시 이미지 높이 자동 조정
    window.addEventListener('resize', () => {
        slides.forEach(slide => {
            slide.style.height = `${slider.offsetWidth * 0.4}px`; // padding-top 비율과 맞춤
        });
    });

    // 초기 높이 설정
    slides.forEach(slide => {
        slide.style.height = `${slider.offsetWidth * 0.4}px`;
    });
});
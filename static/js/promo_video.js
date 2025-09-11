// 영상 모달 열기
function openVideoModal(videoId, videoUrl) {
    const modal = document.getElementById('videoModal');
    const content = document.getElementById('modalContent');

    if (videoUrl && videoUrl.includes("youtube.com")) {
        const embedUrl = videoUrl.replace("watch?v=", "embed/");
        content.innerHTML = `
            <span class="close" onclick="closeVideoModal()">&times;</span>
            <iframe width="80%" height="80%" src="${embedUrl}" frameborder="0" allowfullscreen></iframe>
        `;
    } else {
        content.innerHTML = `
            <span class="close" onclick="closeVideoModal()">&times;</span>
            <video width="80%" height="80%" controls autoplay>
                <source src="/promo_video/${videoId}" type="video/mp4">
            </video>
        `;
    }

    modal.style.display = 'flex';
}

// 영상 모달 닫기
function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    const content = document.getElementById('modalContent');
    content.innerHTML = '<span class="close" onclick="closeVideoModal()">&times;</span>';
    modal.style.display = 'none';
}

// 모달 외부 클릭 시 닫기
window.addEventListener('click', function(e){
    const modal = document.getElementById('videoModal');
    if (e.target === modal) {
        closeVideoModal();
    }
});

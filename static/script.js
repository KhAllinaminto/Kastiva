document.addEventListener('DOMContentLoaded', function() {
    const videoUrlInput = document.getElementById('video-url');
    const goBtn = document.getElementById('go-btn');
    const options = document.getElementById('options');
    const downloadBtn = document.getElementById('download-btn');
    const messageDiv = document.getElementById('message');
    const progressBar = document.querySelector('.progress');
    const progressBarInner = document.querySelector('.progress-bar');

    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = `alert alert-${type} ${text ? '' : 'd-none'}`;
    }

    function validateYoutubeUrl(url) {
        return url.includes('youtube.com/watch?v=') || 
               url.includes('youtu.be/') || 
               url.includes('youtube.com/shorts/');
    }

    function updateProgress(percent) {
        progressBarInner.style.width = `${percent}%`;
        progressBarInner.setAttribute('aria-valuenow', percent);
    }

    function toggleOptions(show) {
        if (show) {
            options.classList.remove('d-none');
            setTimeout(() => options.classList.add('show'), 10);
        } else {
            options.classList.remove('show');
            options.classList.add('d-none');
        }
    }

    function toggleProgressBar(show) {
        if (show) {
            progressBar.classList.remove('d-none');
            setTimeout(() => progressBar.classList.add('show'), 10);
        } else {
            progressBar.classList.remove('show');
            progressBar.classList.add('d-none');
        }
    }

    // Hide progress bar and options initially
    toggleProgressBar(false);
    toggleOptions(false);

    goBtn.addEventListener('click', function() {
        const videoUrl = videoUrlInput.value.trim();

        if (!videoUrl) {
            showMessage("الرجاء إدخال رابط الفيديو", "danger");
            toggleOptions(false);
            return;
        }

        if (!validateYoutubeUrl(videoUrl)) {
            showMessage("الرجاء إدخال رابط يوتيوب صحيح", "danger");
            toggleOptions(false);
            return;
        }

        showMessage("", "");
        toggleOptions(true);
    });

    downloadBtn.addEventListener('click', async function() {
        const videoUrl = videoUrlInput.value.trim();
        const format = document.getElementById('format').value;
        const quality = document.getElementById('quality').value;

        downloadBtn.disabled = true;
        showMessage("جاري تحميل الفيديو...", "info");
        toggleProgressBar(true);
        updateProgress(10);

        try {
            const response = await fetch(`/download?url=${encodeURIComponent(videoUrl)}&format=${format}&quality=${quality}`);

            if (!response.ok) {
                const errorData = await response.json();
                if (response.status === 403) {
                    throw new Error("هذا الفيديو يتطلب تسجيل الدخول إلى يوتيوب");
                }
                throw new Error(errorData.error || "حدث خطأ أثناء التحميل");
            }

            updateProgress(50);
            const blob = await response.blob();
            updateProgress(75);

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `video.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            updateProgress(100);
            showMessage("تم التحميل بنجاح!", "success");
        } catch (error) {
            console.error('Download error:', error);
            showMessage(error.message, "danger");
        } finally {
            downloadBtn.disabled = false;
            setTimeout(() => {
                toggleProgressBar(false);
                updateProgress(0);
            }, 3000);
        }
    });
});
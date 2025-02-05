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
        messageDiv.className = `alert alert-${type} show`;
        messageDiv.style.display = text ? 'block' : 'none';
    }

    function validateYoutubeUrl(url) {
        const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]{11}$/;
        return pattern.test(url);
    }

    function showProgress(show) {
        progressBar.style.display = show ? 'block' : 'none';
        if (show) {
            progressBarInner.style.width = '0%';
        }
    }

    function updateProgress(percent) {
        progressBarInner.style.width = `${percent}%`;
        progressBarInner.setAttribute('aria-valuenow', percent);
    }

    goBtn.addEventListener('click', function() {
        const videoUrl = videoUrlInput.value.trim();

        if (!videoUrl) {
            showMessage("الرجاء إدخال رابط الفيديو", "danger");
            return;
        }

        if (!validateYoutubeUrl(videoUrl)) {
            showMessage("الرجاء إدخال رابط يوتيوب صحيح", "danger");
            return;
        }

        options.style.display = 'block';
        showMessage("", "");
    });

    downloadBtn.addEventListener('click', async function() {
        const videoUrl = videoUrlInput.value.trim();
        const format = document.getElementById('format').value;
        const quality = document.getElementById('quality').value;

        if (!videoUrl) {
            showMessage("الرجاء إدخال رابط الفيديو", "danger");
            return;
        }

        downloadBtn.disabled = true;
        showMessage("جاري تحميل الفيديو...", "info");
        showProgress(true);
        updateProgress(10);

        try {
            const response = await fetch(`/download?url=${encodeURIComponent(videoUrl)}&format=${format}&quality=${quality}`);

            if (!response.ok) {
                const errorData = await response.json();
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
            showMessage(error.message, "danger");
        } finally {
            downloadBtn.disabled = false;
            setTimeout(() => {
                showProgress(false);
            }, 3000);
        }
    });
});
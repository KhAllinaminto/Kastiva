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
        messageDiv.className = `alert alert-${type} mt-3`;
        messageDiv.classList.remove('d-none');
        if (!text) {
            messageDiv.classList.add('d-none');
        }
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

    function showOptions() {
        // Remove d-none and invisible classes
        options.classList.remove('d-none', 'invisible');
        // Force a reflow to ensure transition works
        void options.offsetWidth;
        // Add show class for animation
        options.classList.add('show');
        console.log('Options shown:', options.className); // Debug log
    }

    function hideOptions() {
        options.classList.remove('show');
        options.classList.add('invisible');
        console.log('Options hidden:', options.className); // Debug log
    }

    function toggleProgressBar(show) {
        if (show) {
            progressBar.classList.remove('d-none');
        } else {
            progressBar.classList.add('d-none');
            updateProgress(0);
        }
    }

    // Hide progress bar initially
    toggleProgressBar(false);

    goBtn.addEventListener('click', function() {
        const videoUrl = videoUrlInput.value.trim();
        console.log('Go button clicked, URL:', videoUrl); // Debug log

        if (!videoUrl) {
            showMessage("الرجاء إدخال رابط الفيديو", "danger");
            hideOptions();
            return;
        }

        if (!validateYoutubeUrl(videoUrl)) {
            showMessage("الرجاء إدخال رابط يوتيوب صحيح", "danger");
            hideOptions();
            return;
        }

        showMessage("", "");
        showOptions();
        console.log('Options should be visible now'); // Debug log
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
            }, 3000);
        }
    });
});
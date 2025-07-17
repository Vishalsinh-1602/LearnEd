// Track lesson completion
document.querySelectorAll('.lesson-complete-btn').forEach(button => {
    button.addEventListener('click', function() {
        const lessonId = this.dataset.lessonId;
        const courseId = this.dataset.courseId;
        const isCompleted = this.classList.contains('btn-success');
        
        fetch('/api/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lesson_id: lessonId,
                course_id: courseId,
                completed: !isCompleted
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (isCompleted) {
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-secondary');
                    this.textContent = 'Mark Complete';
                } else {
                    this.classList.remove('btn-outline-secondary');
                    this.classList.add('btn-success');
                    this.textContent = 'Completed';
                }
                
                // Update progress bar if exists
                const progressBar = document.querySelector('.course-progress-bar');
                if (progressBar) {
                    progressBar.style.width = `${data.course_progress}%`;
                    progressBar.textContent = `${data.course_progress}%`;
                }
            }
        });
    });
});

// Video player controls
document.querySelectorAll('.video-player').forEach(player => {
    const video = player.querySelector('video');
    const playBtn = player.querySelector('.play-btn');
    const progressBar = player.querySelector('.progress-bar');
    
    playBtn.addEventListener('click', function() {
        if (video.paused) {
            video.play();
            this.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            video.pause();
            this.innerHTML = '<i class="fas fa-play"></i>';
        }
    });
    
    video.addEventListener('timeupdate', function() {
        const percent = (video.currentTime / video.duration) * 100;
        progressBar.style.width = `${percent}%`;
    });
    
    video.addEventListener('ended', function() {
        playBtn.innerHTML = '<i class="fas fa-play"></i>';
    });
});
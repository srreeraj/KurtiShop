(function () {
    class HeroCarousel {
        constructor(trackId) {
            this.track = document.getElementById(trackId);
            if (!this.track) return;

            this.slides = this.track.children.length;
            this.current = 0;
            this.autoplayMs = 5000;
            this.timer = null;

            this.dots = document.querySelectorAll('.hero-dot');
            this.prevBtn = document.getElementById('hero-prev');
            this.nextBtn = document.getElementById('hero-next');
            this.section = document.getElementById('hero-section');

            this.bindEvents();
            this.startAutoplay();
        }

        update() {
            this.track.style.transform = `translateX(-${this.current * 100}%)`;
            this.dots.forEach((dot, i) => {
                const active = i === this.current;
                dot.classList.toggle('bg-red-600', active);
                dot.classList.toggle('w-6', active);
                dot.classList.toggle('sm:w-8', active);
                dot.classList.toggle('bg-white/50', !active);
                dot.classList.toggle('w-2', !active);
            });
        }

        move(dir) {
            this.current = (this.current + dir + this.slides) % this.slides;
            this.update();
            this.resetAutoplay();
        }

        goTo(index) {
            this.current = index;
            this.update();
            this.resetAutoplay();
        }

        startAutoplay() {
            this.timer = setInterval(() => this.move(1), this.autoplayMs);
        }

        resetAutoplay() {
            clearInterval(this.timer);
            this.startAutoplay();
        }

        bindEvents() {
            this.prevBtn?.addEventListener('click', () => this.move(-1));
            this.nextBtn?.addEventListener('click', () => this.move(1));
            this.dots.forEach(dot => {
                dot.addEventListener('click', () => this.goTo(Number(dot.dataset.index)));
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') this.move(-1);
                if (e.key === 'ArrowRight') this.move(1);
            });

            let startX = 0;
            this.track.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
            this.track.addEventListener('touchend', (e) => {
                const diff = startX - e.changedTouches[0].clientX;
                if (Math.abs(diff) > 50) this.move(diff > 0 ? 1 : -1);
            }, { passive: true });

            this.section?.addEventListener('mouseenter', () => clearInterval(this.timer));
            this.section?.addEventListener('mouseleave', () => this.startAutoplay());
        }
    }

    document.addEventListener('DOMContentLoaded', () => new HeroCarousel('hero-carousel-track'));
})();
/* ============================================
   DounIA — Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

    /* ---- Navbar scroll effect ---- */
    const navbar = document.querySelector('.navbar-dounia');
    window.addEventListener('scroll', function () {
        if (window.scrollY > 50) {
            navbar.classList.add('shadow-sm');
        } else {
            navbar.classList.remove('shadow-sm');
        }
    });

    /* ---- Smooth scroll for anchor links ---- */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
                // Close mobile navbar
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, { toggle: true });
                }
            }
        });
    });

    /* ---- Fade-in-up on scroll (Intersection Observer) ---- */
    const fadeElements = document.querySelectorAll('.fade-in-up');
    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -60px 0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    fadeElements.forEach(el => observer.observe(el));

    /* ---- Counter animation ---- */
    const counters = document.querySelectorAll('.counter');
    const counterObserver = new IntersectionObserver(function (entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const suffix = counter.getAttribute('data-suffix') || '';
                const duration = 2000;
                const steps = 60;
                const increment = target / steps;
                let current = 0;
                const interval = duration / steps;

                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        counter.textContent = target + suffix;
                        clearInterval(timer);
                    } else {
                        counter.textContent = Math.floor(current) + suffix;
                    }
                }, interval);

                counterObserver.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(c => counterObserver.observe(c));

    /* ---- Atelier card → form pre-fill ---- */
    document.querySelectorAll('.btn-atelier-inscription').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const atelierValue = this.getAttribute('data-atelier');
            const formSection = document.getElementById('inscription');
            const atelierSelect = document.getElementById('id_atelier');

            if (atelierSelect && atelierValue) {
                atelierSelect.value = atelierValue;
                // Trigger change event for any listeners
                atelierSelect.dispatchEvent(new Event('change'));
            }

            if (formSection) {
                formSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    /* ---- Character counter for motivation textarea ---- */
    const motivationField = document.getElementById('id_motivation');
    if (motivationField) {
        const maxLength = 500;
        const counterDiv = document.createElement('div');
        counterDiv.className = 'text-muted small mt-1';
        counterDiv.id = 'motivation-counter';
        counterDiv.textContent = `0 / ${maxLength} caractères`;
        motivationField.parentNode.appendChild(counterDiv);

        motivationField.addEventListener('input', function () {
            const len = this.value.length;
            counterDiv.textContent = `${len} / ${maxLength} caractères`;
            if (len > maxLength * 0.9) {
                counterDiv.classList.add('text-warning');
                counterDiv.classList.remove('text-danger', 'text-muted');
            }
            if (len >= maxLength) {
                counterDiv.classList.add('text-danger');
                counterDiv.classList.remove('text-warning', 'text-muted');
            }
            if (len < maxLength * 0.9) {
                counterDiv.classList.add('text-muted');
                counterDiv.classList.remove('text-warning', 'text-danger');
            }
        });
    }

    /* ---- Active nav link highlight ---- */
    const sections = document.querySelectorAll('section[id]');
    window.addEventListener('scroll', function () {
        let scrollPos = window.scrollY + 120;
        sections.forEach(section => {
            const top = section.offsetTop;
            const height = section.offsetHeight;
            const id = section.getAttribute('id');
            const navLink = document.querySelector(`.nav-link[href="#${id}"]`);
            if (navLink) {
                if (scrollPos >= top && scrollPos < top + height) {
                    navLink.classList.add('active');
                } else {
                    navLink.classList.remove('active');
                }
            }
        });
    });

});

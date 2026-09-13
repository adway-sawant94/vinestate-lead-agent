document.addEventListener('DOMContentLoaded', () => {

    // ==========================================================================
    // INITIALIZE LUCIDE ICONS
    // ==========================================================================
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // ==========================================================================
    // MOBILE NAVIGATION DRAWER
    // ==========================================================================
    const menuToggle = document.getElementById('menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const body = document.body;

    function toggleMenu() {
        const isOpen = menuToggle.classList.contains('active');
        if (isOpen) {
            menuToggle.classList.remove('active');
            mobileMenu.classList.remove('active');
            body.style.overflow = '';
            menuToggle.setAttribute('aria-expanded', 'false');
        } else {
            menuToggle.classList.add('active');
            mobileMenu.classList.add('active');
            body.style.overflow = 'hidden'; // Prevent scrolling when menu is open
            menuToggle.setAttribute('aria-expanded', 'true');
        }
    }

    menuToggle.addEventListener('click', toggleMenu);

    // Close menu when clicking a link
    const mobileLinks = document.querySelectorAll('.mobile-nav-item, .mobile-cta-btn');
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            menuToggle.classList.remove('active');
            mobileMenu.classList.remove('active');
            body.style.overflow = '';
            menuToggle.setAttribute('aria-expanded', 'false');
        });
    });

    // ==========================================================================
    // STICKY NAVBAR BACKGROUND
    // ==========================================================================
    const navbar = document.getElementById('navbar');

    function checkScroll() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }

    window.addEventListener('scroll', checkScroll);
    checkScroll(); // Trigger check initially on load

    // ==========================================================================
    // SMOOTH SCROLL FOR ANCHOR LINKS
    // ==========================================================================
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                const headerHeight = navbar.classList.contains('scrolled') ? 70 : 90;
                const offsetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ==========================================================================
    // TABS SWITCHER FOR SIGNATURE PACKAGES
    // ==========================================================================
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            
            // Set active state on button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Show corresponding panel and hide others
            tabPanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === `tab-${tabName}`) {
                    panel.classList.add('active');
                }
            });
        });
    });

    // ==========================================================================
    // INTERSECTION OBSERVER FOR SCROLL FADE-IN
    // ==========================================================================
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const fadeObserverOptions = {
        root: null,
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px' // Trigger slightly before element enters viewport
    };

    const fadeObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Stop tracking once animated in
            }
        });
    }, fadeObserverOptions);

    fadeElements.forEach(el => {
        fadeObserver.observe(el);
    });

    // ==========================================================================
    // INTERACTIVE FORM SUBMISSION (WEB3FORMS AJAX)
    // ==========================================================================
    const form = document.getElementById('discovery-form');
    const formResult = document.getElementById('form-result');

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const accessKeyInput = form.querySelector('input[name="access_key"]');
            
            // Check if Access Key has been set
            if (!accessKeyInput || accessKeyInput.value === 'YOUR_ACCESS_KEY_HERE' || accessKeyInput.value.trim() === '') {
                formResult.innerHTML = "<strong>Notice:</strong> Please configure a valid Web3Forms Access Key in index.html to submit this form.";
                formResult.className = "form-result-message error";
                return;
            }

            formResult.innerHTML = "Sending request. Please wait...";
            formResult.className = "form-result-message";
            formResult.style.display = "block";

            const formData = new FormData(form);
            const object = Object.fromEntries(formData);
            const json = JSON.stringify(object);

            fetch('https://api.web3forms.com/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: json
            })
            .then(async (response) => {
                let jsonRes = await response.json();
                if (response.status === 200) {
                    formResult.innerHTML = "<strong>Success!</strong> Your request has been sent. Our team will contact you shortly.";
                    formResult.className = "form-result-message success";
                    form.reset();
                } else {
                    console.error("Web3Forms response error:", jsonRes);
                    formResult.innerHTML = jsonRes.message || "An error occurred. Please try again later.";
                    formResult.className = "form-result-message error";
                }
            })
            .catch(error => {
                console.error("Network error during form submission:", error);
                formResult.innerHTML = "Failed to connect. Please check your internet connection and try again.";
                formResult.className = "form-result-message error";
            });
        });
    }
});


/* =========================================================
   HARISH E-COMMERCE - 3D INTERACTION ENGINE
   File: static/js/3d.js
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    if (reduceMotion) return;

    const hero = document.querySelector(".hero");
    const heroVisual = document.querySelector(".hero-visual");

    /* -----------------------------------------------------
       1. HERO 3D MOUSE PARALLAX
    ----------------------------------------------------- */

    if (hero && heroVisual) {
        let frameRequested = false;
        let mouseX = 0;
        let mouseY = 0;

        hero.addEventListener("mousemove", (event) => {
            const rect = hero.getBoundingClientRect();

            mouseX = (
                (event.clientX - rect.left) / rect.width - 0.5
            );

            mouseY = (
                (event.clientY - rect.top) / rect.height - 0.5
            );

            if (!frameRequested) {
                frameRequested = true;

                requestAnimationFrame(() => {
                    heroVisual.style.transform = `
                        perspective(1200px)
                        rotateY(${mouseX * 10}deg)
                        rotateX(${-mouseY * 8}deg)
                        translate3d(${mouseX * 12}px, ${mouseY * 12}px, 0)
                    `;

                    frameRequested = false;
                });
            }
        });

        hero.addEventListener("mouseleave", () => {
            heroVisual.style.transform =
                "perspective(1200px) rotateX(0deg) rotateY(0deg)";
        });
    }

    /* -----------------------------------------------------
       2. FLOATING HERO ELEMENTS
    ----------------------------------------------------- */

    const floatingElements = document.querySelectorAll(
        ".hero-product, .hero-orbit, .floating-element"
    );

    floatingElements.forEach((element, index) => {
        const duration = 3 + (index % 4) * 0.6;

        element.animate(
            [
                {
                    transform: "translateY(0px) rotate(0deg)"
                },
                {
                    transform: "translateY(-15px) rotate(3deg)"
                },
                {
                    transform: "translateY(0px) rotate(0deg)"
                }
            ],
            {
                duration: duration * 1000,
                iterations: Infinity,
                easing: "ease-in-out",
                delay: index * 180
            }
        );
    });

    /* -----------------------------------------------------
       3. HERO GLOW FOLLOW EFFECT
    ----------------------------------------------------- */

    if (hero) {
        hero.addEventListener("mousemove", (event) => {
            const rect = hero.getBoundingClientRect();

            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            hero.style.setProperty("--mouse-x", `${x}px`);
            hero.style.setProperty("--mouse-y", `${y}px`);
        });
    }

    /* -----------------------------------------------------
       4. 3D PRODUCT CARD TILT
    ----------------------------------------------------- */

    const cards = document.querySelectorAll(
        ".product-card, .category-card"
    );

    cards.forEach((card) => {
        card.addEventListener("mousemove", (event) => {
            const rect = card.getBoundingClientRect();

            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;

            card.style.transform = `
                perspective(900px)
                rotateX(${rotateX}deg)
                rotateY(${rotateY}deg)
                translateY(-5px)
            `;

            card.style.setProperty(
                "--card-mouse-x",
                `${x}px`
            );

            card.style.setProperty(
                "--card-mouse-y",
                `${y}px`
            );
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "";
        });
    });

    /* -----------------------------------------------------
       5. SCROLL PARALLAX
    ----------------------------------------------------- */

    const parallaxElements = document.querySelectorAll(
        "[data-parallax]"
    );

    let scrollFrame = false;

    function updateParallax() {
        const scrollPosition = window.scrollY;

        parallaxElements.forEach((element) => {
            const speed = parseFloat(
                element.dataset.parallax || "0.15"
            );

            const movement = scrollPosition * speed;

            element.style.transform =
                `translate3d(0, ${movement}px, 0)`;
        });

        scrollFrame = false;
    }

    window.addEventListener(
        "scroll",
        () => {
            if (!scrollFrame) {
                requestAnimationFrame(updateParallax);
                scrollFrame = true;
            }
        },
        { passive: true }
    );

    /* -----------------------------------------------------
       6. GSAP SCROLL ANIMATIONS
    ----------------------------------------------------- */

    if (window.gsap && window.ScrollTrigger) {
        gsap.registerPlugin(ScrollTrigger);

        gsap.utils.toArray(".reveal").forEach((element) => {
            gsap.fromTo(
                element,
                {
                    opacity: 0,
                    y: 45
                },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.9,
                    ease: "power3.out",
                    scrollTrigger: {
                        trigger: element,
                        start: "top 88%",
                        once: true
                    }
                }
            );
        });

        gsap.utils.toArray(".hero-orbit").forEach((element) => {
            gsap.to(element, {
                rotation: 360,
                duration: 24,
                repeat: -1,
                ease: "none",
                transformOrigin: "center center"
            });
        });
    }

    /* -----------------------------------------------------
       7. BUTTON LIGHT EFFECT
    ----------------------------------------------------- */

    document.querySelectorAll(".btn").forEach((button) => {
        button.addEventListener("mousemove", (event) => {
            const rect = button.getBoundingClientRect();

            button.style.setProperty(
                "--button-x",
                `${event.clientX - rect.left}px`
            );

            button.style.setProperty(
                "--button-y",
                `${event.clientY - rect.top}px`
            );
        });
    });

    /* -----------------------------------------------------
       8. IMAGE 3D HOVER
    ----------------------------------------------------- */

    document.querySelectorAll(
        ".product-detail-image, .hero-visual img"
    ).forEach((image) => {
        image.addEventListener("mousemove", (event) => {
            const rect = image.getBoundingClientRect();

            const x = (event.clientX - rect.left) / rect.width;
            const y = (event.clientY - rect.top) / rect.height;

            image.style.transform = `
                scale(1.04)
                rotateX(${(0.5 - y) * 6}deg)
                rotateY(${(x - 0.5) * 6}deg)
            `;
        });

        image.addEventListener("mouseleave", () => {
            image.style.transform = "";
        });
    });

    console.log("HARISH 3D interaction engine loaded successfully.");
});

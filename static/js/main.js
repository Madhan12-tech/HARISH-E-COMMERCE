
/* =====================================================
   HARISH E-COMMERCE - MAIN JAVASCRIPT
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ================================================
       MOBILE NAVIGATION
    ================================================ */

    const menuButton = document.querySelector(".mobile-menu-button");
    const navigation = document.querySelector(".main-navigation");

    if (menuButton && navigation) {

        menuButton.addEventListener("click", function () {

            navigation.classList.toggle("active");

            const isOpen = navigation.classList.contains("active");

            menuButton.setAttribute("aria-expanded", isOpen);
            menuButton.innerHTML = isOpen ? "✕" : "☰";

        });

        navigation.querySelectorAll("a").forEach(function (link) {

            link.addEventListener("click", function () {

                navigation.classList.remove("active");
                menuButton.innerHTML = "☰";
                menuButton.setAttribute("aria-expanded", "false");

            });

        });

    }


    /* ================================================
       HEADER SCROLL EFFECT
    ================================================ */

    const header = document.querySelector(".site-header");

    function updateHeader() {

        if (!header) return;

        if (window.scrollY > 50) {
            header.classList.add("scrolled");
        } else {
            header.classList.remove("scrolled");
        }

    }

    window.addEventListener("scroll", updateHeader);
    updateHeader();


    /* ================================================
       BACK TO TOP
    ================================================ */

    const backToTop = document.querySelector(".back-to-top");

    if (backToTop) {

        window.addEventListener("scroll", function () {

            if (window.scrollY > 400) {
                backToTop.classList.add("visible");
            } else {
                backToTop.classList.remove("visible");
            }

        });

        backToTop.addEventListener("click", function () {

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        });

    }


    /* ================================================
       SCROLL REVEAL ANIMATIONS
    ================================================ */

    const revealElements = document.querySelectorAll(
        ".reveal, .category-card, .product-card, .trust-item"
    );

    if ("IntersectionObserver" in window) {

        const revealObserver = new IntersectionObserver(function (entries) {

            entries.forEach(function (entry) {

                if (entry.isIntersecting) {

                    entry.target.classList.add("active");

                    revealObserver.unobserve(entry.target);

                }

            });

        }, {
            threshold: 0.12
        });

        revealElements.forEach(function (element) {

            element.classList.add("reveal");
            revealObserver.observe(element);

        });

    } else {

        revealElements.forEach(function (element) {
            element.classList.add("active");
        });

    }


    /* ================================================
       PRODUCT CARD TILT EFFECT
    ================================================ */

    const productCards = document.querySelectorAll(".product-card");

    productCards.forEach(function (card) {

        card.addEventListener("mousemove", function (event) {

            if (window.innerWidth < 900) return;

            const rect = card.getBoundingClientRect();

            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -4;
            const rotateY = ((x - centerX) / centerX) * 4;

            card.style.transform =
                `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;

        });

        card.addEventListener("mouseleave", function () {

            card.style.transform = "";

        });

    });


    /* ================================================
       FLASH MESSAGE AUTO DISMISS
    ================================================ */

    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.transition = "opacity .4s, transform .4s";
            message.style.opacity = "0";
            message.style.transform = "translateX(20px)";

            setTimeout(function () {
                message.remove();
            }, 450);

        }, 4500);

    });


    /* ================================================
       PRODUCT IMAGE HOVER
    ================================================ */

    document.querySelectorAll(".product-image img").forEach(function (image) {

        image.addEventListener("error", function () {

            image.style.display = "none";

        });

    });


    /* ================================================
       QUANTITY INPUT VALIDATION
    ================================================ */

    document.querySelectorAll('input[name="quantity"]').forEach(function (input) {

        input.addEventListener("change", function () {

            const min = Number(input.min || 1);
            const max = Number(input.max || 9999);
            let value = Number(input.value);

            if (!Number.isFinite(value)) {
                value = min;
            }

            value = Math.max(min, Math.min(max, value));

            input.value = value;

        });

    });


    /* ================================================
       SMOOTH SCROLL FOR PAGE ANCHORS
    ================================================ */

    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {

        anchor.addEventListener("click", function (event) {

            const targetId = anchor.getAttribute("href");

            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);

            if (target) {

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }

        });

    });


    /* ================================================
       BUTTON CLICK ANIMATION
    ================================================ */

    document.querySelectorAll("button, .primary-btn").forEach(function (button) {

        button.addEventListener("pointerdown", function () {

            button.style.transform = "scale(.97)";

        });

        button.addEventListener("pointerup", function () {

            button.style.transform = "";

        });

        button.addEventListener("pointerleave", function () {

            button.style.transform = "";

        });

    });


    /* ================================================
       CURRENT YEAR
    ================================================ */

    document.querySelectorAll("[data-current-year]").forEach(function (element) {

        element.textContent = new Date().getFullYear();

    });


    console.log("HARISH website JavaScript loaded successfully.");

});

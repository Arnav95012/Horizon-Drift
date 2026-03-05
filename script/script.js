// Intersection Observer for Scroll Animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        // If the element is visible in the viewport
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
        }
    });
});

// Grab all elements with the 'hidden' class
const hiddenElements = document.querySelectorAll('.hidden');

// Tell the observer to watch them
hiddenElements.forEach((el) => observer.observe(el));

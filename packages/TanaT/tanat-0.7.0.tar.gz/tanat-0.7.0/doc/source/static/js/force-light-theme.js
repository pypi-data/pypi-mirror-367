/* Force Light Theme - JavaScript */

// Force the light theme as soon as possible
(function() {
    'use strict';
    
    // Force the data-theme attribute on the html element
    function forceLightTheme() {
        const html = document.documentElement;
        html.setAttribute('data-theme', 'light');
        html.setAttribute('data-mode', 'light');
        html.setAttribute('data-default-mode', 'light');
        
        // Remove the dark class if it exists
        html.classList.remove('dark');
        html.classList.add('light');
        
        // Force in localStorage to avoid auto-detection
        try {
            localStorage.setItem('mode', 'light');
            localStorage.setItem('theme', 'light');
            localStorage.setItem('pst-color-scheme', 'light');
        } catch (e) {
            // Ignore localStorage errors
        }
    }
    
    // Execute immediately
    forceLightTheme();
    
    // Execute when the DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceLightTheme);
    } else {
        forceLightTheme();
    }
    
    // Observe attribute changes to correct them
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && 
                (mutation.attributeName === 'data-theme' || 
                 mutation.attributeName === 'data-mode')) {
                const html = document.documentElement;
                if (html.getAttribute('data-theme') !== 'light') {
                    forceLightTheme();
                }
            }
        });
    });
    
    // Start observing
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme', 'data-mode', 'class']
    });
    
})();


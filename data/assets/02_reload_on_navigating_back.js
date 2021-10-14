// Reload the page on navigating Back - to ensure that presented data is up to date with cache
window.onbeforeunload = function() {
    location.reload();
}

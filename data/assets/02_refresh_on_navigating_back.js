/* Refresh the page on navigating the history back - to ensure that presented data is up to date with cache */

window.onbeforeunload = function() {
    location.reload();
}

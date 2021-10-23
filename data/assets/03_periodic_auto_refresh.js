/* Refresh the page periodically if so requested by user */

var pageAutoRefreshTimeout

// Dash client-side function to call when auto-refresh check box is clicked
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        auto_refresh : function(selected_checkbox_string) {
            enabled = selected_checkbox_string != "";
            if (enabled) {
                intervalSeconds = getAutoRefreshIntervalSeconds();
                pageAutoRefreshTimeout = setTimeout(pageAutoRefresh, intervalSeconds * 1000);
            } else {
                clearTimeout(pageAutoRefreshTimeout);
            }
            return enabled.toString();
        }
    }
});

function getAutoRefreshIntervalSeconds() {
    var domAutoRefreshElement = document.getElementById("auto-refresh-interval-seconds")
    if (domAutoRefreshElement) {
        let seconds=domAutoRefreshElement.title;
        return parseFloat(seconds);
    } else {
        console.error("auto-refresh-interval-seconds html tag not found")
        return 0.0;
    }
}

function pageAutoRefresh() {
    location.reload();
}

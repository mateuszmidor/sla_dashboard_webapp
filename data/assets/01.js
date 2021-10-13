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

// getDataTimestamp returns test results timestamp from domDateTimeElement's title
function getDataTimestamp(domDateTimeElement) {
    const isoDateTimeStr =  domDateTimeElement.title;
    if (isoDateTimeStr == "") {
        return "<unknown>"
    }
    return new Date(isoDateTimeStr).toLocaleString();
}

// setTimestampsToLocalTime sets the test data timestamp low and high values
function setTimestampsToLocalTime() {
    var domTimestampLowElement = document.getElementById('timestamp-low');
    var domTimestampHighElement = document.getElementById('timestamp-high');
    if (domTimestampLowElement && domTimestampHighElement) {
        const serverDataTimestampLow = getDataTimestamp(domTimestampLowElement);
        domTimestampLowElement.textContent = serverDataTimestampLow
        const serverDataTimestampHigh= getDataTimestamp(domTimestampHighElement);
        domTimestampHighElement.textContent = serverDataTimestampHigh
        return
    }
    setTimeout(setTimestampsToLocalTime, 100)
}

setTimeout(setTimestampsToLocalTime, 100)

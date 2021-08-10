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
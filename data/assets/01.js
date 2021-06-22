// data stale warning mechanism
function checkTimeInterval() {
    const domTimeElement = document.getElementById('current-timestamp');
    const domDiffWarningElement = document.getElementById('timeinterval');
    if (domTimeElement) {
        const elementTime =  domTimeElement.title;
        const serverData = new Date(elementTime);
        const dateNow = new Date();
        const diff = (dateNow.getTime() - serverData.getTime()) / 1000; //JS RETURN SECOUND IN MS
        const diffWarning = domDiffWarningElement.innerText;
        const warningElement = document.getElementsByClassName('header-time-warning');
        if(warningElement[0]) {
            if(diff > parseInt(diffWarning)) {
                warningElement[0].className = 'header-time-warning header-time-warning-visible';
            } else{
               warningElement[0].className = 'header-time-warning';
            }
        }
    }
    setTimeout(checkTimeInterval, 100);
}

setTimeout(checkTimeInterval, 100);

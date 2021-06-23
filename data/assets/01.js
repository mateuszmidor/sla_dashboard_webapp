// checkIfServerDataIsStale makes header-stale-data-warning visible if server data is stale.
function checkIfServerDataIsStale() {
    const domTimeElement = document.getElementById('current-timestamp');
    const domDiffWarningElement = document.getElementById('timeinterval');
    if (domTimeElement) {
        const elementTime =  domTimeElement.title;
        const serverData = new Date(elementTime);
        const dateNow = new Date();
        const dataAgeSeconds = (dateNow.getTime() - serverData.getTime()) / 1000; 
        const allowedDataAgeSeconds = domDiffWarningElement.innerText;
        const warningElement = document.getElementsByClassName('header-stale-data-warning');
        if(warningElement[0]) {
            if(dataAgeSeconds > parseInt(allowedDataAgeSeconds)) {
                warningElement[0].className = 'header-stale-data-warning header-stale-data-warning-visible';
            } else{
               warningElement[0].className = 'header-stale-data-warning';
            }
        }
    }
    setTimeout(checkIfServerDataIsStale, 100);
}

setTimeout(checkIfServerDataIsStale, 100);

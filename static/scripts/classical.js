


const bodyElement = document.getElementsByTagName('body')



function startTimer () {
    console.log('started');
    if (timer !== null) {
        clearInterval(timer);
    }
    showTimer();
}

function endTimer() {
    clearInterval(timer);
}

function showTimer () {
    timer = setInterval(() => {
        let hr, min, sec
        diff=diff+10;
        hr = parseInt(diff/1000/60/60);
        hr = hr < 10 ? '0' + hr : hr;

        // minute derived from the difference
        min = parseInt(diff/1000/60);
        if (min > 59) {min %= 60};
        min = min < 10 ? '0' + min : min;
        
        // second derived from the difference
        sec = parseInt(diff/1000);
        if (sec > 59) {sec %= 60};
        sec = sec < 10 ? '0' + sec : sec;

        $('.clock').text(`${hr}:${min}:${sec}`);
    }, 10);
}

$('document').ready(() => {
    timer = null;
    bodyElement.onload = startTimer()
    $('#pause').on('click', function () {
        console.log(diff);
        // pause the time
        endTimer();
        console.log(timer);
        $('.box > img').prop('draggable', false);
        $(this).prop('disabled', true);
        $('#play').prop('disabled', false);
    });
    
    $('#play').on('click', function () {
        // console.log(start);
        // // calculates the time when game was paused
        // start = start + (new Date().getTime() - (diff + start));
        // console.log(start)
        showTimer();
        $('.box img').prop('draggable', true);
        $(this).prop('disabled', true);
        $('#pause').prop('disabled', false); 
    });
})

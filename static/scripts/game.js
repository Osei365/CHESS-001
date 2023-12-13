const default_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
const fen_list = [default_fen];
const move_list = [];
const san_list = [];
const forwardPos = [];
let diff = null;
let timer = null;
let gameover;
let boxes;
let bodyEl;
let playerTimeEl;
let oppTimeEl;
let opponentTime;
let playerTime;





function dragStart (e) {
    e.dataTransfer.setData('text/plain', e.target.id);
    // setTimeout(() => {
    //     e.target.classList.add('hide');
    //     console.log('dragstart');
    // }, 10);
    // e.target.classList.add('hide');
    
}



function dragEnter (e) {
    e.preventDefault();
    if (e.target.tagName === 'IMG') {
        let parent = e.target.parentElement;
        parent.classList.add('drag-over');
    }
    else {
        e.target.classList.add('drag-over');
    }
}

function dragOver (e) {
    e.preventDefault();
    if (e.target.tagName === 'IMG') {
        let parent = e.target.parentElement;
        parent.classList.add('drag-over');
    }
    else {
        e.target.classList.add('drag-over');
    }
    
}

function dragLeave (e) {
    if (e.target.tagName === 'IMG') {
        let parent = e.target.parentElement;
        parent.classList.remove('drag-over');
    }
    else {
        e.target.classList.remove('drag-over');
    }
    
}

function drop (e) {
    // e.preventDefault();

    const id = e.dataTransfer.getData('text/plain');
    if (e.target.tagName === 'IMG') {
        e.target.parentElement.classList.remove('drag-over')
        new_id = e.target.parentElement.id;
    }
    else {
        e.target.classList.remove('drag-over');
        new_id = e.target.id;
    }
    
    const draggable = document.getElementById(id);
    const parent = draggable.parentElement;
    console.log(parent.id+new_id);

    $.ajax({
        type: 'POST',
        url: 'http://127.0.0.1:5000/play',
        data: JSON.stringify({'move': parent.id+new_id, 'fen': fen_list[fen_list.length - 1]}),
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            console.log(data['answer']);
            if (data['answer'] === 'true') {
                if (parent.id+new_id === 'e1h1' && data['san'] === 'O-O') {
                    new_id = 'g1';
                }
                else if (parent.id+new_id === 'e1a1' && data['san'] === 'O-O-O') {
                    new_id = 'c1'
                }
                const to = document.getElementById(new_id);

                if (to.childNodes.length === 0 || to.firstChild.classList.contains('hide')) {
                    forwardPos.push('empty');
                } else if (!to.firstChild.classList.contains('hide')) {
                    forwardPos.push('notEmpty');
                    to.firstChild.classList.add('hide');
                }
                to.insertBefore(draggable, to.firstChild);

                // adding a glow to the position that a piece got moved to
                boxes.forEach((element) => {
                    element.classList.remove('glow');
                })
                console.log(to.classList);
                to.classList.add('glow');
                parent.classList.add('glow');
                

                // handling the castling move in chess
                if (bodyEl.classList.contains('b')) {
                    castlingBlack (parent.id+new_id, data); 
                } else {
                    castlingWhite (parent.id+new_id, data);      
                }

                if (playerTimeEl !== null &&  oppTimeEl !== null) {
                    console.log('blitz')
                    if (timer !== null) {
                        clearInterval(timer);
                    }
                    oppTimer();
                }
                // adding the san notation for each move after the move 
                // has been made
                $('.san-move').append(`<div>${data['san']}</div>`);

                // updating the status of the game (who to move?)
                $('whotomove').text('BLACK TO MOVE')

                // makes background red when opponent's king is on check
                let king;
                if (bodyEl.classList.contains('b')) {
                    king = document.getElementById('wK');
                } else {
                    king = document.getElementById('bK');
                }
                const host = king.parentElement;
                if (data['ischeck'] === true) {
                    host.classList.add('danger');
                } else {
                    boxes.forEach((element) => {
                        if (element.classList.contains('danger')) {
                            element.classList.remove('danger')
                        }
                    })
                }
                console.log(data['ischeckmate']);
                if (data['ischeckmate']) {
                    clearInterval(timer);
                    gameover.classList.remove('hide');
                    // $('.check-mate').css('display', 'block');
                }
                console.log(move_list);
                fen_list.push(data['fen']);
                console.log(fen_list);

                setTimeout('', 100000);
                computerPlayer(data['fen']);
            }
            
        }
    });
    draggable.classList.remove('hide');
}

function undo () {
    boxes.forEach((element) => {
        element.classList.remove('glow');
    });
    if (move_list.length >= 1) {
        
        const str = move_list[move_list.length - 1];
        // const drop_string = str.substring(0, 2);
        // const drag_string = str.substring(2, 4);
        if (str.length === 8) {
            const castling1 = document.getElementById(str.substring(4, 6));
            const castling2 = document.getElementById(str.substring(6, 8));
            castling1.insertBefore(castling2.firstChild, castling1.firstChild);
            if (castling2.childNodes.length > 0) {
                castling2.firstChild.classList.remove('hide');
            }
        }
        console.log(str);
        const element1 = document.getElementById(str.substring(0, 2));
        const element2 = document.getElementById(str.substring(2, 4));
        element1.insertBefore(element2.firstChild, element1.firstChild);
        if (forwardPos[forwardPos.length - 1] === 'notEmpty') {
            element2.firstChild.classList.remove('hide');
        }
        move_list.pop();
        forwardPos.pop();
        fen_list.pop();
        $('.san-move').children().last().remove();
        console.log(fen_list);   
    }
}

window.setInterval(function () {
    $(".san-move").animate({ 
        scrollTop: $( 
            '.san-move').prop('scrollHeight')
        }, 2000);
}, 5000)

function reset_chess () {
    const l = move_list.length;
    for (let i = 1; i <= l; i++) {
        undo();
    }
    startTimer();
}

function computerPlayer (fen) {
    $.ajax({
        type: 'POST',
        url: 'http://127.0.0.1:5000/computer',
        data: JSON.stringify({'fen': fen}),
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            console.log(data['move']);
            const str = data['move'];
            // const drop_string = str.substring(0, 2);
            // const drag_string = str.substring(2, 4);

            const element1 = document.getElementById(str.substring(0, 2));
            const element2 = document.getElementById(str.substring(2, 4));

            
            if (element2.childNodes.length === 0 || element2.firstChild.classList.contains('hide')) {
                element2.insertBefore(element1.firstChild, element2.firstChild);
                forwardPos.push('empty');
            }
            else {
                element2.firstChild.classList.add('hide')
                element2.insertBefore(element1.firstChild, element2.firstChild)
                forwardPos.push('notEmpty');
            }

            // making the present move to glow
            boxes.forEach((element) => {
                element.classList.remove('glow');
            });
            element2.classList.add('glow');
            element1.classList.add('glow');
            

            if (bodyEl.classList.contains('b')) {
                castlingWhite (str, data); 
            } else {
                castlingBlack (str, data);      
            }

            if (playerTimeEl !== null && oppTimeEl !== null) {
                console.log('blitz timer')
                if (timer !== null) {
                    clearInterval(timer);
                }
                
                playerTimer();
            }
            $('.san-move').append(`<div>${data['san']}</div>`);
            $('whotomove').text('WHITE TO MOVE')
            

            // makes background red when opponent's king is on check
            let king;
            if (bodyEl.classList.contains('b')) {
                king = document.getElementById('bK');
            } else {
                king = document.getElementById('wK');
            }
            const host = king.parentElement;
            if (data['ischeck'] === true) {
                host.classList.add('danger');

            } else {
                boxes.forEach((element) => {
                    if (element.classList.contains('danger')) {
                        element.classList.remove('danger')
                    }
                })
            }
            console.log(data['ischeckmate']);
            if (data['ischeckmate']) {
                clearInterval(timer);
                gameover.classList.remove('hide');
                // $('.check-mate').css('display', 'block');
            }
            console.log(move_list);
            fen_list.push(data['fen']);

        }
    });
}

function castlingWhite (str, data) {
    if (str === 'e1g1' && data['san'] === 'O-O') {
        console.log(data['san']);
        const h1 = document.getElementById('h1');
        const f1 = document.getElementById('f1');
        f1.insertBefore(h1.firstChild, f1.firstChild);
        move_list.push(str+'h1f1');
    } else if (str === 'e1c1' && data['san'] === 'O-O-O') {
        console.log(data['san']);
        const a1 = document.getElementById('a1');
        const d1 = document.getElementById('d1');
        d1.insertBefore(a1.firstChild, d1.firstChild);
        move_list.push(str+'a1d1');
    } else {
        move_list.push(str);
    }
}

function castlingBlack (str, data) {
    if (str === 'e8g8' && data['san'] === 'O-O') {
        console.log(data['san']);
        const h8 = document.getElementById('h8');
        const f8 = document.getElementById('f8');
        f8.insertBefore(h8.firstChild, f8.firstChild);
        move_list.push(str+'h8f8');
    } else if (str === 'e8c8' && data['san'] === 'O-O-O') {
        console.log(data['san']);
        const a8 = document.getElementById('a8');
        const d8 = document.getElementById('d8');
        d8.insertBefore(a8.firstChild, d8.firstChild);
        move_list.push(str+'a8d8');
    } else {
        move_list.push(str);
    }
}

function playerTimer () {

    timer = setInterval(() => {
        let min = Math.floor(playerTime / 60); 
        let sec = playerTime % 60;

        min = min < 10? '0' + min : min;
        sec = sec < 10? '0' + sec : sec;

        playerTimeEl.innerHTML = `${min}:${sec}`;

        if (playerTime === 0) {
            clearInterval(timer);
            $('.time-up').removeClass('hide');
        }

        playerTime = playerTime - 1;
    }, 1000)
    
}

function oppTimer () {

    timer = setInterval(() => {
        let min = Math.floor(opponentTime / 60); 
        let sec = opponentTime % 60;

        min = min < 10? '0' + min : min;
        sec = sec < 10? '0' + sec : sec;

        oppTimeEl.innerHTML = `${min}:${sec}`;

        if (opponentTime === 0) {
            clearInterval(timer);
            $('.time-up').removeClass('hide');
            window.stop();
        }

        opponentTime = opponentTime - 1;
    }, 1000)
    
}

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
    bodyEl = document.querySelector('body');

    boxes = document.querySelectorAll('.box');
    gameover = document.querySelector('.check-mate');
    gameover.classList.add('hide');

    oppTimeEl = document.getElementById('blitz-clock1');
    playerTimeEl = document.getElementById('blitz-clock2');

    opponentTime= 5 * 60;
    playerTime = 5 * 60;

    if (bodyEl.classList.contains('classical')) {
        bodyEl.onload = startTimer();
    } else {
        $('.time-up').addClass('hide');
        playerTimeEl.innerHTML = `05:00`;
        oppTimeEl.innerHTML = `05:00`;
        if (bodyEl.classList.contains('b')) {
            oppTimer();
        } else {
            playerTimer();
        }
    }

    


    boxes.forEach(element => {
        element.addEventListener('dragenter', dragEnter);
        element.addEventListener('dragover', dragOver);
        element.addEventListener('dragleave', dragLeave);
        element.addEventListener('drop', drop)
    });
    $('#whotomove').text('WHITE TO MOVE');
    

    $('#undo').on('click', function () {
        // undos both the player and computer move
        undo();
        undo();
    });

    $('#reset').on('click', function () {
        // resets the entire game
        console.log('reset');
        reset_chess();
        endTimer();
        window.stop();
        diff = 0;
        if (bodyEl.classList.contains('classical')) {
            startTimer();
        } else {
            playerTimeEl.innerHTML = `05:00`;
            oppTimeEl.innerHTML = `05:00`;
            playerTime = 5 * 60;
            opponentTime = 5 * 60;

            if (bodyEl.classList.contains('b')) {
                oppTimer();
                computerPlayer(default_fen);
            } else {
                playerTimer();
            }
        }
        
        $('#pause').prop('disabled', false);
        $('#play').prop('disabled', true);
    });

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

    $('#hint').on('click', () => {
        $.ajax({
            type: 'POST',
            url: 'http://127.0.0.1:5000/hint',
            data: JSON.stringify({'fen': fen_list[fen_list.length - 1]}),
            dataType: 'json',
            contentType: 'application/json',
            success: function (data) {
                const str = data['move'];

                const el1 = document.getElementById(str.substring(0, 2));
                const el2 = document.getElementById(str.substring(2, 4));

                boxes.forEach((element) => {
                    element.classList.remove('glow');
                });

                el2.classList.add('glow');
                el1.classList.add('glow');
            }
        })
    });

    if (playerTimeEl.innerHTML === '00:00' || oppTimeEl.innerHTML === '00:00') {
        clearInterval(timer);
        $('.time-up').removeClass('hide');
    }
});
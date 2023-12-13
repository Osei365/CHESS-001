import chess
import chess.engine
from time import sleep
from random import randint
from flask import (
    Flask, 
    render_template, 
    request, 
    jsonify, 
    redirect,
    url_for)

app = Flask(__name__)
engine= ""

engine_dict = {
    'stockfish' : r"stockfish\stockfish-windows-x86-64.exe",
    'komodo' : r"komodo3-64-win\komodo3-64.exe"
}

@app.route('/', strict_slashes=False)
def index():
    return render_template('main.html')

@app.route('/chess/<gs>/<start>/', strict_slashes=False)
def chess_game(gs, start):
    global engine
    if engine == "":
        return redirect('http://127.0.0.1:5000/')
    
    org = []
    for i in range(8, 0, -1):
        val = i * 8
        for n in range(8, 0, -1):
            org.append(chess.SQUARE_NAMES[val - n])

    if start == 'b':
        org = chess.SQUARE_NAMES
    squares=[]
    print(chess.SQUARE_NAMES)
    for pos in range(len(chess.SQUARE_NAMES)):
        row = []
        row.append(org[pos])
        if pos // 8 == 0 or pos // 8 == 2 or pos // 8 == 4 or pos // 8 == 6:
            if pos % 2 == 0:
                row.append('even')
            else:
                row.append('odd')
        elif pos // 8 == 1 or pos // 8 == 3 or pos // 8 == 5 or pos // 8 == 7:
            if pos % 2 == 0:
                row.append('odd')
            else:
                row.append('even')
        squares.append(row)
    pawn_white = ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2']
    pawn_black = ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7']
    opponent = engine.id['name']
    print(squares)
    
    return render_template(
        'chess.html', 
        squares=squares, 
        pwhite=pawn_white, 
        pblack=pawn_black,
        opponent=opponent,
        start=start,
        game_style=gs
        )

@app.route('/play', methods=['POST'], strict_slashes=False)
def play_game():
    dic = request.get_json()
    if dic['move'][0:2] == dic['move'][2:4]:
        return jsonify({'answer': 'false'})
    board = chess.Board(dic['fen'])
    move = chess.Move.from_uci(dic['move'])
    result = {'fen': board.fen()}
    if move in board.legal_moves:
        result['answer'] = 'true'
        result['san'] = str(board.san(move))
        board.push(move)
        result['status'] = board.turn
        result['ischeck'] = board.is_check()
        result['ischeckmate'] = board.is_checkmate()
        result['fen'] = board.fen()
        
    else:
        result['answer'] = 'false'
    return jsonify(result)

@app.route('/computer', methods=['POST'], strict_slashes=False)
def computer():
    if engine == "":
        return redirect('http://127.0.0.1:5000/')
    dic = request.get_json()
    board = chess.Board(dic['fen'])
    result = engine.play(board, chess.engine.Limit(time=0.1))
    new_dic = {'move': str(result.move)}
    new_dic['san'] = str(board.san(result.move))
    print(result.move)
    board.push(result.move)
    print(board)
    new_dic['status'] = board.turn
    new_dic['ischeck'] = board.is_check()
    new_dic['ischeckmate'] = board.is_checkmate()
    new_dic['fen'] = board.fen()

    sleep(randint(4, 9))
    
    return jsonify(new_dic)

@app.route('/hint', methods=['POST'], strict_slashes=False)
def get_hint():
    dic = request.get_json()
    board = chess.Board(dic['fen'])
    result = engine.play(board, chess.engine.Limit(time=0.1))
    new_dic = {'move': str(result.move)}

    return jsonify(new_dic)



@app.route('/init', methods=['POST'], strict_slashes=False)
def initiliaze():
    dic = request.form

    # check if all required values are selected
    if 'blitz' not in dic.keys() or 'comp_engine' not in dic.keys():
        print(request.form)

    #get the global engine variable
    global engine

    # set the engine to the one selected
    engine = chess.engine.SimpleEngine.popen_uci(engine_dict[str(dic.get('comp_engine'))])

    # get key values for the style of game
    game_style = dic.get('chess-style')

    # get the side to start
    starter = dic.get('whotostart')
    if starter == None:
        starter = 'w'
    return redirect('http://127.0.0.1:5000/chess/{}/{}/'.format(game_style, starter))


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
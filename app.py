import chess
import chess.engine
from flask import (
    Flask, 
    render_template, 
    request, 
    jsonify, 
    redirect)

app = Flask(__name__)
engine= ""

engine_dict = {
    'stockfish' : r"C:\Users\owner\CHESS-001\stockfish\stockfish-windows-x86-64.exe",
    'komodo' : r"C:\Users\owner\CHESS-001\komodo3-64-win\komodo3-64.exe"
}

@app.route('/', strict_slashes=False)
def index():
    return render_template('main.html')

@app.route('/chess', strict_slashes=False)
def chess_game():
    global engine
    if engine == "":
        return redirect('http://127.0.0.1:5000/')
    org = []
    for i in range(8, 0, -1):
        val = i * 8
        for n in range(8, 0, -1):
            org.append(chess.SQUARE_NAMES[val - n])
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
        opponent=opponent
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
    
    return jsonify(new_dic)

@app.route('/init', methods=['POST'], strict_slashes=False)
def initiliaze():
    print(request.form.get('comp_engine'))

    #get the global engine variable
    global engine

    # set the engine to the one selected
    engine = chess.engine.SimpleEngine.popen_uci(engine_dict[str(request.form.get('comp_engine'))])
    print(engine.id)
    return redirect('http://127.0.0.1:5000/chess')


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
import chess
import chess.engine
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
engine= chess.engine.SimpleEngine.popen_uci(r"C:\Users\user\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")

@app.route('/', strict_slashes=False)
def index():
    org = []
    for i in range(8, 0, -1):
        val = i * 8
        for n in range(8, 0, -1):
            org.append(chess.SQUARE_NAMES[val - n])
    squares=[]
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
    
    return render_template('index.html', squares=squares, pwhite=pawn_white, pblack=pawn_black)

@app.route('/play', methods=['POST'], strict_slashes=False)
def play_game():
    dic = request.get_json()
    if dic['fen'] != '':
        board = chess.Board(dic['fen'])
    else:
        board = chess.Board()
    move = chess.Move.from_uci(dic['move'])
    result = {'fen': board.fen()}
    if move in board.legal_moves:
        result['answer'] = 'true'
        result['san'] = str(board.san(move))
        board.push(move)
        print(board)
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
    board.push(result.move)
    new_dic['fen'] = board.fen()
    
    return jsonify(new_dic)


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
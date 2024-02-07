import os
import chess
import chess.engine
import requests
import json
import models
from time import sleep
from random import randint
from flask import (
    Flask, render_template, 
    request, jsonify, 
    redirect, url_for
)
from flask_login import (
    LoginManager, current_user,
    login_user, logout_user,
    login_required
)
from oauthlib.oauth2 import WebApplicationClient
from models.user import User
from models.game import Game


with open('oauth2.json', 'r') as f:
    oauth_obj =json.load(f)
    print(oauth_obj)


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
app = Flask(__name__)
app.secret_key = os.urandom(24)


client = WebApplicationClient(oauth_obj['web']['client_id'])

engine= ""
engine_dict = {
    'stockfish' : r"stockfish\stockfish-windows-x86-64.exe",
    'komodo' : r"komodo3-64-win\komodo3-64.exe"
}

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return models.storage.get(User, user_id)

@app.teardown_appcontext
def teardown_db(exception):
    """closes the storage on teardown"""
    models.storage.close()

@app.route('/', strict_slashes=False)
def index():
    return render_template('main.html')

@app.route('/login', strict_slashes=False)
@app.route('/login/<id>', strict_slashes=False)
def login(id=""):

    
        
    request_uri = client.prepare_request_uri(
        oauth_obj['web']['auth_uri'],
        redirect_uri=oauth_obj['web']['redirect_uris'][0],
        scope=['openid', 'email', 'profile'],
        state=id
    )

    return redirect(request_uri)

@app.route('/login/callback')
def callback(id=""):
    code = request.args.get('code')
    state = request.args.get('state')
    print(code)
    print(state)


    token_url, headers, body = client.prepare_token_request(
        oauth_obj['web']['token_uri'],
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(oauth_obj['web']['client_id'], oauth_obj['web']['client_secret']),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    uri, headers, body = client.add_token("https://openidconnect.googleapis.com/v1/userinfo")
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get('email_verified'):
        google_id=userinfo_response.json().get('sub')
        email=userinfo_response.json().get('email')
        picture=userinfo_response.json().get('picture')
        users_name= userinfo_response.json().get('given_name')
    else:
        return "User email not available or not verified by Google.", 400

    
    user = models.storage.get_google_id(User, google_id)
    

    if user is None:
        user = User(google_id=google_id, email=email,
                    picture=picture, users_name=users_name)
        user.save()
    # user = User(google_id=google_id, email=email)

    login_user(user)
    if state:
        return redirect('/chess/{}/'.format(state))
    else:
        return redirect(url_for('index'))


@app.route('/chess/<game_id>/', strict_slashes=False)
def chess_game(game_id):
    global engine
    # if engine == "":
    #     return redirect('http://127.0.0.1:5000/')
    
    game = models.storage.get(Game, game_id)

    if current_user.is_anonymous:
        game.opponent_name = "anonymous"
        
    elif game.user.id != current_user.id:
        game.opponent_name = current_user.users_name
    models.storage.save()

    game = models.storage.get(Game, game_id)

    org_squares = chess.SQUARE_NAMES
    org = []
    for i in range(8, 0, -1):
        val = i * 8
        for n in range(8, 0, -1):
            org.append(chess.SQUARE_NAMES[val - n])

    print(game.user_start)
    if game.user_start == True:
        working_sqr = org.copy()
        start = game.user_start
        if game.opponent == 'human' and (current_user.is_anonymous or game.user.id != current_user.id):
            working_sqr = org_squares.copy()
            start = False
    else:
        working_sqr = org_squares.copy()
        start = game.user_start
        if game.opponent == 'human' and (current_user.is_anonymous or game.user.id != current_user.id):
            working_sqr = org_squares.copy()
            start = True


    
    squares=[]
    print(chess.SQUARE_NAMES)
    for pos in range(len(chess.SQUARE_NAMES)):
        row = []
        row.append(working_sqr[pos])
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
    if game.opponent == 'human':
        if current_user.is_anonymous or game.user.id != current_user.id:
            opponent = game.user.users_name
        elif game.user.id == current_user.id:
            opponent = game.opponent_name
    print(squares)
    
    return render_template(
        'chess.html',
        squares=squares, 
        pwhite=pawn_white,
        pblack=pawn_black,
        opponent=opponent, 
        game_style=game.game_style,
        start=start,
        game=game
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

@app.route('/play-human/<id>/<move_no>', methods=['GET','POST'], strict_slashes=False)
def play_human(id, move_no):
    if request.method == 'POST':
        result = {}
        dic = request.get_json()
        if dic['move'][0:2] == dic['move'][2:4]:
            return jsonify({'answer': 'false'})
        board = chess.Board(dic['fen'])
        move = chess.Move.from_uci(dic['move'])
        if move in board.legal_moves:

            with open('moves.json', 'r') as f:
                obj = json.load(f)
            obj[id]['move'].append(str(move))
            obj[id]['san'].append(str(board.san(move)))
            result['answer'] = 'true'
            result['san'] = str(board.san(move))
            board.push(move)
            result['status'] = board.turn
            result['ischeck'] = board.is_check()
            result['ischeckmate'] = board.is_checkmate()
            result['fen'] = board.fen()
            

            
            obj[id]['fen'].append(board.fen())

            with open('moves.json', 'w') as f:
                json.dump(obj, f)
            return jsonify(result)
        else:
            jsonify({'answer': 'false'})

    with open('moves.json', 'r') as f:
        obj = json.load(f)
        print(obj)

    if len(obj[id]['move']) - 1 == int(move_no):
        return jsonify({
            'move': obj[id]['move'][int(move_no)],
            'fen' : obj[id]['fen'][int(move_no)],
            'san' : obj[id]['san'][int(move_no)]
            })
    else:
        return jsonify({'move': ''})
    
    
        




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
    print(request.args)


    game_style = dic['game_style']
    opponent = dic['opponent']
    if dic.get('start'):
        user_start = True
    else:
        user_start = False
    comp_engine  = dic.get('engine')

    if opponent == 'human':
        game = Game(opponent=opponent, game_style=game_style, 
                    user_start=user_start, opponent_name='anonymous')
        current_user.games.append(game)
        game.save()
        current_user.save()
        with open('moves.json', 'r') as f:
            obj = json.load(f)

        obj[game.id] = {'move': [], 'fen': [], 'san': []}

        with open('moves.json', 'w') as f:
            json.dump(obj, f)
        return redirect('/chess/{}/'.format(game.id))
    return 'successful'


    #get the global engine variable
    # global engine

    # # set the engine to the one selected
    # engine = chess.engine.SimpleEngine.popen_uci(engine_dict[str(dic.get('comp_engine'))])

    # # get key values for the style of game
    # game_style = dic.get('chess-style')

    # # get the side to start
    # starter = dic.get('whotostart')
    # if starter == None:
    #     starter = 'w'
    # return redirect('http://127.0.0.1:5000/chess/{}/{}/'.format(game_style, starter))


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
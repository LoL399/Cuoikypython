import torch
import chess
import chess.svg
from state import State
import time
import traceback
import base64
from flask import Flask, Response, request, render_template
import os

MAXVAL = 10000
class ClassicValuator(object):
    values = {chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0}

    def __init__(self):
        self.reset()
        self.memo={}
    def reset(self):
        self.count = 0
    def __call__(self,s):
        self.count+=1
        key = s.key()
        if key not in self.memo:
            b = s.board
            if b.is_variant_win():
                if b.turn == chess.WHITE:
                    return MAXVAL
                else:
                    return -MAXVAL
            if b.is_variant_loss():
                if b.turn == chess.WHITE:
                    return -MAXVAL
                else:
                    return MAXVAL
            val=0.0
            pm = s.board.piece_map()
            for x in pm:
                tval = self.values[pm[x].piece_type]
                if pm[x].color == chess.WHITE:
                    val+=tval
                else:
                    val=tval
            #slow
            bak = b.turn
            b.turn = chess.WHITE
            val += 0.1 * b.legal_moves.count()
            b.turn = chess.BLACK
            val -= 0.1 * b.legal_moves.count()
            b.turn = bak
            self.memo[key]=val
        
        return self.memo[key]
            

def explore_leaves(s,v):
    ret=[]
    v.reset()   
    for e in s.edges():
        s.board.push(e)
        ret.append((computer_minimax(s,v),e))
        s.board.pop()
    return ret

#############################################################################################    
v = ClassicValuator()
#v = Valuator()
s = State()

def computer_minimax(s, v, depth=2):
    if depth == 0 or s.board.is_game_over():
        return v(s)
# white is maximizing player
    turn = s.board.turn
    if turn == chess.WHITE:
        ret = -MAXVAL
    else:
        ret = MAXVAL

    for e in s.edges():
        s.board.push(e)
        tval = computer_minimax(s,v,depth-1)
        if turn == chess.WHITE:
            ret = max(ret,tval)
        else:
            ret = min(ret,tval)
        s.board.pop()
    return ret

def to_svg(s):
    return base64.b64encode(chess.svg.board(board = s.board).encode('utf-8')).decode('utf-8')

app = Flask(__name__)
@app.route("/")
def hello():
    ret = open("index.html").read()
    return ret.replace('start', s.board.fen())
   
def computer_move(s,v):
    move = sorted(explore_leaves(s, v),key=lambda x: x[0], reverse=s.board.turn)
    if len(move)==0:
        return 
    s.board.push(move[0][1])
@app.route("/move_coordinates")



def move_coordinates():
    if not s.board.is_game_over():
      source = int(request.args.get('from', default=''))
      target = int(request.args.get('to', default=''))
      promotion = True if request.args.get('promotion', default='') == 'true' else False
      move = s.board.san(chess.Move(source, target, promotion=chess.QUEEN if promotion else None))

    if move is not None and move != "":
        print("human moves", move)
        try:
            s.board.push_san(move)
            computer_move(s, v)
        except Exception:
            traceback.print_exc()
        response = app.response_class(response=s.board.fen(),status=200)
        return response
    print("GAME IS OVER")
    response = app.response_class(response="game over",status=200)
    return response

@app.route("/newgame")
def newgame():
    s.board.reset()
    response = app.response_class(response=s.board.fen(),status=200)
    return response

#pc vs pc    
@app.route("/self")
def selfplay():
    s=State()
    ret = '<html><head>'
    while not s.board.is_game_over():
        computer_move(s,v)
        ret += '<img width=600 height=600 src="data:image/svg+xml;base64,%s"></img><br/>'% to_svg(s)

    return ret

#pc vs player
@app.route("/move")
def move():
    if not s.board.is_game_over():
        move = request.args.get('move', default="")
        if move is not None and move !="":
            print("Human moves",move)
            try:
                s.board.push_san(move)
                computer_move(s,v)
            except Exception:
                traceback.print_exc()
                response = app.response_class( response=s.board.fen(),status=200)
                return response
    else:
        print("GAME OVER")
        response = app.response_class(response="game over",status=200)
        return response
    return hello()
       

if __name__=="__main__":
    if os.getenv("SELF") is not None:
        s = State()
        while not s.board.is_game_over():
            computer_move(s, v)
            print(s.board)
        print(s.board.result())
    else:
        app.run()

        


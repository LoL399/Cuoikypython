import numpy as np
import chess

#class dung may logic con co, tao ban co ao
class State(object):
  def __init__(self, board=None):
    if board is None:
      self.board = chess.Board()
    else:
      self.board = board

  def key(self):
    return (self.board.board_fen(), self.board.turn, self.board.castling_rights, self.board.ep_square)

  def edges(self):
    return list(self.board.legal_moves)

if __name__ == "__main__":
  s = State()


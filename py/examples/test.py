import time

from checkers_game_toolbox import *
from mcts_toolbox import *
from board_visuals import BasicVisual

boardgame=CheckerBoard(visual=BasicVisual)

boardgame.initBoard(2)

print(boardgame.matrix)

checker_to_move = boardgame.getSquare(3,2).checker
boardgame.move(checker_to_move, (2,3))

time.sleep(1)

checker_to_move = boardgame.getSquare(0,5).checker
boardgame.move(checker_to_move, (1,4))

time.sleep(1)

isAlive =  boardgame.playRandomMove(1, forcedTakeRule=True) 

time.sleep(1)

isAlive =  boardgame.playRandomMove(2, forcedTakeRule=True) 

time.sleep(1)

mcts_player=MCTS(playerId=1, boardgame=boardgame, depth_RollOut=20, thinkingTime=2., forcedTakeRule=True)

mcts_player.draw()

isAlive, mcts_player = boardgame.playMCTSMove(mcts_player)

mcts_player.draw()

time.sleep(1)

isAlive =  boardgame.playRandomMove(2, forcedTakeRule=True) 

time.sleep(1)

mcts_player = mcts_player.observeBoard(boardgame)

mcts_player.draw()

isAlive, mcts_player = boardgame.playMCTSMove(mcts_player)

mcts_player.draw()

time.sleep(2)

mcts_player=MCTS(playerId=2, boardgame=boardgame, depth_RollOut=10, thinkingTime=1., forcedTakeRule=True)
boardgame.playUserAgainstMCTS(mcts_player)


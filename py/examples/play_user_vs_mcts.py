from checkers_game_toolbox import *
from mcts_toolbox import *
from board_visuals import BasicVisual
from reward_designs_toolbox import *

if __name__ == '__main__':

    boardgame=CheckerBoard(visual=BasicVisual)

    boardgame.initBoard(2)

    mcts_player=MCTS(playerId=2, boardgame=boardgame, 
        thinkingTime=2., useTransfer=True,
        depth_RollOut=10, CONST_UCB=.2, rewardDesign=rewardDesign_1,
        forcedTakeRule=True)

    boardgame.playUserAgainstMCTS(mcts_player)





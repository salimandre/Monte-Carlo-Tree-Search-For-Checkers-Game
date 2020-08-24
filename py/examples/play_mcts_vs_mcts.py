from checkers_game_toolbox import *
from mcts_toolbox import *
from board_visuals import BasicVisual
from reward_designs_toolbox import *

if __name__ == '__main__':

    boardgame=CheckerBoard(visual=BasicVisual)

    boardgame.initBoard(2)

    mcts_player_1=MCTS(playerId=1, boardgame=boardgame, 
        thinkingTime=1., useTransfer=True,
        depth_RollOut=10, CONST_UCB=.4, rewardDesign=rewardDesign_1,
        forcedTakeRule=True)

    mcts_player_2=MCTS(playerId=2, boardgame=boardgame, 
        thinkingTime=2., useTransfer=True,
        depth_RollOut=10, CONST_UCB=.4, rewardDesign=rewardDesign_1,
        forcedTakeRule=True)

    outcome, n_turns, winnerId, score = boardgame.playMCTSAgainstMCTS(mcts_player_1, mcts_player_2, draw_after=70)
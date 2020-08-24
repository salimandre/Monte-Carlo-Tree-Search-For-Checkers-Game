import time

from checkers_game_toolbox import *
from mcts_toolbox import *
from reward_designs_toolbox import *
from board_visuals import BasicVisual

def evaluateMCTSconfig(practice_partner, mcts_player_to_eval, draw_after=50,  visual=None):
    
    boardgame=CheckerBoard(visual=visual)

    boardgame.initBoard(2)

    if mcts_player_to_eval.playerId==2:
        outcome, n_turns, winnerId, score = boardgame.playMCTSAgainstMCTS(practice_partner, mcts_player_to_eval, draw_after=draw_after)

    if mcts_player_to_eval.playerId==1:
        outcome, n_turns, winnerId, score = boardgame.playMCTSAgainstMCTS(mcts_player_to_eval, practice_partner, draw_after=draw_after)

    mcts_eval=lambda x: .04*(15-x)+0.9

    if outcome=='draw':
        return mcts_eval(draw_after)

    if outcome=='win':
        if winnerId==mcts_player_to_eval.playerId:
            return mcts_eval(n_turns)
        else:
            return mcts_eval(2*draw_after*draw_after/n_turns)


if __name__ == '__main__':

    evaluator=MCTS(playerId=2, boardgame=None, 
        thinkingTime=1., useTransfer=True,
        depth_RollOut=10, CONST_UCB=6., rewardDesign=rewardDesign_1,
        forcedTakeRule=True)

    mcts_player=MCTS(playerId=1, boardgame=None, 
        thinkingTime=2., useTransfer=True,
        depth_RollOut=18, CONST_UCB=7., rewardDesign=rewardDesign_1,
        forcedTakeRule=True)
           
    score = evaluateMCTSconfig(practice_partner=evaluator, mcts_player_to_eval=mcts_player)
    print('*\nscore = ', score,'\n*')


import numpy as np

def rewardDesign_1(boolTrueWinner, nTurns, depth_RollOut, deltaScore, alpha_RewardDesign=0.5):
    win_reward = alpha_RewardDesign * np.exp(-nTurns/9.) + (1. - alpha_RewardDesign) * deltaScore/12

    if deltaScore>0:
        return win_reward, 'win'
    else:
        return .03, 'win'
        #return None, 'draw'             






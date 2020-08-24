import time
import copy
import random
import numpy as np

from reward_designs_toolbox import rewardDesign_1#, rewardDesign_2

class MCTS:
    def __init__(self, playerId, boardgame, parent=None, children=[], CONST_UCB=.9, depth_RollOut=100, 
        rewardDesign=rewardDesign_1, thinkingTime=1., useTransfer=False, forcedTakeRule=True):

        self.CONST_UCB=CONST_UCB
        self.depth_RollOut=depth_RollOut

        self.forcedTakeRule=forcedTakeRule

        self.useTransfer=useTransfer

        self.thinkingTime=thinkingTime

        self.parent=parent

        self.rewardDesign=rewardDesign

        if self.parent is None:
            self.nTurns=1
        else:
            if self.parent.parent is None:
                self.nTurns=1
            else:
                self.nTurns=1+self.parent.parent.nTurns

        self.playerId=playerId

        self.boardgame=copy.deepcopy(boardgame) #boardgame
        self.visitCount=1
        self.reward=0

        self.potential_children=[]
        if self.boardgame is not None:
            forest_moves=self.boardgame.getForestMoves(playerId, forcedTakeRule)
            if len(forest_moves)>0 and self.nTurns<100:
                self.hasEnded=False
                for tree in forest_moves:
                    checker, _, tree_nodes = tree
                    for node in tree_nodes:
                        self.potential_children+=[(checker, node)]
            else:
                self.hasEnded=True

        self.expanded_children=[]
        self.nextMoves=[]


    def expand(self):
        '''
        select one of possible moves at position self.boardgame
        create a MCTS as a child from self from new position
        '''
        chosen_checker, chosen_node = random.choice(self.potential_children)
        next_move = chosen_node.getRoot2Node()[1:]

        copy_board = copy.deepcopy(self.boardgame)
        copy_board.visual=None
        copy_checker = copy_board.getSquare(*chosen_checker.square.pos).checker

        for node in next_move:
            copy_board.move(copy_checker, node.pos)

        next_playerId = 3-self.playerId

        new_child = MCTS(playerId=next_playerId, boardgame=copy_board, parent=self, 
            CONST_UCB=self.CONST_UCB, depth_RollOut=self.depth_RollOut, rewardDesign=self.rewardDesign,
            thinkingTime=self.thinkingTime, useTransfer=self.useTransfer, forcedTakeRule=self.forcedTakeRule)

        self.expanded_children+=[new_child]
        self.nextMoves+=[(chosen_checker.square.pos, [nd.pos for nd in next_move])]
        self.potential_children.remove((chosen_checker, chosen_node))

        return new_child


    @property
    def isFullyExpanded(self):
        if self.potential_children==[]:
            return True
        else:
            return False

    @property
    def isRoot(self):
        if self.parent is None:
            return True
        else:
            return False

    @property
    def isLeaf(self):
        if len(self.expanded_children)==0:
            return True   
        else:
            return False

    @property
    def depth(self):
        if self.isRoot:
            return 0
        else:
            return 1 + self.parent.depth

    @property
    def leaves(self):
        if self.isLeaf:
            return [self]
        else:
            leaves=[]
            for child in self.expanded_children:
                leaves+=child.leaves
            return leaves

    @property
    def nodes(self):
        if self.isLeaf:
            return [self]
        else:
            nodesInChildren=[]
            for child in self.expanded_children:
                nodesInChildren+=child.nodes
            
            return [self]+nodesInChildren

    def draw(self):
        if not self.isLeaf:
            str_node=self.depth*'          '+'('+(str(self.visitCount)+','+str(self.reward/self.visitCount)[:5]+')').ljust(3)+'----'
            #str_node=self.depth*'          '+'(o,'+(str(self.visitCount)+','+str(self.nTurns)+')').ljust(3)+'----'
            print(str_node)
            for child in self.expanded_children:
                child.draw()
        else:
            str_node=self.depth*'          '+'('+(str(self.visitCount)+','+str(self.reward/self.visitCount)[:5]+')').ljust(3)
            #str_node=self.depth*'          '+'(o,'+(str(self.visitCount)+','+str(self.nTurns)+')').ljust(3)
            print(str_node)
            for child in self.expanded_children:
                child.draw()

    def __updateNTurns(self,delta):
        '''
        Update nTurns after change of root in MCTS
        '''
        if delta%2==0:
            self.nTurns-=delta//2
        else:
            if self.depth%2==0:
                self.nTurns-=delta

        for child in self.expanded_children:
            child.__updateNTurns(delta)


    def observeBoard(self, new_boardgame):
        '''
        look for a node with position equals 
        to new_boardgame in tree. If there is
        then this node becomes the new MCTS root.
        If not then return a new MCTS with new_boardgame
        and with same hyperparameters as self.
        '''
        if self.boardgame is None:
            #print('* None *')
            return MCTS(playerId=self.playerId, boardgame=new_boardgame, parent=None, 
                CONST_UCB=self.CONST_UCB, depth_RollOut=self.depth_RollOut, rewardDesign=self.rewardDesign,
                thinkingTime=self.thinkingTime, useTransfer=self.useTransfer, forcedTakeRule=self.forcedTakeRule)
        else:
            if np.sum(self.boardgame.matrix != new_boardgame.matrix) == 0:
                # if new_boardgame equals current boardgame then do nothing
                #print('* same board *')
                return self
            else:
                if self.useTransfer:
                    # look for evaluations on similar boardgame as new_boardgame to transfer
                    for node in self.nodes:
                        if np.sum(node.boardgame.matrix != new_boardgame.matrix) == 0 and node.playerId==self.playerId:
                            #  update node to be a root
                            node.__updateNTurns(node.depth)
                            node.parent=None
                            #print('** transfer + {} **'.format(node.visitCount))
                            return node
                #print('** no transfer **') 
                return MCTS(playerId=self.playerId, boardgame=new_boardgame, parent=None, 
                    CONST_UCB=self.CONST_UCB, depth_RollOut=self.depth_RollOut, rewardDesign=self.rewardDesign,
                    thinkingTime=self.thinkingTime, useTransfer=self.useTransfer, forcedTakeRule=self.forcedTakeRule)


    def updateReward(self, winnerId, newReward):
        '''
            add newReward to mcts node self iff 
            mcts node is the result of a play 
            from player winnerId.
        '''

        if not self.hasEnded:
            if self.playerId==3-winnerId:
                self.reward+=newReward

    def backpropagateReward(self, winnerId, newReward):
        '''
            backpropagate reward from leaf Lt by updating
            rewards on path from parent node of Lt to
            root node
        '''

        temp_mcts = self
        while temp_mcts.parent is not None:
            temp_mcts.parent.visitCount+=1
            temp_mcts.parent.updateReward(winnerId, newReward)
            temp_mcts=temp_mcts.parent

        
    def optimistic_selection(self):
        '''
        Returns the MCTS leaf with current best UCB:
        '''
        if self.isFullyExpanded and not self.hasEnded:
            best_UCB = -1e6

            for i, child in enumerate(self.expanded_children):
                #print('mean = ',child.reward/child.visitCount)
                #print('bound = + ',self.CONST_UCB * np.sqrt(np.log(self.visitCount)/child.visitCount))
                child_UCB = child.reward/child.visitCount + self.CONST_UCB * np.sqrt(np.log(self.visitCount)/child.visitCount)

                if child_UCB > best_UCB:
                    best_UCB_child_i = i
                    best_UCB = child_UCB

            return self.expanded_children[best_UCB_child_i].optimistic_selection()

        else:
            return self


    def rollOut(self):
        '''
        A virtual game is played with 2 random players during
        a number of turns self.depth_RollOut then returns
        winnerId, nb of turns, checkers counts difference
        '''

        virtual_board=copy.deepcopy(self.boardgame)

        next_playerId=self.playerId
        true_winner=False

        for i in range(self.depth_RollOut):

            isAlive =  virtual_board.playRandomMove(next_playerId, self.forcedTakeRule)
            if not isAlive:
                winnerId=3-next_playerId
                true_winner=True
                break

            next_playerId=3-next_playerId                       

            isAlive = virtual_board.playRandomMove(next_playerId, self.forcedTakeRule)
            if not isAlive:
                winnerId=3-next_playerId
                true_winner=True
                break 
            
            next_playerId=3-next_playerId  

        cc_1 = len(virtual_board.checkers['1'])
        cc_2 = len(virtual_board.checkers['2'])

        delta_checkers = cc_2 - cc_1

        if i+1==self.depth_RollOut:
            if delta_checkers < 0:
                winnerId=1
            elif delta_checkers > 0:
                winnerId=2
            else:
                winnerId=0

        return true_winner, winnerId, i+1, np.abs(delta_checkers)


    def getBestNextMove(self): 
        '''
        returns index of best move among self.nextMoves
        '''
        best_reward=-1e6
        for i, child in enumerate(self.expanded_children):
            if child.reward > best_reward:
                best_child_i = i
                best_reward = child.reward
        return best_child_i#self.nextMoves[best_child_i]

    def getBestNextMoveOLD(self): 
        '''
        returns index of best move among self.nextMoves
        '''
        best_reward=-1e6
        best_visitCount=0
        for i, child in enumerate(self.expanded_children):
            if child.visitCount > best_visitCount:
                best_child_i = i
                best_reward = child.reward
                best_visitCount = child.visitCount

            if child.visitCount == best_visitCount:
                if child.reward > best_reward:
                    best_child_i = i
                    best_reward = child.reward
                    best_visitCount = child.visitCount

        return best_child_i#self.nextMoves[best_child_i]

    def findNextMove(self):
        '''
        returns None if there is no move available
        else during a time Thinkingtime expands resursively
        MCTS tree self by UCB exploration/exploitation then 
        returns best move index of root node
        '''

        startClock = time.time()
        endClock = time.time()

        if not self.hasEnded:
            i = 0
            while endClock - startClock < self.thinkingTime:
                selectedNode = self.optimistic_selection()

                if not selectedNode.hasEnded:

                    newLeaf = selectedNode.expand()

                    bool_true_winner, winnerId, nturns, delta = newLeaf.rollOut()

                    reward, outcome = self.rewardDesign(bool_true_winner, nturns, self.depth_RollOut, delta)

                    if reward is not None:
                        if outcome == 'win':

                            newLeaf.updateReward(winnerId, reward)
                            newLeaf.backpropagateReward(winnerId, reward)

                        if outcome == 'draw':

                            newLeaf.updateReward(1, reward)
                            newLeaf.backpropagateReward(1, reward)
                            newLeaf.updateReward(2, reward)
                            newLeaf.backpropagateReward(2, reward)

                else:

                    cc_1, cc_2 = selectedNode.boardgame.getScore()
                    delta = np.abs(cc_2 - cc_1)

                    bool_true_winner = True

                    winnerId = 3-selectedNode.playerId

                    virtual_board=selectedNode.boardgame

                    win_reward = (1 + np.exp(-selectedNode.depth/10))*3 / 6

                    selectedNode.backpropagateReward(winnerId, win_reward)

                    reward, outcome = self.rewardDesign(bool_true_winner, selectedNode.nTurns, self.depth_RollOut, delta)

                    if outcome == 'win':

                        selectedNode.updateReward(winnerId, reward)
                        selectedNode.backpropagateReward(winnerId, reward)

                endClock = time.time()
                i+=1

            return self.getBestNextMove()

        else:

            return None

from turtle import *
import time
import copy
import random
import numpy as np

from mcts_toolbox import MCTS

class CheckerBoard:
    def __init__(self, visual=None):
        self.board=[None]*8*8
        self.visual=visual
        self.checkers={'1': [], '2': []}

    def initBoard(self, showtime=None):

        new_key=0
        for ix in range(8):
            for iy in range(8):

                new_checker=None

                if (ix+iy)%2==1 and (iy<3 or iy>4):
                        if iy<3:
                            playerId_=1
                            if self.visual is not None:
                                col_checker=self.visual.checker_col_1
                        if iy>4:
                            playerId_=2
                            if self.visual is not None:
                                col_checker=self.visual.checker_col_2

                        # create checker
                        if self.visual is None:
                            new_checker=Checker(key=new_key, playerId=playerId_)
                        else:
                            new_checker=Checker(key=new_key, playerId=playerId_, sizes=self.visual.checker_sizes, colors=col_checker)

                        self.checkers[str(playerId_)]+=[new_checker]

                # create square
                if self.visual is None:
                    new_square=Square(pos=(ix, iy), checker=new_checker)
                else:

                    if (ix+iy)%2==1:
                        col_square=self.visual.square_col_A
                    else:
                        col_square=self.visual.square_col_B

                    new_square=Square(pos=(ix, iy), checker=new_checker, size=self.visual.square_size, coord_x=self.visual.coord_X[ix], coord_y=self.visual.coord_Y[iy], color=col_square)

                # add square to the board
                self.board[ix*8+iy]=new_square

                new_key+=1

        # display boardgame
        if self.visual is not None:

            setup(420, 420, 370, 0)
            hideturtle()
            tracer(False)

            for ix in range(8):
                for iy in range(8):
                    self.getSquare(ix, iy).display()

            update()

            for checker in self.checkers['1']+self.checkers['2']:
                checker.display()

            update()

            self.displayScore()

            update()

            if showtime is not None:
                time.sleep(showtime)

    def display(self):
        setup(420, 420, 370, 0)
        hideturtle()
        tracer(False)

        for ix in range(8):
            for iy in range(8):
                self.getSquare(ix, iy).display()

        update()

        for checker in self.checkers['1']+self.checkers['2']:
            checker.display()

        update()

    def getSquare(self, ix, iy):
        return self.board[ix * 8 + iy]

    @property   
    def matrix(self):
        B=np.zeros((8,8))
        for ix in range(8):
            for iy in range(8):
                if self.getSquare(ix, iy).checker is None:
                    B[8-1-iy, ix] = 0
                else:
                    B[8-1-iy, ix] = self.getSquare(ix, iy).checker.playerId
        return B

    def move(self, checker, new_pos):

        delta_x = new_pos[0]-checker.square.pos[0]
        delta_y = new_pos[1]-checker.square.pos[1]            

        if delta_x == 2 or delta_x == -2:
            # you go to intermediate square and take opponent checker
            take_pos=(checker.square.pos[0]+int(0.5*delta_x), checker.square.pos[1]+int(0.5*delta_y))
            # remove an opponent checker
            opp_playerId=3-checker.playerId
            opp_checkerKey=self.getSquare(*take_pos).checker.key
            self.checkers[str(opp_playerId)] = [ c for c in self.checkers[str(opp_playerId)] if c.key!=opp_checkerKey]
            # go to intermediate square
            self.move(checker, take_pos)


        # remove checker from old square
        old_square=checker.square
        old_square.checker=None

        # add checker to new square
        new_square=self.getSquare(*new_pos)
        checker.square=new_square
        if checker.square.pos[1]==7 and checker.playerId==1 and not checker.isQueen:
            checker.isQueen=True
        if checker.square.pos[1]==0 and checker.playerId==2 and not checker.isQueen:
            checker.isQueen=True    
        new_square.checker=checker

        if self.visual is not None:
            old_square.display(empty=True)
            checker.display()
            self.displayScore()
            update()
            time.sleep(.1)

    def __getPossibleSpots(self, checker):
        '''
            return possible next spots after a move
            These are splitted between:
                - free spots 
                - spots occupied by an opponent checker
        '''

        # check possible moves within the board
        if not checker.isQueen and checker.playerId==1:
            Nbh=checker.square.getNeighborhood()
            pos_moves=[Nbh[str_pos] for str_pos in ['up-right', 'up-left'] if Nbh[str_pos] is not None] 

        if not checker.isQueen and checker.playerId==2:
            Nbh=checker.square.getNeighborhood()
            pos_moves=[Nbh[str_pos] for str_pos in ['down-right', 'down-left'] if Nbh[str_pos] is not None] 

        if checker.isQueen:
            Nbh=checker.square.getNeighborhood()
            pos_moves=[Nbh[str_pos] for str_pos in ['up-right', 'up-left', 'down-right', 'down-left'] if Nbh[str_pos] is not None]

        # check if possible spots are free 
        free_spots = [ pos for pos in pos_moves if self.getSquare(*pos).checker is None]

        # deduce occupied spots 
        occ_spots = [pos for pos in pos_moves if pos not in free_spots and self.getSquare(*pos).checker.playerId!=checker.playerId]

        return free_spots, occ_spots

    def __trySingleJump(self, checker, occ_pos):
        '''
            if can checker can take on occ_pos and move on the next square then return square pos
            else return None
        '''
        # check if occupied spots is on the edge of the board
        if occ_pos[1]==0 or occ_pos[1]==7 or occ_pos[0]==0 or occ_pos[0]==7:
            return None

        else:
            # check if next spot behind occupied spot is free
            delta_x = occ_pos[0]-checker.square.pos[0]
            delta_y = occ_pos[1]-checker.square.pos[1]
            target_pos=(occ_pos[0]+delta_x, occ_pos[1]+delta_y)
            if self.getSquare(*target_pos).checker is not None:
                return None

            else:
                return target_pos

    def __getTreeJumps(self, checker, node=None):

        if node is None:
            node = Node(pos=checker.square.pos, parent=None, children=[])

        _, occ_spots=self.__getPossibleSpots(checker)

        for pos in occ_spots:
            jump_pos = self.__trySingleJump(checker, pos)

            if jump_pos is not None:

                virtual_board = copy.deepcopy(self)
                virtual_board.visual=None
                virtual_checker = virtual_board.getSquare(*checker.square.pos).checker
                virtual_board.move(virtual_checker, jump_pos)

                new_node = Node(pos=jump_pos, parent=node, children=[])
                node.children+=[new_node]

                virtual_board.__getTreeJumps(virtual_checker, new_node)

        return node

    def getTreeMoves(self, checker, forcedTakeRule=True):
        '''
        return all available moves for a SINGLE checker as a tree
        '''

        root = self.__getTreeJumps(checker)

        if len(root.children)==0:
            canTake = False
        else:
            canTake = True

        if not forcedTakeRule or not canTake:
            free_spots, _ = self.__getPossibleSpots(checker)

            if len(free_spots)>0:
                for pos in free_spots:
                    new_node = Node(pos=pos, parent=root, children=[])
                    root.children+=[new_node]
                canMove=True
            else:
                canMove=bool(canTake)

        else:
            canMove=True

        root.updateLeaves()

        root.updateAncesters()

        tree_nodes=list(root.leaves)
        for nd in root.leaves:
            tree_nodes+=nd.ancesters

        tree_nodes=[node for node in tree_nodes if node != root]

        tree_nodes=list(set(tree_nodes))

        return root, tree_nodes, canMove, canTake

    def playRandomMove(self, playerId, forcedTakeRule=True):

        # find checkers which can move and if they can take
        checkers_to_play=[]
        nextMoveIsForced=False
        for checker in self.checkers[str(playerId)]:
            root, tree_nodes, canMove, canTake = self.getTreeMoves(checker, forcedTakeRule)
            
            if forcedTakeRule and canTake:
                nextMoveIsForced=True

            if canMove:
                checkers_to_play+=[(checker, root, tree_nodes, canTake)]

        # if forcedTakeRule applies and at least one checker can take, then next move is a take
        if nextMoveIsForced:
            checkers_to_play=[(tup[0], tup[1], tup[2]) for tup in checkers_to_play if tup[3]]
        else:
            checkers_to_play=[(tup[0], tup[1], tup[2]) for tup in checkers_to_play]

        if len(checkers_to_play)>0:

            chosen_checker, root, tree_nodes = random.choice(checkers_to_play)

            next_move = random.choice(tree_nodes).getRoot2Node()

            for node in next_move[1:]:
                self.move(chosen_checker, node.pos)

            return True

        else:
            return False

    def getForestMoves(self, playerId, forcedTakeRule=True):
        '''
        return all available moves for EACH checker of a player as a list of trees
        '''

        # find checkers which can move and if they can take
        forest_moves=[]
        nextMoveIsForced=False
        for checker in self.checkers[str(playerId)]:
            root, tree_nodes, canMove, canTake = self.getTreeMoves(checker, forcedTakeRule)
            
            if forcedTakeRule and canTake:
                nextMoveIsForced=True

            if canMove:
                forest_moves+=[(checker, root, tree_nodes, canTake)]

        # if forcedTakeRule applies and at least one checker can take, then next move is a take
        if nextMoveIsForced:
            forest_moves=[(tup[0], tup[1], tup[2]) for tup in forest_moves if tup[3]]
        else:
            forest_moves=[(tup[0], tup[1], tup[2]) for tup in forest_moves]

        return forest_moves

    def displayScore(self):

        if self.visual is not None:

            self.getSquare(0,0).display(empty=True, text=str(len(self.checkers['1'])), colorText=self.visual.checker_col_1[0])
            self.getSquare(7,7).display(empty=True, text=str(len(self.checkers['2'])), colorText=self.visual.checker_col_2[0])
            

    def getScore(self):

        return (len(self.checkers['1']), len(self.checkers['2']))

    def getWinner(self):
        return sorted([1,2], key=lambda k: self.getScore[k-1])[1]

    def playMCTSMove(self, mcts):

        mcts = mcts.observeBoard(self)

        best_child_ind = mcts.findNextMove()

        if best_child_ind is not None:

            checker_pos, next_pos = mcts.nextMoves[best_child_ind]

            my_checker = self.getSquare(*checker_pos).checker
            if self.visual is not None:
                my_checker.display(shine=True)
                update()
                time.sleep(.2)

            for pos in next_pos:
                self.move(my_checker, pos)

            return True, mcts
        else:
            return False, mcts

    def playUserAgainstMCTS(self, mcts_player):

        isAlive = False

        userId = 3-mcts_player.playerId

        forest_moves=self.getForestMoves(userId, mcts_player.forcedTakeRule)

        if len(forest_moves)>0:

            isAlive = True

            if userId == 1:
                print('select a checker to move...')
            else:
                print('click on the board to start...')

            global isUserTurn
            global checkerIsSelected
            global mcts_player_copy

            isUserTurn = userId==1
            checkerIsSelected = False
            mcts_player_copy=copy.deepcopy(mcts_player)

        def tapOne(x, y, board=self, userId=userId):
            '''
            select checker from user click on (x,y) over board.
            if checker around (x,y) can move then go to tapTwo
            else loop starts over waiting for a user click
            '''
            global checkerIsSelected
            global isUserTurn
            global isq, jsq
            global ick, jck
            global mcts_player_copy

            if isUserTurn and checkerIsSelected:

                isq = int((x - (-205))//50)
                jsq = int((y - (-145))//50 + 1)

                '''
                tapTwo moves checker on square (ick,jck) provided by tapOne
                to new square (isq,jsq) where is (isq,jsq) square is around 
                user click (x,y).
                If checker cannot move (isq,jsq) then loop starts over
                waiting for the user to click on a proper square
                '''

                forest_moves=board.getForestMoves(userId, mcts_player_copy.forcedTakeRule)

                for tree in forest_moves:
                    checker, _, tree_nodes = tree

                    if checker.square.pos == (ick, jck):

                        list_moves=[]
                        for node in tree_nodes:

                            if node.pos == (isq, jsq):

                                move = [node.pos for node in node.getRoot2Node()][1:]
                                list_moves+=[move]

                        if len(list_moves)>0:
                            chosen_move = sorted(list_moves, key=lambda a: len(a))[-1]
                            for pos in chosen_move:
                                board.move(checker, pos)

                            print('ok')
                            isUserTurn = False
                            ick, jck = None, None
                            isq, jsq = None, None
                            break

            if isUserTurn and not checkerIsSelected:

                checkerIsSelected = False

                ick = int((x - (-205))//50)
                jck = int((y - (-145))//50 + 1)

                forest_moves=board.getForestMoves(userId, mcts_player_copy.forcedTakeRule)

                if len(forest_moves)>0:

                    for tree in forest_moves:
                        checker, _, _ = tree

                        if checker.square.pos == (ick, jck):
                            checkerIsSelected = True
                            print('ok')
                            checker.display(shine=True)
                            print('select a square where to move checker...')
                            break
                else:
                    print('\n** MCTS won ! **')
                    bye()

            if not isUserTurn:
                isAlive, mcts_player_copy = board.playMCTSMove(mcts_player_copy)
                #mcts_player_copy.draw()
                #print('depths = ',max([leaf.depth for leaf in mcts_player_copy.leaves]))
                if not isAlive:
                    print('\n** User won ! **')
                    bye()
                else:                 
                    isUserTurn=True
                    checkerIsSelected = False
                    print('select a checker to move...')

        if isAlive:
            onscreenclick(tapOne)
            done()

    def playMCTSAgainstMCTS(self, mcts_player_1, mcts_player_2, draw_after=None):

        if mcts_player_1.playerId == 2:
            mcts_player_swap = mcts_player_2
            mcts_player_2 = mcts_player_1
            mcts_player_1 = mcts_player_swap
            del mcts_player_swap


        i_turn=0

        while True:

            isAlive, mcts_player_1 = self.playMCTSMove(mcts_player_1)
            #mcts_player_1.draw()

            if not isAlive:
                print('MCTS 2 won')
                outcome='win'
                winnerId=2
                break

            isAlive, mcts_player_2 = self.playMCTSMove(mcts_player_2)
            #mcts_player_2.draw()

            if not isAlive:
                print('MCTS 1 won')
                outcome='win'
                winnerId=1
                break

            i_turn+=1
            print('turn # {} played | score: {}'.format(i_turn, self.getScore()))

            if draw_after is not None and i_turn>=draw_after:
                print('current score: ', self.getScore())
                print('draw MCTS 1 vs MCTS 2')
                outcome='draw'
                winnerId=None
                break

        return outcome, i_turn, winnerId, self.getScore()

    def playMCTSAgainstRandom(self, mcts_player, draw_after=None):

        i_turn=0
        i_play=0
        isMCTSTurn = mcts_player.playerId == 1

        while True:

            if isMCTSTurn:

                isAlive, mcts_player = self.playMCTSMove(mcts_player)
                isMCTSTurn = False
                i_play+=1
                mcts_player.draw()

                if not isAlive:
                    print('Random player won')
                    outcome= 'win'
                    winnerId= 3 - mcts_player.playerId
                    break

            if not isMCTSTurn:

                isAlive = self.playRandomMove(3 - mcts_player.playerId, forcedTakeRule=mcts_player.__dict__['forcedTakeRule'])
                isMCTSTurn = True
                i_play+=1

                if not isAlive:
                    print('MCTS won')
                    outcome='win'
                    winnerId= mcts_player.playerId
                    break

            if i_play%2==0:
                i_turn=i_play//2
                print('turn # {} played | score: {}'.format(i_turn, self.getScore()))

            if draw_after is not None and i_turn>=draw_after:
                print('current score: ', self.getScore())
                print('draw MCTS vs Random')
                outcome='draw'
                winnerId=None
                break

        return outcome, i_turn, winnerId, self.getScore()

class Node:
    '''
    tree used to store every possible jump paths of a checker
    '''
    def __init__(self, pos, parent=None, children=[]):
        self.pos=pos
        self.parent=parent
        self.children=children
        self.leaves=[]
        self.ancesters=[]

    def getRoot(self):
        if self.parent is None:
            return self

        else:
            return self.parent.getRoot()

    def updateLeaves(self):
        if self.children==[]:
            parent_node = self.parent
            while parent_node is not None:
                parent_node.leaves+=[self]
                parent_node = parent_node.parent

        else:
            for child in self.children:
                child.updateLeaves()

    def updateAncesters(self):

        if self.parent is not None:
            self.ancesters+=[self.parent] + self.parent.ancesters

        for child in self.children:
            child.updateAncesters()

    def getRoot2Node(self):
        return self.ancesters[::-1]+[self]


class Square:
    def __init__(self, pos, checker, size=None, coord_x=None, coord_y=None, color=None):
        self.pos=pos
        self.checker=checker
        if self.checker is not None:
            self.checker.square=self

        self.size=size
        self.coord_x=coord_x
        self.coord_y=coord_y
        self.color=color

    def display(self, empty=False, text='', colorText='black'):

        up()
        goto(self.coord_x, self.coord_y)
        if empty:
            hideturtle()

        fillcolor(self.color)
        begin_fill()
        for i in range(4):
          forward(self.size)
          right(90)
        end_fill()

        if len(text)>0:
            goto(self.coord_x+25, self.coord_y-35)
            color(colorText)
            write(text, True, align="center",font=("Arial", 20, "bold"))
            update()

    def getNeighborhood(self):
        Nbh={'up-right': (self.pos[0]+1, self.pos[1]+1), 'up-left': (self.pos[0]-1, self.pos[1]+1), \
                'down-right': (self.pos[0]+1, self.pos[1]-1), 'down-left': (self.pos[0]-1, self.pos[1]-1)}

        if self.pos[0]==0:
            Nbh['up-left']=None
            Nbh['down-left']=None
        if self.pos[0]==7:
            Nbh['up-right']=None
            Nbh['down-right']=None
        if self.pos[1]==0:
            Nbh['down-left']=None
            Nbh['down-right']=None
        if self.pos[1]==7:
            Nbh['up-left']=None
            Nbh['up-right']=None

        return Nbh

class Checker:
    def __init__(self, key, playerId, sizes=None, colors=None):
        self.key=key
        self.square=None
        self.playerId=playerId
        self.isQueen=False

        if sizes is not None:
            self.size_inside=sizes[0]
            self.size_boundary=sizes[1]  
            self.size_shining=sizes[2]   
        else:
            self.size_inside=None
            self.size_boundary=None
            self.size_shining=None

        if colors is not None:
            self.col_inside=colors[0]
            self.col_boundary=colors[1]
            self.col_shining=colors[2]
        else:
            self.col_inside=None
            self.col_boundary=None
            self.col_shining=None

    def display(self, shine=False):
        up()
        goto(self.square.coord_x+25, self.square.coord_y-25)

        if shine:
            dot(self.size_shining, self.col_shining)

        dot(self.size_inside, self.col_inside)
        dot(self.size_boundary, self.col_boundary)

        if self.isQueen:
            goto(self.square.coord_x+25, self.square.coord_y-35)

            if self.playerId==1:
                color(self.col_inside)
            if self.playerId==2:
                color(self.col_inside)

            write("K", True, align="center",font=("Arial", 20, "bold"))

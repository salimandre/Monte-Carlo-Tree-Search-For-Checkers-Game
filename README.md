# Monte-Carlo Tree Search for checkers game

## Installation

These scripts ran on Mac with python 3.7.6 using only Turtle and Numpy packages.

## Content

  * **Checkers** game with **graphical interface** with 2 possible rules: with and without forced take (jump)
  * **MCTS** model with customized **reward designs**, **thinking time** and with option to use or not **transfer of knowledge** (MCTS player reuses relevant branches from former built tree according to current boardgame). It is also possible to visualize the tree with number of visits and average reward at each state.
  * 3 Different **modes**: MCTS vs MCTS, User vs MCTS, MCTS vs Random
  
### MCTS vs MCTS

<p align="center">
  <img src="img/mcts_v_mcts.gif" width="24%">
</p>

### User vs MCTS

<p align="center">
  <img src="img/user_v_mcts.gif" width="24%">
</p>

### MCTS vs Random

<p align="center">
  <img src="img/mcts_v_random.gif" width="24%">
</p>

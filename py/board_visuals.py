class BasicVisual:

    # coordinates for top left corner of squares 
    # graphical x,y not like matrix coordinates
    coord_X=list(range(-205, 175, 50))
    coord_Y=list(range(-145, 235, 50))
    # dimension = height = width for squares
    square_size=50
    # colors for squares 
    square_col_A='#afd7db'
    square_col_B='#3c6bba'
    # diameter whole checker, diameter for interior of checker, 
    # diameter for checker with shining circle when selected
    checker_sizes=[40, 30, 50]
    # colors for checkers: interior, edges, when selected
    checker_col_1=['#181818', '#273847', 'yellow']
    checker_col_2=['#5b000a', '#bf1f2e', 'yellow']
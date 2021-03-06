"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


import math
log2 = {0:float('-inf')}
for i in range(1,9):
    log2[i] = math.log2(i)

def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    # TODO: finish this function!
    # First, check if the game is lost or won.
    if game.is_loser(player):
        return float("-inf")
    if game.is_winner(player):
        return float("inf")
    
#    # Option one: "Guaranteed moves"
#    # Only count number of moves that are guaranteed---subtract one if there's an overlap between my moves and opponent's moves
#    active_moves = set(game.get_legal_moves(game.active_player))
#    inactive_moves = set(game.get_legal_moves(game.inactive_player))
#    score = len(active_moves) - max(len(inactive_moves - active_moves),len(inactive_moves)-1)
#    if game.active_player == player:
#        return score
#    else:
#        return -score
#    
#    # Option two: "Percent score"
#    # Look at the available moves as percent of total blank spaces
#    n_active = len(game.get_legal_moves(game.active_player))
#    n_inactive = len(game.get_legal_moves(game.inactive_player))
#    n_empty = len(game.get_blank_spaces())
#    score = n_active/n_empty - n_inactive/max(n_empty-1,0.5)
#    if game.active_player == player:
#        return score
#    else:
#        return -score
#    
    # Option three: "Single branch depth search"
    # If there's only a single choice for a move for the active player, then go deeper recursively
    active_moves = game.get_legal_moves(game.active_player)
    if len(active_moves) == 1:
        return custom_score(game.forecast_move(active_moves[0]),player)
    else:
        active_moves = set(active_moves)
        inactive_moves = set(game.get_legal_moves(game.inactive_player))
        n_empty = len(game.get_blank_spaces())
        score = len(active_moves)/n_empty - len(inactive_moves - active_moves)/(n_empty-1)
        if game.active_player == player:
            return score
        else:
            return -score

class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # TODO: finish this function!

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves
        
        # Default position to return is (-1,-1) if the algorithm doesn't find anything in time or if there's no next moves.
        position = (-1,-1)
        if len(legal_moves) == 0:
            return position
        
        # Unless method is specified as alphabeta, then run minimax.
        if self.method=='alphabeta':
            algorithm = self.alphabeta
        else:
            algorithm = self.minimax

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            
            # If iterative, run selected method continuously with increasing depth until time runs out, saving the output at every level
            if self.iterative:
                depth = 1
                while True:
                    score, position = algorithm(game, depth)
                    depth += 1
            # If not iterative, perform a single fixed-depth search
            else:
                score, position = algorithm(game, self.search_depth)

        except Timeout:
            # Handle any actions required at timeout, if necessary
            return position

        # Return the best move from the last completed search iteration
        return position
    
    def minimax(self, game, depth, maximizing_layer=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
        
        # TODO: finish this function!
        
        # Get the list of next possible moves
        possible_next_moves = game.get_legal_moves(game.active_player)
        
        # If there's no next moves, return (-1,-1).
        # If it's on CustomPlayer's turn, it's a losing state! Return score of -inf.  If it's not, it's a winning state---score of +inf.
        if len(possible_next_moves)==0:
            if maximizing_layer:
                return (float('-inf'),(-1,-1))
            else:
                return (float('inf'),(-1,-1))
        
        # This only runs when there are possible next moves.
        # If it has not reached the defined depth in the tree, go one layer deeper recursively.
        # If the defined depth is reached, calculate the score for the leaf nodes.  Score is in the perspective of the CustomPlayer agent.
        if depth > 1:
            scores = [self.minimax(game.forecast_move(move), depth-1, not maximizing_layer)[0] for move in possible_next_moves]
        else:
            scores = [self.score(game.forecast_move(move), self) for move in possible_next_moves]
        
        # Return max or min score, next_position combination.
        return maxmin_move(scores,possible_next_moves,maximizing_layer)

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_layer=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_layer : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # TODO: finish this function!
                # Get the list of next possible moves
        possible_next_moves = game.get_legal_moves(game.active_player)
        
        # If there's no next moves, return (-1,-1).
        # If it's on CustomPlayer's turn, it's a losing state! Return score of -inf.  If it's not, it's a winning state---score of +inf.
        if len(possible_next_moves)==0:
            if maximizing_layer:
                return (float('-inf'),(-1,-1))
            else:
                return (float('inf'),(-1,-1))
        
        # This only runs when there are possible next moves.
        # If it has not reached the defined depth in the tree, go one layer deeper recursively.
        # If the defined depth is reached, calculate the score for the leaf nodes.  Score is in the perspective of the CustomPlayer agent.
        if depth > 1:
            # First node score
            scores = [self.alphabeta(game.forecast_move(possible_next_moves[0]), depth-1, alpha, beta, not maximizing_layer)[0]]
            for move in possible_next_moves[1:]:
                # For minimizing layer, kill node if previous node is already less than alpha.
                # If it can't be removed, update the beta for the following layer, then recursively continue.
                # Similar for maximizing layer.
                if maximizing_layer:
                    if scores[-1] >= beta:
                        break
                    new_alpha = max(scores)
                    scores.append(self.alphabeta(game.forecast_move(move), depth-1, new_alpha, beta, not maximizing_layer)[0])
                else:
                    if scores[-1] <= alpha:
                        break
                    new_beta = min(scores)
                    scores.append(self.alphabeta(game.forecast_move(move), depth-1, alpha, new_beta, not maximizing_layer)[0])
        # Reached leaf nodes, calculate score.
        else:
            scores = []
            for move in possible_next_moves:
                scores.append(self.score(game.forecast_move(move), self))
                if (maximizing_layer and scores[-1]>=beta) or ((not maximizing_layer) and scores[-1]<=alpha):
                    break
        
        # Return max or min score, next_position combination.
        return maxmin_move(scores,possible_next_moves[:len(scores)],maximizing_layer)

def maxmin_move(scores, possible_next_moves, maximizing_layer):
    # For list of scores and list of possible_next_moves, return either max or min 
    if maximizing_layer:
        best_move = max(zip(scores,possible_next_moves), key=lambda x: x[0])
    else:
        best_move = min(zip(scores,possible_next_moves), key=lambda x: x[0])
    return best_move
import numpy as np
from anytree import Node, RenderTree


class GameTree(Node):
    def __init__(self, name, game,
                 reward_param=(1, 0, -1, 0), discount=1,
                 parent=None):
        super().__init__(name=name, parent=parent)
        self._game = game
        self._reward_param = reward_param
        self._discount = discount
        self._children_simulated = False
    
    def __repr__(self):
        print_text = '<State ({:}-{:}-{:.2f})>'
        print_text = print_text.format(
            self.name,
            self._game.winner,
            self.reward
        )
        return print_text
    
    @property
    def size(self):
        return 1 + len(self.descendants)
    
    @property
    def leaves(self):
        if self.is_leaf:
            return (self,)
        else:
            leaves = ()
            for child in self.children:
                leaves += child.leaves
            return leaves
    
    def show(self, max_depth=None):
        if max_depth is None:
            print(RenderTree(self))
        elif isinstance(max_depth, int):
            for pre, _, node in RenderTree(self):
                if node.depth <= max_depth:
                    print('{:}{:}'.format(pre, node))
        else:
            raise TypeError('max_depth must be either an int or None (whole tree).')
    
    @property
    def game(self):
        return self._game
    
    @property
    def winner(self):
        return self._game.winner
    
    @property
    def reward(self):
        if self.is_leaf:
            if self.winner is None:
                r = self._reward_param[3]
            elif self.winner == -1:
                r = self._reward_param[1]
            elif self.winner == self.root.game.turn_player:
                r = self._reward_param[0]
            else:
                r = self._reward_param[2]
            r *= self._discount**(max(self.depth - 1, 0) // 2)
        else:
            r = [x.reward for x in self.children]
            if self._children_simulated:
                r = sum(r)/len(r)
            else:
                r = max(r) if self.depth % 2 == 0 else min(r)
        return r
    
    def minmax(self, depth=1):
        for _ in range(depth):
            for node in self.leaves:
                if node.game.is_ended:
                    pass
                else:
                    for move in node.game.gameboard.available_moves:
                        game = node.game.copy()
                        game.move(*move, game.turn_player)
                        GameTree(move, game=game, parent=node)
    
    def alpha_beta(self, depth=1):
        for _ in range(depth):
            for node in self.leaves:
                if node.game.is_ended:
                    pass
                else:
                    for move in node.game.gameboard.available_moves:
                        game = node.game.copy()
                        game.move(*move, game.turn_player)
                        GameTree(move, game=game, parent=node)
                        if game.winner in range(2):
                            break
    
    def monte_carlo(self, r=10):
        for node in self.leaves:
            if node.game.is_ended:
                pass
            else:
                self._children_simulated = True
                for i in range(r):
                    game = node.game.copy()
                    while game.winner is None:
                        available_moves = game.gameboard.available_moves
                        move = available_moves[np.random.choice(len(available_moves))]
                        game.move(*move, player=game.turn_player)
                    GameTree('{:}_{:}'.format(node.name, i), game=game, parent=node)

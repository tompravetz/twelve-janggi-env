import gymnasium as gym
import numpy as np
from game import Game
from piece import Owner, PieceType

def build_action_list():
    actions = []
    directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    for row in range(4):
        for col in range(3):
            for dr, dc in directions:
                actions.append(("move", row, col, row+dr, col+dc))
    drop_pieces = [PieceType.MAN, PieceType.MINISTER, PieceType.GENERAL]
    for piece_type in drop_pieces:
        for row in range(4):
            for col in range(3):
                actions.append(("drop", piece_type, row, col))
    return actions

ALL_ACTIONS = build_action_list()

class TwelveJanggiEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.game = None
        self.observation_space = gym.spaces.Box(
            low=0,
            high=10,
            shape=(19,),
            dtype=np.int8
        )
        self.action_space = gym.spaces.Discrete(132)
        self.all_actions = ALL_ACTIONS
    
    def get_observation(self):
        PIECE_ENCODING = {
            PieceType.MINISTER: 1,
            PieceType.GENERAL: 2,
            PieceType.KING: 3,
            PieceType.MAN: 4,
            PieceType.FEUDAL_LORD: 5,
        }
        
        obs = []
        
        # Part 1: board (12 numbers)
        for row in range(4):
            for col in range(3):
                cell = self.game.board.grid[row][col]
                if cell is None:
                    obs.append(0)
                elif cell.owner == Owner.P0:
                    obs.append(PIECE_ENCODING[cell.piece_type])
                else:
                    obs.append(PIECE_ENCODING[cell.piece_type] + 5)
        
        # Part 2: hands (6 numbers)
        # count of MAN, MINISTER, GENERAL in P0's hand
        # count of MAN, MINISTER, GENERAL in P1's hand
        hand_pieces = [PieceType.MAN, PieceType.MINISTER, PieceType.GENERAL]
        for owner in [Owner.P0, Owner.P1]:
            for piece_type in hand_pieces:
                obs.append(self.game.board.hands[owner].count(piece_type))
        
        # Part 3: current player (1 number)
        obs.append(self.game.current_player.value)
        
        return np.array(obs, dtype=np.int8)
    
    def get_action_mask(self):
        mask = np.zeros(132, dtype=bool)
        legal_actions = self.game.get_all_legal_actions()
        for action in legal_actions:
            if action in self.all_actions:
                mask[self.all_actions.index(action)] = True
        return mask
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game = Game()
        return self.get_observation(), {"action_mask": self.get_action_mask()}
    
    def step(self, action_int):
        action = self.all_actions[action_int]
        self.game.step(action)
        obs = self.get_observation()
        if self.game.winner == Owner.P0:
            reward = 1
            terminated = True
        elif self.game.winner == Owner.P1:
            reward = -1
            terminated = True
        else:
            reward = 0
            terminated = False
        return obs, reward, terminated, False, {"action_mask": self.get_action_mask()}

env = TwelveJanggiEnv()
obs, info = env.reset()

# take the first legal action
legal_indices = np.where(info["action_mask"])[0]
print("Legal action indices:", legal_indices)

# step with first legal action
obs, reward, terminated, truncated, info = env.step(legal_indices[0])
print("After step 1:")
print("Reward:", reward)
print("Terminated:", terminated)
print("Legal actions:", info["action_mask"].sum(), "of 132")
print(env.game.board)
import random
import gymnasium as gym
import numpy as np
from .game import Game
from .piece import Owner, PieceType


# ── Opponent policies ─────────────────────────────────────────────────────────

def random_opponent(game):
    """Picks a random legal action. Default opponent policy."""
    actions = game.get_all_legal_actions()
    return random.choice(actions) if actions else None


def passive_opponent(game):
    """Never moves — useful for debugging win conditions."""
    return None


# ── Action list ───────────────────────────────────────────────────────────────

def build_action_list():
    actions = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for row in range(4):
        for col in range(3):
            for dr, dc in directions:
                actions.append(("move", row, col, row + dr, col + dc))
    drop_pieces = [PieceType.MAN, PieceType.MINISTER, PieceType.GENERAL]
    for piece_type in drop_pieces:
        for row in range(4):
            for col in range(3):
                actions.append(("drop", piece_type, row, col))
    return actions


ALL_ACTIONS = build_action_list()


# ── Environment ───────────────────────────────────────────────────────────────

class TwelveJanggiEnv(gym.Env):
    """
    Gymnasium environment for Twelve Janggi (십이장기).

    The agent always plays as Owner.P0. The opponent's behavior is controlled
    by the opponent_policy argument — a callable that takes a Game instance
    and returns an action tuple, or None to skip.

    Built-in policies:
        random_opponent  — picks a random legal action (default)
        passive_opponent — never moves (debug only)

    Custom policies (e.g. trained agent, human input) can be passed in at
    construction time, making it easy to swap opponents without changing the env.

    Args:
        first_player:     Owner.P0 or Owner.P1 — who moves first each episode.
        opponent_policy:  Callable(game) -> action tuple | None.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, first_player=Owner.P0, opponent_policy=None):
        super().__init__()
        self.first_player    = first_player
        self.opponent_policy = opponent_policy if opponent_policy is not None else random_opponent
        self.agent_owner     = Owner.P0   # agent is always P0
        self.game            = None

        self.observation_space = gym.spaces.Box(
            low=0, high=10, shape=(19,), dtype=np.int8
        )
        self.action_space = gym.spaces.Discrete(132)
        self.all_actions  = ALL_ACTIONS

    # ── Observation ───────────────────────────────────────────────────────────

    def get_observation(self):
        PIECE_ENCODING = {
            PieceType.MINISTER:    1,
            PieceType.GENERAL:     2,
            PieceType.KING:        3,
            PieceType.MAN:         4,
            PieceType.FEUDAL_LORD: 5,
        }
        obs = []

        # Board: 12 numbers
        for row in range(4):
            for col in range(3):
                cell = self.game.board.grid[row][col]
                if cell is None:
                    obs.append(0)
                elif cell.owner == Owner.P0:
                    obs.append(PIECE_ENCODING[cell.piece_type])
                else:
                    obs.append(PIECE_ENCODING[cell.piece_type] + 5)

        # Hands: 6 numbers (MAN, MINISTER, GENERAL counts for each player)
        hand_pieces = [PieceType.MAN, PieceType.MINISTER, PieceType.GENERAL]
        for owner in [Owner.P0, Owner.P1]:
            for piece_type in hand_pieces:
                obs.append(self.game.board.hands[owner].count(piece_type))

        # Current player: 1 number
        obs.append(self.game.current_player.value)

        return np.array(obs, dtype=np.int8)

    # ── Action mask ───────────────────────────────────────────────────────────

    def get_action_mask(self):
        mask = np.zeros(132, dtype=bool)
        legal_actions = self.game.get_all_legal_actions()
        for action in legal_actions:
            if action in self.all_actions:
                mask[self.all_actions.index(action)] = True
        return mask

    # ── Opponent step ─────────────────────────────────────────────────────────

    def _opponent_step(self):
        """Let the opponent policy take its turn."""
        if self.game.winner is not None:
            return
        action = self.opponent_policy(self.game)
        if action is not None:
            self.game.step(action)

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game = Game(first_player=self.first_player)

        # If opponent goes first, let them move before returning observation
        if self.first_player != self.agent_owner:
            self._opponent_step()

        return self.get_observation(), {"action_mask": self.get_action_mask()}

    # ── Step ──────────────────────────────────────────────────────────────────

    def step(self, action_int):
        # Agent's move
        action = self.all_actions[action_int]
        self.game.step(action)

        # Opponent's move (if game isn't over)
        if self.game.winner is None:
            self._opponent_step()

        # Result
        obs = self.get_observation()

        if self.game.winner == self.agent_owner:
            reward, terminated = 1.0, True
        elif self.game.winner is not None:
            reward, terminated = -1.0, True
        else:
            reward, terminated = 0.0, False

        return obs, reward, terminated, False, {"action_mask": self.get_action_mask()}
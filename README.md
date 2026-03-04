# Twelve Janggi Gym (십이장기)

A [Gymnasium](https://gymnasium.farama.org/) environment for **Twelve Janggi (십이장기)**, a strategy game from the Korean reality show [The Genius](https://the-genius-show.fandom.com/wiki/Twelve_Janggi). Built as a validation environment for [PIDGIN](https://github.com/tompravetz), a framework for emergent strategy vocabulary in reinforcement learning.

---

## What is Twelve Janggi?

Twelve Janggi is a two-player strategy game played on a 4×3 board — twelve squares total, hence the name. It appeared in *The Genius: Black Garnet* and *The Genius: Grand Final* as a death match format, where contestants competed in high-stakes elimination rounds.

The game is a modified version of Dobutsu Shogi, with key rule differences that make it strategically distinct. No published strategic analysis exists in English, and the game has no established human vocabulary for its concepts — making it an ideal domain for novel strategy discovery in RL research.

---

## Why does this exist?

This environment was built as the primary validation domain for **PIDGIN** (Policy Interpretability via Domain-Grounded Integrated Naming), a research framework for emergent strategy vocabulary in reinforcement learning. PIDGIN requires a domain where no prior LLM knowledge exists, so that any strategy vocabulary it generates is genuinely emergent rather than imported from existing human expertise. Twelve Janggi fits that requirement exactly.

It is also useful as a standalone lightweight two-player strategy environment for anyone interested in training RL agents on small combinatorial games with hand mechanics.

---

## Rules

- The board has 4 rows and 3 columns. Each player's closest row is their **territory**.
- Each player starts with 4 pieces: **Minister** (diagonal), **General** (orthogonal), **King** (all directions), and **Man** (forward only).
- When a **Man** enters the opponent's territory it promotes to **Feudal Lord**, which can move in all directions except diagonally backward.
- On each turn a player must either **move** a piece one square or **drop** a captured piece onto any empty square outside the opponent's territory.
- When a piece is captured it goes to the capturing player's hand. A captured Feudal Lord reverts to a Man.
- **Win condition 1:** Capture the opponent's King.
- **Win condition 2:** Move your King into the opponent's territory and survive one full turn.

---

## Installation

```bash
git clone https://github.com/tompravetz/twelve-janggi-env
cd twelve-janggi-env
pip install .
```

> Install PyTorch separately from [pytorch.org](https://pytorch.org) for your platform before training.

---

## Usage

### Play against a random agent

```bash
python render.py
```

Click a piece to select it. Legal moves appear as yellow dots. Click a destination to move. To drop a captured piece, click it in your hand column on the right, then click a valid board square. Click a selected piece again to deselect. Press **R** to restart.

### Watch two random agents play

```bash
python render.py watch
```

### Run a random agent test (10 games)

```bash
python test_random.py
```

### Train an agent

> Coming soon — `train.py` with MaskablePPO via `sb3-contrib`.

> Install PyTorch for your platform before training: [pytorch.org](https://pytorch.org)

---

## Environment Details

### Observation space

A flat array of 19 integers (`Box(0, 10, shape=(19,), dtype=int8)`):

| Indices | Meaning |
|---|---|
| 0–11 | Board squares (row 0 col 0 → row 3 col 2). 0=empty, 1–5=P0 pieces, 6–10=P1 pieces |
| 12–14 | P0 hand counts: Man, Minister, General |
| 15–17 | P1 hand counts: Man, Minister, General |
| 18 | Current player (0=P0, 1=P1) |

Piece encoding: Minister=1, General=2, King=3, Man=4, Feudal Lord=5. P1 pieces add 5.

### Action space

`Discrete(132)` — a flat index over all possible actions:

| Range | Type | Count |
|---|---|---|
| 0–95 | Move actions (12 squares × 8 directions) | 96 |
| 96–131 | Drop actions (3 piece types × 12 squares) | 36 |

Illegal actions are masked at every step via the `action_mask` key in the info dict. Use `MaskablePPO` from `sb3-contrib` to respect the mask during training.

### Rewards

| Event | Reward |
|---|---|
| P0 wins | +1.0 |
| P1 wins | −1.0 |
| Any other step | 0.0 |

---

## File Structure

```
twelve-janggi-env/
├── piece.py          # PieceType, Owner enums, Piece class with move sets
├── board.py          # Board state, legal moves, drops, captures, win detection
├── game.py           # Turn management, action validation, game loop
├── env.py            # Gymnasium wrapper (TwelveJanggiEnv)
├── render.py         # Pygame renderer, human play mode, watch mode
├── test_random.py    # Run 10 random-vs-random games to verify the environment
└── pyproject.toml    # Package metadata and dependencies
```

---

## Related Projects

- **PRISM** — concept-based RL framework for zero-shot strategy transfer
- **PIDGIN** — emergent strategy vocabulary via co-evolved concepts and language (uses this environment)

---

## License

MIT
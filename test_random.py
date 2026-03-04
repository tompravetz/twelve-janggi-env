from env import TwelveJanggiEnv
import numpy as np

env = TwelveJanggiEnv()

for game_num in range(10):
    obs, info = env.reset()
    terminated = False
    steps = 0

    while not terminated and steps < 500:
        actions = np.where(info["action_mask"])[0]
        action = np.random.choice(actions)
        obs, reward, terminated, truncated, info = env.step(action)
        steps += 1

    print(f"Game {game_num + 1:2d}: {steps:3d} steps | winner: {env.game.winner}")
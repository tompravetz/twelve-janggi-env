"""
train.py — Train a MaskablePPO agent on Twelve Janggi.

Usage:
    python scripts/train.py                        # train with defaults
    python scripts/train.py --timesteps 1000000    # longer run
    python scripts/train.py --randomize            # randomize who goes first
"""

import argparse
import os
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from twelve_janggi import TwelveJanggiEnv
from twelve_janggi.piece import Owner


def mask_fn(env):
    return env.get_action_mask()


def make_env(randomize_first=False):
    if randomize_first:
        import random
        first = random.choice([Owner.P0, Owner.P1])
        env = TwelveJanggiEnv(first_player=first)
    else:
        env = TwelveJanggiEnv(first_player=Owner.P0)
    env = ActionMasker(env, mask_fn)
    return env


def train(timesteps=500_000, randomize_first=False, save_path="models/ppo_baseline"):
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    env = make_env(randomize_first)

    model = MaskablePPO(
        "MlpPolicy",
        env,
        verbose=1,
        tensorboard_log="logs/",
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        learning_rate=3e-4,
    )

    print(f"Training for {timesteps:,} timesteps...")
    print(f"Randomize first player: {randomize_first}")
    print(f"Saving to: {save_path}")
    print("-" * 40)

    model.learn(total_timesteps=timesteps)
    model.save(save_path)
    print(f"\nModel saved to {save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=500_000)
    parser.add_argument("--randomize", action="store_true",
                        help="Randomize which player goes first each episode")
    parser.add_argument("--save", type=str, default="models/ppo_baseline")
    args = parser.parse_args()

    train(
        timesteps=args.timesteps,
        randomize_first=args.randomize,
        save_path=args.save,
    )
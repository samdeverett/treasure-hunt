import ray
from ray.rllib.algorithms.ppo import PPOConfig
from constants import NUM_TRAINING_ITERATIONS
import argparse
from utils import get_env_config
from ray.rllib.policy.policy import PolicySpec
from environment import MultiAgentPressurePlate
from constants import CHECKPOINT_DIR
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    "--env_name", type=str, required=True, help="The PressurePlate configuration to use. See env_configs.py for supported configurations."
)

if __name__ == "__main__":
    args = parser.parse_args()

    # Initialize a Ray instance.
    ray.init()

    # Pull the configuration of the given environment.
    env_config = get_env_config(args.env_name)

    # Configure learning algorithm.
    config = (
        PPOConfig()
        .environment(
            env=MultiAgentPressurePlate,
            env_config=env_config
        )
        .multi_agent(
            policies={
                "agent_0_policy": PolicySpec(),
                "agent_1_policy": PolicySpec()
            },
            policy_mapping_fn=lambda agent_id, episode, worker, **kwargs: f"agent_{agent_id}_policy"
        )
    )

    # Build learning algorithm.
    algo = config.build()

    # Train learning algorithm.
    for i in range(NUM_TRAINING_ITERATIONS):
        algo.train()
        # Checkpoint at last iteration.
        if (i + 1) % NUM_TRAINING_ITERATIONS == 0:
            checkpoint_dir = algo.save(os.path.join(CHECKPOINT_DIR, args.env_name, str(i + 1))).checkpoint.path
            print(f"\nCheckpoint saved in directory {checkpoint_dir}\n")
            print(f"You can run a demo of the checkpoint using the following command: python demo.py --env_name {args.env_name} --checkpoint {i + 1} \n")

    # Release training resources.
    algo.stop()

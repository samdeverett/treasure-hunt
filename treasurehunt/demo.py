import os
from constants import CHECKPOINT_DIR
from ray.rllib.algorithms.algorithm import Algorithm
from environment import TreasureHunt
import argparse
from utils import get_env_config, check_args, print_step, print_actions, print_results, print_terminated

parser = argparse.ArgumentParser()
parser.add_argument(
     "--env_name", type=str, required=True, help="The environment configuration to use. See env_configs.py for supported configurations."
)
parser.add_argument(
    "--checkpoint", type=int, required=True, help="The checkpoint (i.e., number of training iterations) to use."
)

if __name__ == "__main__":
    args = parser.parse_args()

    # TODO: Check arguments are valid.
    check_args()

    # Pull checkpoint.
    checkpoint_path = os.path.join(CHECKPOINT_DIR, args.env_name, str(args.checkpoint))
    
    # Restore algorithm to checkpoint.
    algo = Algorithm.from_checkpoint(checkpoint_path)

    # Create environment.
    env_config = get_env_config(args.env_name)
    env = TreasureHunt(env_config)
    obs, info = env.reset()
    env.render()
    
    input()
    # Step through checkpointed policy.
    step = 1
    while True:
        print_step(step)
        # Get action for each agent.
        actions = {}
        for agent in obs.keys():
            action = algo.compute_single_action(
                obs[agent],
                # TODO generalize this using a policy_mapping_fn
                policy_id=f"agent_{agent}_policy",
                explore=False
            )
            actions[agent] = action
        print_actions(actions)
        # Take actions.
        obs, reward, terminated, truncated, info = env.step(actions)
        step += 1
        # Render results.
        print_results(reward, terminated, truncated)
        env.render()
        input()
        # Check for termination.
        if terminated['__all__'] or truncated['__all__']:
            print_terminated()
            break

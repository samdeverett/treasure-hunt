from typing import Dict, Optional
from env_configs import ENV_CONFIGS

def get_env_config(
        env_name: str
    ) -> Dict:
    assert env_name in ENV_CONFIGS, f"There is no configuration named {env_name}. Check env_configs.py for supported configurations."
    return ENV_CONFIGS[env_name]

def check_entity(entity: str) -> Optional[ValueError]:
    if entity not in ['agents', 'walls', 'doors', 'plates', 'goals', 'escapes']:
        raise ValueError(f"""
            Invalid entity passed.
            Valid entities include 'agents', 'walls', 'doors', 'plates', 'goals', or 'escapes'.
            Got entity={entity}.
        """)
    
def check_args():
    pass

def print_step(
        step: int
    ) -> None:
    print("##############")
    print(f"## STEP: {step} ##")
    print("##############")
    print()

def print_actions(
        actions: Dict
    ) -> None:
    print(f"ACTIONS: {actions}")
    print()

def print_results(
        reward: Dict,
        terminated: Dict,
        truncated: Dict
    ) -> None:
        print("AFTER ACTIONS")
        print(f"rewards: { {agent: round(reward, 2) for agent, reward in reward.items()} }")
        print(f"terminated: {terminated}")
        print(f"truncated: {truncated}")
        print()

def print_terminated(
        reward: Dict
    ) -> None:
    print("################")
    print("## TERMINATED ##")
    print("################")
    print()
    print(f"Total Rewards: { {agent: round(reward, 5) for agent, reward in reward.items()} }")

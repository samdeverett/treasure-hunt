from ray.rllib.env.multi_agent_env import MultiAgentEnv
from gymnasium import spaces
from actions import Actions
from assets import LAYOUTS, LAYERS
from ray.rllib.env.env_context import EnvContext
import numpy as np
from utils import check_entity
from entity import Agent, Plate, Door, Wall, Goal, Escape    # used in _reset_entity
from typing import Dict, Tuple
import sys


class MultiAgentPressurePlate(MultiAgentEnv):

    def __init__(self, env_config: EnvContext):
        super().__init__()

        self.layout = LAYOUTS[env_config['layout']]
        self.grid_size = (env_config['height'], env_config['width'])
        self.sensor_range = env_config['sensor_range']

        self.agents = [Agent(i, pos[0], pos[1]) for i, pos in enumerate(self.layout['AGENTS'])]
        self._agent_ids = [agent.id for agent in self.agents]

        self.action_space = spaces.Dict(
            {agent.id: spaces.Discrete(len(Actions)) for agent in self.agents}
        )
        self.observation_space = spaces.Dict(
            {agent.id: spaces.Box(
                # All values will be 0.0 or 1.0 other than an agent's position.
                low=0.0,
                # An agent's position is constrained by the size of the grid.
                high=float(max([self.grid_size[0], self.grid_size[1]])),
                # An agent can see the {sensor_range} units in each direction (including diagonally) around them,
                # meaning they can see a square grid of {sensor_range} * 2 + 1 units.
                # They have a grid of this size for each of the 6 entities: agents, walls, doors, plates, goals, and escapes.
                # Plus they know their own position, parametrized by 2 values.
                shape=((self.sensor_range * 2 + 1) * (self.sensor_range * 2 + 1) * 6 + 2,),
                dtype=np.float32
            ) for agent in self.agents}
        )

        # TODO use the gamma in PPOConfig.training
        self.gamma = 0.98

        self._rendering_initialized = False
        self.viewer = None

        # Set initial conditions.
        self.reset()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        
        # Wipe grid.
        self._wipe_grid()

        # Reset timesteps.
        # TODO use the timestep in algo
        self.timestep = 0

        # Put entities in their starting positions.
        self._reset_entity('agents')
        self._reset_entity('walls')
        self._reset_entity('doors')
        self._reset_entity('plates')
        self._reset_entity('goals')
        self._reset_entity('escapes')

        obs, info = {}, {}
        for agent in self.agents:
            obs[agent.id] = self._get_obs(agent)
            info[agent.id] = {}

        return obs, info

    def step(self, action_dict):

        # Take actions.
        for agent_id, action in action_dict.items():
            self.agents[agent_id].take_action(action, env=self)

        # Calculate reward.
        reward = {}
        for agent in self.agents:
            # Agents only get rewarded if they escape.
            if agent.escaped:
                reward[agent.id] = self._get_reward()
            else:
                reward[agent.id] = 0

        # Update environment by (1) opening doors for plates that are pressed and (2) updating goals that have been achieved.
        self._update_plates_and_doors()
        self._update_goals()
        # Check if any agents were crushed by doors closing.
        self._update_crushed_agents()

        # Get new observations for active agents.
        obs = {}
        for agent in self.agents:
            if not agent.escaped and not agent.crushed:
                obs[agent.id] = self._get_obs(agent)

        # Check for game termination, which happens when all agents escape or time runs out.
        # TODO update, see here for motivation: https://github.com/ray-project/ray/blob/master/rllib/examples/env/multi_agent.py
        terminated, truncated = {}, {}
        for agent in self.agents:
            terminated[agent.id] = agent.escaped or agent.crushed
            truncated[agent.id] = agent.escaped or agent.crushed
        terminated["__all__"] = np.all([terminated[agent.id] for agent in self.agents])
        truncated["__all__"] = np.all([truncated[agent.id] for agent in self.agents])
        # TODO use tune instead of train to handle this, but for now...
        if self.timestep > 100:
            terminated["__all__"] = True
            truncated["__all__"] = True

        # Pass info.
        info = {}
        for agent in self.agents:
            if not agent.escaped and not agent.crushed:
                info[agent.id] = {}

        # Increment timestep.
        self.timestep += 1

        return obs, reward, terminated, truncated, info

    def render(self, mode='human'):
        if not self._rendering_initialized:
            self._init_render()
        return self.viewer.render(self, mode == 'rgb_array')

    def _wipe_grid(self):
        self.grid = np.zeros((len(LAYERS), *self.grid_size))

    def _reset_entity(self, entity: str) -> None:
        check_entity(entity)
        # Reset entity to empty list.
        setattr(self, entity, [])
        # Get class of entity. See entity.py for class definitions.
        entity_class = getattr(sys.modules[__name__], entity[:-1].capitalize())    # taking away 's' at end of entity argument
        # Add values from assets.py to the grid.
        for id, pos in enumerate(self.layout[entity.upper()]):
            setattr(self, entity, getattr(self, entity) + [entity_class(id, pos[0], pos[1])])
            self.grid[LAYERS[entity], pos[1], pos[0]] = 1

    def _get_obs(self, agent: Agent):
        # When the agent's vision, as defined by self.sensor_range,
        # goes off of the grid, we pad the grid-version of the observation.
        # Get padding.
        padding = self._get_padding(agent)
        # Add padding.
        _agents  = self._pad_entity('agents' , padding)
        _walls   = self._pad_entity('walls'  , padding)
        _doors   = self._pad_entity('doors'  , padding)
        _plates  = self._pad_entity('plates' , padding)
        _goals   = self._pad_entity('goals'  , padding)
        _escapes = self._pad_entity('escapes', padding)
        # Concatenate grids.
        obs = np.concatenate((_agents, _walls, _doors, _plates, _goals, _escapes, np.array([agent.x, agent.y])), axis=0, dtype=np.float32)
        # Flatten and return.
        obs = np.array(obs).reshape(-1)
        return obs
    
    def _get_padding(self, agent: Agent) -> Dict:
        x, y = agent.x, agent.y
        pad = self.sensor_range * 2 // 2
        padding = {}
        padding['x_left'] = max(0, x - pad)
        padding['x_right'] = min(self.grid_size[1] - 1, x + pad)
        padding['y_up'] = max(0, y - pad)
        padding['y_down'] = min(self.grid_size[0] - 1, y + pad)
        padding['x_left_padding'] = pad - (x - padding['x_left'])
        padding['x_right_padding'] = pad - (padding['x_right'] - x)
        padding['y_up_padding'] = pad - (y - padding['y_up'])
        padding['y_down_padding'] = pad - (padding['y_down'] - y)
        return padding

    def _pad_entity(self, entity: str, padding: Dict) -> np.ndarray:
        check_entity(entity)
        # For all objects but walls, we pad with zeros.
        # For walls, we pad with ones, as edges of the grid act in the same way as walls.
        padding_fn = np.zeros
        if entity == 'walls':
            padding_fn = np.ones
        # Get grid for entity.
        entity_grid = self.grid[LAYERS[entity], padding['y_up']:padding['y_down'] + 1, padding['x_left']:padding['x_right'] + 1]
        # Pad left.
        entity_grid = np.concatenate((padding_fn((entity_grid.shape[0], padding['x_left_padding'])), entity_grid), axis=1)
        # Pad right.
        entity_grid = np.concatenate((entity_grid, padding_fn((entity_grid.shape[0], padding['x_right_padding']))), axis=1)
        # Pad up.
        entity_grid = np.concatenate((padding_fn((padding['y_up_padding'], entity_grid.shape[1])), entity_grid), axis=0)
        # Pad down.
        entity_grid = np.concatenate((entity_grid, padding_fn((padding['y_down_padding'], entity_grid.shape[1]))), axis=0)
        # Flatten and return.
        entity_grid = entity_grid.reshape(-1)
        return entity_grid
    
    def _update_plates_and_doors(self) -> None:
        agents_pos = [[agent.x, agent.y] for agent in self.agents]
        for plate in self.plates:
            plate_pos = [plate.x, plate.y]
            if np.any([plate_pos == agent_pos for agent_pos in agents_pos]):
                plate.pressed = True
                self.doors[plate.id].open = True
                plate.ever_pressed = True
            else:
                plate.pressed = False
                self.doors[plate.id].open = False
    
    def _update_goals(self) -> None:
        agents_pos = [[agent.x, agent.y] for agent in self.agents]
        for goal in self.goals:
            if not goal.achieved:    # only have to check goals that haven't been achieved
                goal_pos = [goal.x, goal.y]
                if np.any([goal_pos == agent_pos for agent_pos in agents_pos]):
                    goal.achieved = True

    def _update_crushed_agents(self):
        for agent in self.agents:
            if not agent.escaped and not agent.crushed:
                agent_pos = [agent.x, agent.y]
                closed_doors_pos = [[door.x, door.y] for door in self.doors if not door.open]
                for closed_door_pos in closed_doors_pos:
                    if agent_pos == closed_door_pos:
                        agent.crushed = True
                        break
    
    def _get_reward(self):
        # Agents who escape evenly split the total treasure they found.
        total_treasue = np.sum([agent.treasure for agent in self.agents if agent.escaped])
        n_escaped_agents = np.sum([agent.escaped for agent in self.agents])
        return total_treasue / n_escaped_agents
    
    def _init_render(self):
        from rendering import Viewer
        self.viewer = Viewer(self.grid_size)
        self._rendering_initialized = True

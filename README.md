**NOTE: under active refactor**

<div align="center">
  <img src="img/title.gif"
       height="250" width="250" />
</div>

A highly configurable multi-agent reinforcement learning environment with quality rendering.

<div align="center">
  <img src="img/cooperate.gif"
       height="250" width="250" />
</div>

## Story
*In collaboration with ChatGPT*

In a world brimming with undiscovered mysteries, agents embark on a thrilling quest to become master treasure hunters. They face any configuration of treasures, friends, foes, escapes, and hidden chambers guarded by pressure plates on the floor. Will your agents learn to unlock doors and unveil the precious treasures lie beyond or will they get trapped inside? Will they learn to cooperate or will they betray one another? Come along in this compelling adventure and watch as your agents strive to become the ultimate treasure hunters in this arbitrarily challenging world of hidden riches.

## About

Treasure Hunt is a [gymnasium](https://gymnasium.farama.org) environment that was made to support custom configurations of cooperative, competitive, and mixed-sum multi-agent games.

Agents are placed in a grid-world separated into chambers by walls. Some chambers are connected via locked doors in the walls. Each door is connected to a pressure plate on the ground and is unlocked when the pressure plate is stepped on. Agents are rewarded for navigating to the treasure and then finding an escape.

The configuration of the walls, doors, plates, treasures, escapes, agent starting locations, and agent reward functions determines whether the game is cooperative, competitive, or mixed. See [Customizing Scenarios](#customizing-scenarios) for more details.

This environment was adapted from [Trevor McInroe](https://github.com/trevormcinroe) and [Filippos Christianos'](https://github.com/semitable) [PressurePlate](https://github.com/uoe-agents/pressureplate) environment.

### Environment

#### Observation Space

#### Action Space

## Installation

1.  Clone Treasure Hunt:

    ```shell
    git clone -b main https://github.com/samdeverett/treasurehunt
    cd treasurehunt
    ```

2.  (Optional) Activate a Virtual Environment, e.g.:

    ```shell
    conda create -n treasurehunt python=3.9
    conda activate treasurehunt
    ```

3.  Install Requirements:

    ```shell
    pip install -r requirements.txt
    ```

## Usage

### Training Agents

### Rendering Game

## Customizing Scenarios

### Layout

### Reward Functions

## Citing Treasure Hunt

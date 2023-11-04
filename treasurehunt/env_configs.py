"""The configuration for each environment.

A configuration is a dictionary with four key-value pairs:
    'layout': str, layout of the grid world (from TODO)
    'height': int, height of grid world
    'width': int, width of grid world
    'sensor_range': int, number of grid units agents can observe in each direction
"""

ENV_CONFIGS = {

    'ExampleEnv': {
        'layout': 'CooperativeTwoAgent',
        'height': 7,
        'width': 9,
        'sensor_range': 5
    }

}

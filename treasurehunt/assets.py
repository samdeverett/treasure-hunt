"""
	For ease of use, please lay out your grid in Euclidean-plane format and NOT
	in numpy-type format. For example, if an object needs to be placed in the
	3rd row and 7th column of the gridworld numpy matrix, enter its location in your
	layout dict as [7,3]. The codebase will take care of the matrix-indexing for you.
	For example, the above object will be queried as grid[3, 7] when placed into the
	grid.

	NOTE: the origin (0,0) is the top-left corner of the grid. The positive direction
	along the x-axis counts to the right and the positive direction along the y-axis

"""

LAYOUTS = {

      'CooperativeTwoAgent': {
          
            'AGENTS': [
                  [3, 1],
                  [5, 1]
		],
        
		'WALLS': [
                  [0, 3],
                  [1, 3],
                  [2, 3],
                  [3, 3],
                  [4, 3],
                  [5, 3],
                  [7, 3],
                  [8, 3]
		],
        
		'DOORS': [
                  [6, 3]
		],
        
		'PLATES': [
                  [1, 1]
		],
        
		'GOALS': [
                  [6, 5]
		],
        
            'ESCAPES': [
                  [0, 0],
                  [5, 6],
                  [8, 0]
            ]

	},
    
}

LAYERS = {
    'agents': 0,
    'walls': 1,
    'doors': 2,
    'plates': 3,
    'goals': 4,
    'escapes': 5
}

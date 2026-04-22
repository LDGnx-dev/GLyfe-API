import random
import math
from datetime import datetime

def get_preset_pattern(pattern_name, default_w, default_h):
    """Devuelve (semillas, ancho, alto) según el patrón elegido"""

################ Glider preset ################
    
    if pattern_name == 'glider':
        return [(1,0), (2,1), (0,2), (1,2), (2,2)], default_w, default_h

################ Random Seed preset ################
    
    elif pattern_name == 'random':
        now = datetime.now()
        minute_block = math.floor(now.minute / 5) * 5
        time_seed = f"{now.strftime('%Y-%m-%d-%H')}-{minute_block}"
        random.seed(time_seed)

        num_cells = random.randint(70, 100)
        seeds = [(random.randint(0, default_w-1), random.randint(0, default_h-1)) for _ in range(num_cells)]
        random.seed() 
        
        return seeds, default_w, default_h

################ R-Pentomino preset ################
    
    elif pattern_name == 'r-pentomino':
        cx, cy = 26, 3
        return [(cx, cy-1), (cx+1, cy-1), (cx-1, cy), (cx, cy), (cx, cy+1)], default_w, default_h

################ Glider Factory preset ################
    
    elif pattern_name == 'gun':
        w, h = 40, 25
        gun = [
            (24, 1), (22, 2), (24, 2), (12, 3), (13, 3), (20, 3), (21, 3), (34, 3), (35, 3),
            (11, 4), (15, 4), (20, 4), (21, 4), (34, 4), (35, 4), (0, 5), (1, 5), (10, 5),
            (16, 5), (20, 5), (21, 5), (0, 6), (1, 6), (10, 6), (14, 6), (16, 6), (17, 6),
            (22, 6), (24, 6), (10, 7), (16, 7), (24, 7), (11, 8), (15, 8), (12, 9), (13, 9)
        ]
        return gun, w, h

    
return None, default_w, default_h

class LifeEngine:
    def __init__(self, width=52, height=7):
        self.width = width
        self.height = height

    def get_next_generation(self, current_cells):
        neighbors_count = {}
        
        for (x, y) in current_cells:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0: continue
                    # Cells can exceed borders
                    nx, ny = (x + dx) % self.width, (y + dy) % self.height
                    neighbors_count[(nx, ny)] = neighbors_count.get((nx, ny), 0) + 1

        next_cells = []
        for (pos, count) in neighbors_count.items():
            if count == 3 or (count == 2 and pos in current_cells):
                next_cells.append(pos)
                
        return next_cells

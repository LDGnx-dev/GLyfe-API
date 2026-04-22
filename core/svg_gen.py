import random
from collections import defaultdict
from core.engine import LifeEngine

def build_dynamic_svg(w, h, color):
    """
    Genera un SVG autónomo usando el Gynx Engine para calcular
    una simulación real y hornearla en animaciones CSS.
    """
    scale = 10  
    width_px = w * scale
    height_px = h * scale
    
    total_generations = 20     
    frame_duration = 0.8      
    dur_total = total_generations * frame_duration
    
    engine = LifeEngine(width=w, height=h)
    
    num_cells = int((w * h) * 0.15)
    current_gen = set((random.randint(0, w-1), random.randint(0, h-1)) for _ in range(num_cells))
    
    history = defaultdict(lambda: [0] * total_generations)
    
    for step in range(total_generations):
        for (x, y) in current_gen:
            history[(x, y)][step] = 1
            
        current_gen = engine.get_next_generation(current_gen)
        
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px} {height_px}" width="100%" height="100%">']
    

################################# SVG CSS Style #################################

    svg.append('''
    <style>
        .ecosystem {
            /* Aseguramos que rote y escale desde el centro exacto */
            transform-origin: center;
            
            /* Aplicamos DOS animaciones al mismo tiempo con duraciones desfasadas */
            animation: 
                breathe 25s ease-in-out infinite alternate,
                drift 40s ease-in-out infinite alternate;
        }
        
        /* Animación 1: El zoom suave que ya teníamos */
        @keyframes breathe {
            0% { transform: scale(1); }
            100% { transform: scale(1.1); }
        }
        
        /* Animación 2: Rotación de péndulo apenas visible (-1.5 a 1.5 grados) */
        @keyframes drift {
            0% { transform: rotate(-1.5deg); }
            100% { transform: rotate(1.5deg); }
        }
    </style>
    <g class="ecosystem">
    ''')
    
    for (x, y), states in history.items():
        if sum(states) == 0:
            continue
            
        x_px = x * scale
        y_px = y * scale
        
        opacities = ["0.9" if state == 1 else "0.05" for state in states]
        
        opacities.append(opacities[0])
        values_str = "; ".join(opacities)
        
        rect = f'''
        <rect x="{x_px}" y="{y_px}" width="{scale-1}" height="{scale-1}" fill="{color}" opacity="0.05">
            <animate attributeName="opacity" values="{values_str}" dur="{dur_total}s" repeatCount="indefinite"/>
        </rect>
        '''
        svg.append(rect)
        
    svg.append('</g></svg>')
    return "".join(svg)
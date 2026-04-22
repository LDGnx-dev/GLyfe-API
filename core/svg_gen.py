from core.engine import LifeEngine
from core.config import *
import random

def build_dynamic_svg(w, h, color):
    """
    Genera un SVG autónomo con semillas aleatorias, 
    Fade In/Out por célula y un Zoom In/Out global.
    """
    scale = 10
    width_px = w * scale
    height_px = h * scale
    
    num_cells = random.randint(int((w * h) * 0.10), int((w * h) * 0.25))
    seeds = set((random.randint(0, w-1), random.randint(0, h-1)) for _ in range(num_cells))
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px} {height_px}" width="100%" height="100%">'
    ]
    
    svg.append('''
    <style>
        .ecosystem {
            transform-origin: center;
            animation: breathe 25s ease-in-out infinite alternate;
        }
        @keyframes breathe {
            0% { transform: scale(1); }
            100% { transform: scale(1.1); /* Zoom in sutil del 10% */ }
        }
    </style>
    <g class="ecosystem">
    ''')
    
    for (x, y) in seeds:
        x_px = x * scale
        y_px = y * scale
        
        dur = round(random.uniform(3.0, 8.0), 1) 
        delay = round(random.uniform(0.0, 5.0), 1) 
        
        rect = f'''
        <rect x="{x_px}" y="{y_px}" width="{scale-1}" height="{scale-1}" fill="{color}" rx="2" opacity="0.1">
            <animate attributeName="opacity" values="0.1; 0.9; 0.1" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>
        </rect>
        '''
        svg.append(rect)
        
    svg.append('</g></svg>')
    return "".join(svg)
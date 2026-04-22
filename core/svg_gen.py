import random
from collections import defaultdict
from core.engine import LifeEngine

def build_dynamic_svg(w, h, color):
    """
    Genera un SVG autónomo usando el Gynx Engine para calcular
    una simulación real y hornearla en animaciones CSS.
    """
    scale = 10  # Tamaño de cada célula en píxeles
    width_px = w * scale
    height_px = h * scale
    
    # 1. Parámetros de la Simulación
    total_generations = 20     # Cuántos pasos del futuro vamos a calcular
    frame_duration = 0.5       # Segundos por cada generación (fluido pero relajado)
    dur_total = total_generations * frame_duration
    
    # 2. Inicializamos tu motor matemático
    engine = LifeEngine(width=w, height=h)
    
    # Plantamos la semilla inicial aleatoria (Densidad del 15% para que no se sature)
    num_cells = int((w * h) * 0.15)
    current_gen = set((random.randint(0, w-1), random.randint(0, h-1)) for _ in range(num_cells))
    
    # 3. El Libro de Historia (Aquí guardamos la vida de cada célula)
    # Por defecto, una célula empieza con una lista de ceros [0, 0, 0...]
    history = defaultdict(lambda: [0] * total_generations)
    
    # 4. LA MAGIA: Hacemos que el motor calcule el futuro
    for step in range(total_generations):
        # Anotamos quién está vivo en este paso
        for (x, y) in current_gen:
            history[(x, y)][step] = 1
            
        # Le pedimos a TU motor la siguiente generación
        current_gen = engine.get_next_generation(current_gen)
        
    # 5. Construimos el Lienzo SVG
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px} {height_px}" width="100%" height="100%">']
    
    # Añadimos el Efecto de Respiración / Zoom In global
    svg.append('''
    <style>
        .ecosystem {
            transform-origin: center;
            animation: breathe 20s ease-in-out infinite alternate;
        }
        @keyframes breathe {
            0% { transform: scale(1); }
            100% { transform: scale(1.08); /* Un zoom muy sutil y elegante */ }
        }
    </style>
    <g class="ecosystem">
    ''')
    
    # 6. Horneamos la historia en CSS
    for (x, y), states in history.items():
        if sum(states) == 0:
            continue
            
        x_px = x * scale
        y_px = y * scale
        
        # Convertimos la historia binaria [0, 1, 1, 0...] en opacidades reales
        # 1 = Brilla (0.9), 0 = Apagado (0.05)
        opacities = ["0.9" if state == 1 else "0.05" for state in states]
        
        # Truco de animación: Duplicamos el estado inicial al final para que el GIF (loop) sea perfecto
        opacities.append(opacities[0])
        values_str = "; ".join(opacities)
        
        # Inyectamos la línea de tiempo matemática directamente al SVG
        rect = f'''
        <rect x="{x_px}" y="{y_px}" width="{scale-1}" height="{scale-1}" fill="{color}" opacity="0.05">
            <animate attributeName="opacity" values="{values_str}" dur="{dur_total}s" repeatCount="indefinite"/>
        </rect>
        '''
        svg.append(rect)
        
    svg.append('</g></svg>')
    return "".join(svg)
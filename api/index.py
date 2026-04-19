import io
import requests
import random
from flask import Flask, Response
from PIL import Image, ImageDraw
from GofLyfe import LifeEngine

app = Flask(__name__)

# Configuración estética
BG_COLOR = (0, 0, 0, 0) # Transparente para GIFs
CELL_COLOR = "#bb9af7"
GRID_SIZE = 20 

def get_github_seeds():
    try:
        r = requests.get("https://api.github.com/users/LDGnx-dev/events")
        events = r.json()
        seeds = set()
        for e in events[:20]:
            event_id = int(e['id'])
            seeds.add((event_id % GRID_SIZE, (event_id // 10) % GRID_SIZE))
        return list(seeds)
    except:
        return [(random.randint(0, 19), random.randint(0, 19)) for _ in range(15)]

def generate_gif(seeds, frames=20, scale=10):
    engine = LifeEngine(size=GRID_SIZE)
    images = []
    current_gen = seeds

    for _ in range(frames):
        # Crear lienzo transparente
        img = Image.new('RGBA', (GRID_SIZE*scale, GRID_SIZE*scale), BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        for (x, y) in current_gen:
            x1, y1 = x * scale, y * scale
            x2, y2 = x1 + scale - 2, y1 + scale - 2
            # Dibujamos las células
            draw.rounded_rectangle([x1, y1, x2, y2], radius=2, fill=CELL_COLOR)
        
        images.append(img)
        current_gen = engine.get_next_generation(current_gen)

    # Convertir a binario
    out = io.BytesIO()
    # disposal=2 es crítico para que los fondos transparentes no se sobrepongan
    images[0].save(out, format='GIF', save_all=True, append_images=images[1:], 
                   duration=250, loop=0, disposal=2)
    return out.getvalue()

@app.route('/api/life.gif')
def game_of_life():
    seeds = get_github_seeds()
    gif_data = generate_gif(seeds)
    
    # DevOps Magic: Caché de 1 semana (604800 segundos)
    headers = {
        'Cache-Control': 'public, max-age=604800, s-maxage=604800'
    }
    return Response(gif_data, mimetype='image/gif', headers=headers)

if __name__ == "__main__":
    app.run()

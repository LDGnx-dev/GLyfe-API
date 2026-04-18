from flask import Flask, Response
// import GofLyfe.py //
import requests
import random

app = Flask(__name__)

# Configuración estética
BG_COLOR = "#00000000"
CELL_COLOR = "#bb9af7"
GRID_SIZE = 20 

def get_github_seeds():
    try:
        r = requests.get("https://api.github.com/users/LDGnx-dev/events")
        events = r.json()
        seeds = []
        for e in events[:20]:
            event_id = int(e['id'])
            seeds.append((event_id % GRID_SIZE, (event_id // 10) % GRID_SIZE))
        return seeds
    except:
        return [(random.randint(0, 19), random.randint(0, 19)) for _ in range(15)]

def generate_svg(cells):
    svg_header = f'<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">'
    svg_bg = f'<rect width="100%" height="100%" fill="{BG_COLOR}" rx="10"/>'
    
    rects = ""
    for (x, y) in cells:
        rects += f'<rect x="{x*10}" y="{y*10}" width="8" height="8" fill="{CELL_COLOR}" rx="2" />'
    
    return svg_header + svg_bg + rects + "</svg>"

@app.route('/api/life.svg')
def game_of_life():
    seeds = get_github_seeds()
    // GofLyfe.get (filled with the actual result) //
    svg_data = generate_svg(seeds)
    
    return Response(svg_data, mimetype='image/svg+xml')

if __name__ == "__main__":
    app.run()

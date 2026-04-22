import io
import os
import sys
import re
import random
from datetime import datetime

# (api/) added to the search
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from flask import Flask, Response, request, jsonify
from PIL import Image, ImageDraw

# Local and cloud functions
from GofLyfe import LifeEngine
from config import *

app = Flask(__name__)

# Local variables for testing purposes
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.environ.get('GITHUB_TOKEN')

# --- SECURITY FUNCTION (ANTI-INJECTION) ---
def sanitize_inputs(raw_user, raw_color):
    clean_user = re.sub(r'[^a-zA-Z0-9-]', '', str(raw_user))
    if not clean_user: 
        clean_user = GITHUB_USERNAME
        
    clean_color = re.sub(r'[^a-fA-F0-9]', '', str(raw_color))
    if not clean_color:
        clean_color = CELL_COLOR.replace('#', '')
        
    return clean_user, f"#{clean_color}"

# --- EASTER EGGS ENGINE (PRESETS) ---
def get_preset_pattern(pattern_name):
    """Devuelve (semillas, ancho, alto) según el patrón elegido"""
    if pattern_name == 'glider':
        return [(1,0), (2,1), (0,2), (1,2), (2,2)], GRID_WIDTH, GRID_HEIGHT
        
    elif pattern_name == 'random':
        today = datetime.now().strftime('%Y-%m-%d')
        random.seed(today) # Date as seed for random
        num_cells = random.randint(40, 100)
        seeds = [(random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1)) for _ in range(num_cells)]
        return seeds, GRID_WIDTH, GRID_HEIGHT
        
    elif pattern_name == 'r-pentomino':
        cx, cy = 26, 3
        return [(cx, cy-1), (cx+1, cy-1), (cx-1, cy), (cx, cy), (cx, cy+1)], GRID_WIDTH, GRID_HEIGHT
        
    elif pattern_name == 'gun':
        w, h = 40, 25
        gun = [
            (24, 1), (22, 2), (24, 2), (12, 3), (13, 3), (20, 3), (21, 3), (34, 3), (35, 3),
            (11, 4), (15, 4), (20, 4), (21, 4), (34, 4), (35, 4), (0, 5), (1, 5), (10, 5),
            (16, 5), (20, 5), (21, 5), (0, 6), (1, 6), (10, 6), (14, 6), (16, 6), (17, 6),
            (22, 6), (24, 6), (10, 7), (16, 7), (24, 7), (11, 8), (15, 8), (12, 9), (13, 9)
        ]
        return gun, w, h
        
    return None, GRID_WIDTH, GRID_HEIGHT


def get_contribution_matrix(target_user):
    query = """
    query { user(login: "%s") { contributionsCollection { contributionCalendar { weeks { contributionDays { contributionCount } } } } } }
    """ % target_user
    headers = {"Authorization": f"bearer {TOKEN}"}
    try:
        response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        weeks = response.json()['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        
        matrix = []
        for w_idx, week in enumerate(weeks):
            if w_idx >= GRID_WIDTH: break
            for d_idx, day in enumerate(week['contributionDays']):
                if day['contributionCount'] > 0: matrix.append((w_idx, d_idx))
        return matrix
    except Exception:
        return []

def generate_gif(seeds, target_color, w, h):
    # Initialized with the right dimension (normal or extended)
    engine = LifeEngine(width=w, height=h)
    images = []
    current_gen = seeds

    for _ in range(TOTAL_FRAMES):
        img = Image.new('RGBA', (w * CELL_SCALE, h * CELL_SCALE), BG_COLOR)
        draw = ImageDraw.Draw(img)
        for (x, y) in current_gen:
            x1, y1 = x * CELL_SCALE, y * CELL_SCALE
            x2, y2 = x1 + CELL_SCALE - 2, y1 + CELL_SCALE - 2
            draw.rounded_rectangle([x1, y1, x2, y2], radius=2, fill=target_color)
        images.append(img)
        current_gen = engine.get_next_generation(current_gen)

    out = io.BytesIO()
    images[0].save(out, format='GIF', save_all=True, append_images=images[1:], duration=FRAME_DURATION, loop=0, disposal=2)
    return out.getvalue()

# GIF generetad by the seed
@app.route('/api/life.gif')
def game_of_life():
    raw_user = request.args.get('user', GITHUB_USERNAME)
    raw_color = request.args.get('color', CELL_COLOR)
    req_pattern = request.args.get('pattern', None)
    
    # Secured enter
    req_user, req_color = sanitize_inputs(raw_user, raw_color)
    
    # Check for Easter Egg
    preset_seeds, active_w, active_h = get_preset_pattern(req_pattern)
    
    # GitHub read when no EEgg
    if preset_seeds is None:
        initial_cells = get_contribution_matrix(req_user)
    else:
        initial_cells = preset_seeds

    # GIF Cache value by type
    if req_pattern == 'random':
        cache_time = 5 # 5 seconds just for test purposes
       # cache_time = 300 # # 5 minutes
        wrapping = True 
    elif req_pattern is not None:
        cache_time = 604800  # 1 week
        wrapping = False
    else:
        cache_time = 86400  # 1 day (GitHub Commits)
        wrapping = True

    # GIF generate
    gif_data = generate_gif(initial_cells, req_color, active_w, active_h)

    # Reserved area for the cache controls
    # validate the time completition or not
    # to keep or clean cache 

    headers = {
        'Cache-Control': f'public, max-age={cache_time}, s-maxage={cache_time}'
    }
    return Response(gif_data, mimetype='image/gif', headers=headers)

# Initial seed preview
@app.route('/api/seed.png')
def debug_seed_image():
    raw_user = request.args.get('user', GITHUB_USERNAME)
    raw_color = request.args.get('color', CELL_COLOR)
    req_pattern = request.args.get('pattern', None)
    
    req_user, req_color = sanitize_inputs(raw_user, raw_color)
    preset_seeds, active_w, active_h = get_preset_pattern(req_pattern)
    
    if preset_seeds is None:
        initial_cells = get_contribution_matrix(req_user)
    else:
        initial_cells = preset_seeds

    img = Image.new('RGBA', (active_w * CELL_SCALE, active_h * CELL_SCALE), BG_COLOR)
    draw = ImageDraw.Draw(img)

    for (x, y) in initial_cells:
        x1, y1 = x * CELL_SCALE, y * CELL_SCALE
        x2, y2 = x1 + CELL_SCALE - 2, y1 + CELL_SCALE - 2
        draw.rounded_rectangle([x1, y1, x2, y2], radius=2, fill=req_color)
        
    out = io.BytesIO()
    img.save(out, format='PNG')
    return Response(out.getvalue(), mimetype='image/png', headers={'Cache-Control': 'no-cache'})

# API routes not found (404)
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({
        "error": "Ruta no encontrada",
        "mensaje": "El motor GynxLife solo procesa /api/life.gif y /api/seed.png",
        "status": 404
    }), 404

# GitHub errors
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "error": "Error interno del servidor",
        "mensaje": "Las células mutaron de forma inesperada. Revisa los logs.",
        "status": 500
    }), 500

if __name__ == "__main__":
    app.run()

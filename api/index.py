import io
import os
import sys

# (api/) added to the search
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from flask import Flask, Response, request
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

def get_contribution_matrix(target_user):
    query = """
    query {
      user(login: "%s") {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
              }
            }
          }
        }
      }
    }
    """ % target_user

    headers = {"Authorization": f"bearer {TOKEN}"}
    try:
        response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        data = response.json()
        weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        
        matrix = []
        for w_idx, week in enumerate(weeks):
            if w_idx >= GRID_WIDTH: break
            for d_idx, day in enumerate(week['contributionDays']):
                if day['contributionCount'] > 0:
                    matrix.append((w_idx, d_idx))
        return matrix
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def generate_gif(seeds, target_color):
    engine = LifeEngine(width=GRID_WIDTH, height=GRID_HEIGHT)
    images = []
    current_gen = seeds

    for _ in range(TOTAL_FRAMES):
        img = Image.new('RGBA', (GRID_WIDTH * CELL_SCALE, GRID_HEIGHT * CELL_SCALE), BG_COLOR)
        draw = ImageDraw.Draw(img)
        for (x, y) in current_gen:
            x1, y1 = x * CELL_SCALE, y * CELL_SCALE
            x2, y2 = x1 + CELL_SCALE - 2, y1 + CELL_SCALE - 2
            draw.rounded_rectangle([x1, y1, x2, y2], radius=2, fill=target_color)
        images.append(img)
        current_gen = engine.get_next_generation(current_gen)

    out = io.BytesIO()
    images[0].save(out, format='GIF', save_all=True, append_images=images[1:], 
                   duration=FRAME_DURATION, loop=0, disposal=2)
    return out.getvalue()

@app.route('/api/life.gif')
def game_of_life():
    # URL parameters or config.py (deafult user: LDGnx-dev)
    req_user = request.args.get('user', GITHUB_USERNAME)
    req_color = request.args.get('color', CELL_COLOR.replace('#', ''))
    
    if not req_color.startswith('#'):
        req_color = f"#{req_color}"
        
    # Data generator
    initial_cells = get_contribution_matrix(req_user)
    gif_data = generate_gif(initial_cells, req_color)
    
    # Dynamic cache (each URL has his own cache for 24 hours)
    headers = {'Cache-Control': 'public, max-age=86400, s-maxage=86400'}
    return Response(gif_data, mimetype='image/gif', headers=headers)

@app.route('/api/seed.png')
def debug_seed_image():
    # Diagnose Endpoint
    req_user = request.args.get('user', GITHUB_USERNAME)
    req_color = request.args.get('color', CELL_COLOR.replace('#', ''))
    
    if not req_color.startswith('#'):
        req_color = f"#{req_color}"
        
    initial_cells = get_contribution_matrix(req_user)
    img = Image.new('RGBA', (GRID_WIDTH * CELL_SCALE, GRID_HEIGHT * CELL_SCALE), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    for (x, y) in initial_cells:
        x1, y1 = x * CELL_SCALE, y * CELL_SCALE
        x2, y2 = x1 + CELL_SCALE - 2, y1 + CELL_SCALE - 2
        draw.rounded_rectangle([x1, y1, x2, y2], radius=2, fill=req_color)
        
    out = io.BytesIO()
    img.save(out, format='PNG')
    
    # No cache for fast tests
    return Response(out.getvalue(), mimetype='image/png', headers={'Cache-Control': 'no-cache'})

if __name__ == "__main__":
    app.run()
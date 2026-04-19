import io
import os
import requests
from flask import Flask, Response
from PIL import Image, ImageDraw
from api.GofLyfe import LifeEngine
from api.config import *

app = Flask(__name__)

# Local variables load
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.environ.get('GITHUB_TOKEN')

def get_contribution_matrix():
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
    """ % GITHUB_USERNAME

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

def generate_gif(seeds):
    engine = LifeEngine(width=GRID_WIDTH, height=GRID_HEIGHT)
    images = []
    current_gen = seeds

    for _ in range(TOTAL_FRAMES):
        img = Image.new('RGBA', (GRID_WIDTH * CELL_SCALE, GRID_HEIGHT * CELL_SCALE), BG_COLOR)
        draw = ImageDraw.Draw(img)
        for (x, y) in current_gen:
            x1, y1 = x * CELL_SCALE, y * CELL_SCALE
            x2, y2 = x1 + CELL_SCALE - 2, y1 + CELL_SCALE - 2
            draw.rounded_rectangle([x1, y1, x2, y2], radius=2, fill=CELL_COLOR)
        images.append(img)
        current_gen = engine.get_next_generation(current_gen)

    out = io.BytesIO()
    images[0].save(out, format='GIF', save_all=True, append_images=images[1:], 
                   duration=FRAME_DURATION, loop=0, disposal=2)
    return out.getvalue()

# GofLyfe GIF
@app.route('/api/life.gif')
def game_of_life():
    initial_cells = get_contribution_matrix()
    gif_data = generate_gif(initial_cells)
    headers = {'Cache-Control': 'public, max-age=86400, s-maxage=86400'}
    return Response(gif_data, mimetype='image/gif', headers=headers)

# GofLyfe First Generation PNG
@app.route('/api/seed.png')
def debug_seed_image():
    # GitHub Data
    initial_cells = get_contribution_matrix()
    
    # Map (52x7)
    img = Image.new('RGBA', (GRID_WIDTH * CELL_SCALE, GRID_HEIGHT * CELL_SCALE), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # First Gen drwawing
    for (x, y) in initial_cells:
        x1, y1 = x * CELL_SCALE, y * CELL_SCALE
        x2, y2 = x1 + CELL_SCALE - 2, y1 + CELL_SCALE - 2
        draw.rounded_rectangle([x1, y1, x2, y2], radius=2, fill=CELL_COLOR)
    
    # PNG gen
    out = io.BytesIO()
    img.save(out, format='PNG')
    
    headers = {'Cache-Control': 'no-cache'}
    return Response(out.getvalue(), mimetype='image/png', headers=headers)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

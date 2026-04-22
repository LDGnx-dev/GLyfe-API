import os
import sys
from flask import Flask, Response, request, jsonify, redirect

# Path main to found the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import *
from core.security import is_junk_request, sanitize_inputs
from core.utils import get_contribution_matrix
from data.patterns import get_preset_pattern
from core.gif_gen import generate_gif, generate_png
# from core.svg_gen import generate_background_svg

app = Flask(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.environ.get('GITHUB_TOKEN')

defaults = {
        'user': GITHUB_USERNAME,
        'color': CELL_COLOR,
        'w': GRID_WIDTH,
        'h': GRID_HEIGHT
    }

@app.route('/api/life.gif')
def game_of_life():


    allowed_keys = ['user', 'color', 'pattern', 'w', 'h']
    if is_junk_request(request.args, allowed_keys):
        return redirect('/assets/errors/404/404.html')


    u, c, w, h = sanitize_inputs(
        request.args.get('user'),
        request.args.get('color'),
        request.args.get('w'),
        request.args.get('h'),
        defaults
    )

    pattern_name = request.args.get('pattern')
    preset_seeds, active_w, active_h = get_preset_pattern(pattern_name, w, h)
    
    
    if preset_seeds is None:
        initial_cells = get_contribution_matrix(req_user, GRID_WIDTH, TOKEN)
    else:
        initial_cells = preset_seeds

    # Cache Logic
    if req_pattern == 'random':
      # cache_time = 3 # Test purposes only
       cache_time = 300 # 5 minutes
    elif req_pattern is not None:
        cache_time = 604800  # 1 week
    else:
        cache_time = 86400  # 1 day

    gif_data = generate_gif(
        initial_cells, req_color, active_w, active_h, 
        BG_COLOR, CELL_SCALE, TOTAL_FRAMES, FRAME_DURATION
    )

    headers = {'Cache-Control': f'public, max-age={cache_time}, s-maxage={cache_time}'}
    return Response(gif_data, mimetype='image/gif', headers=headers)

@app.route('/api/seed.png')
def debug_seed_image():

    
    allowed_keys = ['user', 'color', 'pattern', 'w', 'h']
    if is_junk_request(request.args, allowed_keys):
        return redirect('/assets/errors/404/404.html')


    raw_user = request.args.get('user', GITHUB_USERNAME)
    raw_color = request.args.get('color', CELL_COLOR)
    req_pattern = request.args.get('pattern', None)
    
    req_user, req_color = sanitize_inputs(raw_user, raw_color, GITHUB_USERNAME, CELL_COLOR)
    preset_seeds, active_w, active_h = get_preset_pattern(req_pattern, GRID_WIDTH, GRID_HEIGHT)
    
    if preset_seeds is None:
        initial_cells = get_contribution_matrix(req_user, GRID_WIDTH, TOKEN)
    else:
        initial_cells = preset_seeds

    png_data = generate_png(initial_cells, req_color, active_w, active_h, BG_COLOR, CELL_SCALE)
    return Response(png_data, mimetype='image/png', headers={'Cache-Control': 'no-cache'})

@app.errorhandler(404)
def resource_not_found(e):
    return redirect('/assets/errors/404/404.html')

@app.errorhandler(500)
def internal_server_error(e):
    return redirect('/assets/errors/500/500.html')

if __name__ == "__main__":
    app.run()
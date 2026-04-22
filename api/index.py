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
from core.svg_gen import build_dynamic_svg, build_bg_svg

app = Flask(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.environ.get('GITHUB_TOKEN')

################## SEED GIF ##################

@app.route('/api/life.gif')
def game_of_life():


    allowed_keys = ['user', 'color', 'pattern']
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

################## SEED PNG ##################

@app.route('/api/seed.png')
def debug_seed_image():

    
    allowed_keys = ['user', 'color', 'pattern']
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

################## SVG ##################

@app.route('/api/background.svg')
def background_svg():
    allowed_keys = ['w', 'h', 'color']
    if is_junk_request(request.args, allowed_keys):
        return redirect('/assets/errors/404.html')

    req_color = request.args.get('color', '#00FF00')
    
    try:
        req_w = min(max(int(request.args.get('w', 80)), 20), 200)
        req_h = min(max(int(request.args.get('h', 40)), 20), 200)
    except:
        req_w, req_h = 80, 40

    svg_data = build_dynamic_svg(req_w, req_h, req_color)
    
    cache_time = 5 # Test purposes only
    # cache_time = 1800

    headers = {'Cache-Control': f'public, max-age={cache_time}, s-maxage={cache_time}'}
    return Response(svg_data, mimetype='image/svg+xml', headers=headers)

################## SVG ##################

@app.route('/api/bg.svg')
def background_alternative():
    # 1. Atrapamos los parámetros de la URL con valores seguros por defecto
    try:
        req_w = int(request.args.get('w', 120))
        req_h = int(request.args.get('h', 60))
    except (ValueError, TypeError):
        req_w, req_h = 120, 60
        
    # Podemos probar con ese tono violeta/amatista para darle un toque increíble, 
    # o mantener el verde clásico si no mandan nada.
    req_color = request.args.get('color', '#a855f7') 
    
    # Si el usuario mandó el color sin el '#', se lo agregamos por seguridad
    if not req_color.startswith('#'):
        req_color = f'#{req_color}'

    # 2. Generamos el texto del SVG usando tu función
    svg_data = build_bg_svg(req_w, req_h, req_color)
    
    # 3. Lo empaquetamos como una imagen real con caché
    headers = {'Cache-Control': 'public, max-age=1800'} # 30 minutos de caché
    return Response(svg_data, mimetype='image/svg+xml', headers=headers)

@app.errorhandler(404)
def resource_not_found(e):
    return redirect('/assets/errors/404/404.html')

@app.errorhandler(500)
def internal_server_error(e):
    return redirect('/assets/errors/500/500.html')

if __name__ == "__main__":
    app.run()
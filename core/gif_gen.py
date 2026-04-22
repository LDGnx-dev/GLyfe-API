import io
from PIL import Image, ImageDraw
from core.engine import LifeEngine
from core.config import *

def generate_gif(seeds, target_color, w, h, bg_color, cell_scale, total_frames, frame_duration):
    engine = LifeEngine(width=w, height=h)
    images = []
    current_gen = seeds

    for _ in range(total_frames):
        img = Image.new('RGBA', (w * cell_scale, h * cell_scale), bg_color)
        draw = ImageDraw.Draw(img)
        for (x, y) in current_gen:
            x1, y1 = x * cell_scale, y * cell_scale
            x2, y2 = x1 + cell_scale - 2, y1 + cell_scale - 2
            draw.rounded_rectangle([x1, y1, x2, y2], radius=2, fill=target_color)
        images.append(img)
        current_gen = engine.get_next_generation(current_gen)

    out = io.BytesIO()
    images[0].save(out, format='GIF', save_all=True, append_images=images[1:], duration=frame_duration, loop=0, disposal=2)
    return out.getvalue()

def generate_png(seeds, target_color, w, h, bg_color, cell_scale):
    img = Image.new('RGBA', (w * cell_scale, h * cell_scale), bg_color)
    draw = ImageDraw.Draw(img)

    for (x, y) in seeds:
        x1, y1 = x * cell_scale, y * cell_scale
        x2, y2 = x1 + cell_scale - 2, y1 + cell_scale - 2
        draw.rounded_rectangle([x1, y1, x2, y2], radius=2, fill=target_color)
        
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()
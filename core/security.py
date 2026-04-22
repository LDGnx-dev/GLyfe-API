import re

def is_junk_request(request_args, allowed_keys):
    """
    Escudo Anti-Basura: Revisa si hay parámetros intrusos.
    Recibe el diccionario de parámetros de la URL y la lista VIP.
    Retorna True si hay basura, False si está limpio.
    """
    for param in request_args.keys():
        if param not in allowed_keys:
            return True
    return False

def sanitize_inputs(raw_user, raw_color, default_user, default_color):
    """
    Escudo Anti-Inyección y Buffer Overflow: 
    Limpia caracteres raros y limita la longitud extrema.
    """
    # GitHub have a username limit of 39 chars
    clean_user = re.sub(r'[^a-zA-Z0-9-]', '', str(raw_user))[:39]
    if not clean_user: 
        clean_user = default_user
        
    # HEX valid code dont need more tan 6 values
    clean_color = re.sub(r'[^a-fA-F0-9]', '', str(raw_color))[:6]
    if not clean_color:
        clean_color = default_color.replace('#', '')

    try:
        val_w = int(raw_w)
        clean_w = min(max(val_w, 10), 400) 
        
        val_h = int(raw_h)
        clean_h = min(max(val_h, 10), 400)
    except (ValueError, TypeError):
        clean_w = defaults['w']
        clean_h = defaults['h']


    return clean_user, f"#{clean_color}", clean_w, clean_h
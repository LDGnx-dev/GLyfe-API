import re
import requests

def sanitize_inputs(raw_user, raw_color, default_user, default_color):
    clean_user = re.sub(r'[^a-zA-Z0-9-]', '', str(raw_user))
    if not clean_user: 
        clean_user = default_user
        
    clean_color = re.sub(r'[^a-fA-F0-9]', '', str(raw_color))
    if not clean_color:
        clean_color = default_color.replace('#', '')
        
    return clean_user, f"#{clean_color}"

def get_contribution_matrix(target_user, limit_w, token):
    query = """
    query { user(login: "%s") { contributionsCollection { contributionCalendar { weeks { contributionDays { contributionCount } } } } } }
    """ % target_user
    headers = {"Authorization": f"bearer {token}"}
    try:
        response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        weeks = response.json()['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        
        matrix = []
        for w_idx, week in enumerate(weeks):
            if w_idx >= limit_w: break
            for d_idx, day in enumerate(week['contributionDays']):
                if day['contributionCount'] > 0: matrix.append((w_idx, d_idx))
        return matrix
    except Exception:
        return []
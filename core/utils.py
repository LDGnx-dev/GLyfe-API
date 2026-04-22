import re
import requests

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
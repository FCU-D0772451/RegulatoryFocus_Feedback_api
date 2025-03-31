from flask import jsonify
from scipy.stats import t

def handle_ttest(request):
    data = request.get_json()
    p_value = data['p_value']
    n = data['n']
    
    df = 2 * (n - 1)
    t_value = t.ppf(1 - p_value / 2, df)
    
    response = jsonify({'t_value': t_value})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
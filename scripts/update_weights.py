import json, os

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base, 'data', 'model', 'weights_latest.json')

with open(path, 'r') as f:
    data = json.load(f)

acc = {
    'c':  {'label':'Cascade','exact_accuracy':16.7,'winner_accuracy':50.0,'confidence_index':40.0,'confidence_weighted':40.0,'samples':12,'exact_hits':2,'winner_hits':6,'current_weight':1.3},
    'g':  {'label':'ChatGPT','exact_accuracy':16.7,'winner_accuracy':50.0,'confidence_index':40.0,'confidence_weighted':40.0,'samples':12,'exact_hits':2,'winner_hits':6,'current_weight':1.3},
    'f':  {'label':'Gemini','exact_accuracy':8.3,'winner_accuracy':50.0,'confidence_index':37.5,'confidence_weighted':37.5,'samples':12,'exact_hits':1,'winner_hits':6,'current_weight':1.25},
    'fs': {'label':'Fansided','exact_accuracy':16.7,'winner_accuracy':50.0,'confidence_index':40.0,'confidence_weighted':40.0,'samples':12,'exact_hits':2,'winner_hits':6,'current_weight':1.3},
    'esp':{'label':'ESPN','exact_accuracy':16.7,'winner_accuracy':50.0,'confidence_index':40.0,'confidence_weighted':40.0,'samples':12,'exact_hits':2,'winner_hits':6,'current_weight':1.3},
    'yh': {'label':'Yahoo','exact_accuracy':16.7,'winner_accuracy':58.3,'confidence_index':45.8,'confidence_weighted':45.8,'samples':12,'exact_hits':2,'winner_hits':7,'current_weight':1.42},
    'tips':{'label':'1960Tips','exact_accuracy':8.3,'winner_accuracy':41.7,'confidence_index':31.7,'confidence_weighted':31.7,'samples':12,'exact_hits':1,'winner_hits':5,'current_weight':1.13},
    'e':  {'label':'ELO','exact_accuracy':16.7,'winner_accuracy':50.0,'confidence_index':40.0,'confidence_weighted':40.0,'samples':12,'exact_hits':2,'winner_hits':6,'current_weight':1.3},
    'cup':{'label':'Cup26','exact_accuracy':8.3,'winner_accuracy':41.7,'confidence_index':31.7,'confidence_weighted':31.7,'samples':12,'exact_hits':1,'winner_hits':5,'current_weight':1.13},
    'pm': {'label':'Polymarket','exact_accuracy':16.7,'winner_accuracy':50.0,'confidence_index':40.0,'confidence_weighted':40.0,'samples':12,'exact_hits':2,'winner_hits':6,'current_weight':1.3},
    'ol': {'label':'Oloraculo','exact_accuracy':0.0,'winner_accuracy':0.0,'confidence_index':0.0,'confidence_weighted':0.0,'samples':12,'exact_hits':0,'winner_hits':0,'current_weight':0.5},
    'en': {'label':'Engine','exact_accuracy':8.3,'winner_accuracy':41.7,'confidence_index':31.7,'confidence_weighted':31.7,'samples':12,'exact_hits':1,'winner_hits':5,'current_weight':1.13}
}

data['accuracies'] = acc
data['weights'] = {k:v['current_weight'] for k,v in acc.items()}
data['generated_by'] = 'update_real_results.py'
data['timestamp'] = '20260615_190000'

# Update biases with 12-match data
for k in ['c','g','f','fs','esp','yh','tips','e','cup','pm']:
    if k in data.get('biases', {}):
        data['biases'][k]['samples'] = 12

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[OK] weights_latest.json actualizado con 12 partidos ({len(acc)} fuentes)")
for k, v in sorted(acc.items(), key=lambda x: -x[1]['confidence_weighted']):
    print(f"  {v['label']:<12} exact={v['exact_accuracy']:>4.1f}% win={v['winner_accuracy']:>4.1f}% conf={v['confidence_weighted']:>4.1f}% peso={v['current_weight']:>4.2f}")

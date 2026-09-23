import re

def norm(s): return re.sub(r'\s+',' ',str(s or '').strip()).upper()

def validate(pred, context):
    defs={norm(x['characteristic']):x for x in context['characteristics']}
    clean={}; errors=[]
    for k,v in (pred.get('characteristics') or {}).items():
        nk=norm(k); nv=norm(v)
        if nk not in defs:
            errors.append(f'Unknown characteristic: {k}')
            continue
        d=defs[nk]
        if d['open_close'].lower().startswith('close'):
            allowed={norm(x):x for x in d['possible_values']}
            if nv not in allowed:
                errors.append(f'Invalid closed value for {k}: {v!r}; allowed={d["possible_values"]}')
                continue
            clean[d['characteristic']]=allowed[nv]
        else:
            clean[d['characteristic']]=str(v).strip()
    return clean,errors

def missing_characteristics(pred, context):
    got={norm(k) for k in (pred.get('characteristics') or {})}
    return [x['characteristic'] for x in context['characteristics'] if norm(x['characteristic']) not in got]

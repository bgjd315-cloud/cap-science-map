# Check every tools/data/<year>.json against the official key and the writing rules.
# Usage: python -X utf8 tools/lint.py        (exit code 1 if anything is wrong)
import json, os, re, sys
TOOLS = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(TOOLS, 'data')
K = json.load(open(os.path.join(D, 'key.json'), encoding='utf-8'))
U = json.load(open(os.path.join(D, 'units.json'), encoding='utf-8'))
years = sorted(f[:3] for f in os.listdir(D) if re.fullmatch(r'\d{3}\.json', f))
bad = []

def strings(o, path=''):
    if isinstance(o, str): yield path, o
    elif isinstance(o, dict):
        for k, v in o.items(): yield from strings(v, path + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from strings(v, path + f'[{i}]')

for y in years:
    R = json.load(open(os.path.join(D, f'{y}.json'), encoding='utf-8'))
    if len(R) != 50: bad.append((y, 'expected 50 records', len(R)))
    for d in R:
        tag = f"{y}-{d['no']}"; t = d.get('detail') or {}
        if d['exam'] not in ('生物', '理化', '地科'): bad.append((tag, 'exam')); continue
        if d.get('type') not in ('單題', '題組'): bad.append((tag, 'type'))
        if True:
            if y not in K: bad.append((tag, 'year missing from key.json')); continue
            if d['answer'].strip('()') != K[y]['ans'][d['no']]: bad.append((tag, 'answer != official key'))
            if abs(d['rate'] - float(K[y]['pass'][d['no']])) > 1e-9: bad.append((tag, 'rate != official pass rate'))
            want = '易' if d['rate'] >= .70 else '中' if d['rate'] >= .45 else '難'
            if d['difficulty'] != want: bad.append((tag, 'difficulty', d['difficulty'], want))
        if d['unit'] not in U: bad.append((tag, 'unit'))
        rd = t.get('read', {})
        if not (rd.get('given') and rd.get('ask') and 2 <= len(rd.get('keys', [])) <= 4): bad.append((tag, 'read'))
        if not 2 <= len(t.get('crack', [])) <= 4: bad.append((tag, 'crack'))
        if not 1 <= len(t.get('concepts', [])) <= 3: bad.append((tag, 'concepts'))
        st = t.get('steps', [])
        if not 3 <= len(st) <= 6 or any(not s.get('hint') or not s.get('calc') for s in st): bad.append((tag, 'steps'))
        for p, s in strings(d):
            if re.search(r'[\x00-\x1f]', s): bad.append((tag, 'control char (bad escape?)', p))
            if s.count('$') % 2: bad.append((tag, 'unbalanced $', p))
            if '座標' in s: bad.append((tag, '座標→坐標', p))
            if p.endswith('.tex') or '.vars' in p:
                if '/' in re.sub(r'\\text\{[^}]*\}|\^\{[^}]*\}', '', s): bad.append((tag, 'slash in tex', p))
                continue
            if re.search('[√²³½⁻⁺₂₃₄]', re.sub(r'\$[^$]*\$', '', s)): bad.append((tag, 'unicode math outside $', p))
            for m in re.findall(r'\$([^$]*)\$', s):
                if '/' in re.sub(r'\\text\{[^}]*\}|\^\{[^}]*\}', '', m): bad.append((tag, '/ inside $…$', p))
                if '\\frac' in m.replace('\\dfrac', ''): bad.append((tag, '\\frac (use \\dfrac)', p))

print(len(years), 'years:', ', '.join(years), '| problems:', len(bad))
for b in bad[:60]: print(' ', b)
sys.exit(1 if bad else 0)

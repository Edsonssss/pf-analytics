#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Публикация папки publish/ в новый публичный репозиторий GitHub + включение Pages.

Использование:
    GH_TOKEN=ghp_xxx python3 deploy_github.py [имя-репозитория]

Токен нигде не сохраняется: передаётся через переменную окружения, в .git/config
после пуша подставляется заглушка.
"""
import json, os, subprocess, sys, time, urllib.request, urllib.error

REPO = (sys.argv[1] if len(sys.argv) > 1 else 'portfolio-analytics').strip()
TOKEN = os.environ.get('GH_TOKEN', '').strip()
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'publish')
if not TOKEN:
    sys.exit('Нужен токен: GH_TOKEN=... python3 deploy_github.py')

def api(method, path, body=None, host='https://api.github.com'):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(host + path, data=data, method=method,
                                headers={'Authorization': 'token ' + TOKEN,
                                         'Accept': 'application/vnd.github+json',
                                         'User-Agent': 'portfolio-analytics-deploy',
                                         'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {'message': raw[:400]}

def run(cmd, cwd=SRC, check=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        print('CMD FAIL:', ' '.join(cmd), '\n', p.stdout, p.stderr)
        sys.exit(1)
    return p

# 1) кто я
st, me = api('GET', '/user')
if st != 200:
    sys.exit(f'Токен не принят (HTTP {st}): {me.get("message")}')
login = me['login']
print(f'✓ токен валиден, аккаунт: {login}')

# 2) создаём репозиторий (или используем существующий)
st, r = api('POST', '/user/repos', {
    'name': REPO,
    'description': 'Технический анализ портфеля: 25 бумаг + IMOEX (данные торгов 16.10.2026)',
    'private': False, 'has_issues': False, 'has_wiki': False, 'auto_init': False})
if st in (200, 201):
    print(f'✓ репозиторий создан: {r["full_name"]}')
elif st == 422 and 'already exists' in json.dumps(r):
    print(f'· репозиторий уже существует: {login}/{REPO} — пушу в него')
else:
    sys.exit(f'Не удалось создать репозиторий (HTTP {st}): {r.get("message")} {r.get("errors", "")}')

remote = f'https://x-access-token:{TOKEN}@github.com/{login}/{REPO}.git'
run(['git', 'remote', 'remove', 'origin'], check=False)
run(['git', 'remote', 'add', 'origin', remote])
p = run(['git', 'push', '-u', 'origin', 'main', '--force'], check=False)
print('✓ push:', (p.stderr or p.stdout).strip().splitlines()[-1:] or 'ok')
# вычищаем токен из конфига
run(['git', 'remote', 'set-url', 'origin', f'https://github.com/{login}/{REPO}.git'])
print('✓ токен удалён из .git/config')

# 3) включаем GitHub Pages
st, pg = api('POST', f'/repos/{login}/{REPO}/pages', {'source': {'branch': 'main', 'path': '/'}})
if st in (200, 201):
    print('✓ Pages включён')
elif st == 409:
    st, pg = api('PUT', f'/repos/{login}/{REPO}/pages', {'source': {'branch': 'main', 'path': '/'}})
    print('· Pages уже был включён, обновил настройки:', st)
else:
    print(f'! Pages не включился автоматически (HTTP {st}): {pg.get("message")}'
          f'\n  Включите вручную: Settings → Pages → Branch: main / (root) → Save')

url = f'https://{login}.github.io/{REPO}/'
print('\n=== ГОТОВО ===')
print('Репозиторий :', f'https://github.com/{login}/{REPO}')
print('Сайт        :', url)
print('Сводная     :', url + 'summary.html')
print('IMOEX       :', url + 'imoex.html')

# 4) ждём сборки Pages
for i in range(20):
    time.sleep(15)
    st, b = api('GET', f'/repos/{login}/{REPO}/pages/builds/latest')
    status = b.get('status') if st == 200 else None
    print(f'  сборка Pages: {status or "ожидает"} ({(i+1)*15} c)')
    if status == 'built':
        print('✓ сайт опубликован:', url)
        break
else:
    print('· сборка ещё идёт — проверьте через пару минут:', url)

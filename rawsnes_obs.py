#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAW-SNES OBS Companion: independent RetroAchievements-to-OBS notifier.

Adapted from the MIT-licensed MegaRaw OBS Companion maintained by
HeresAChallenger. This program does not read, modify, or bundle RAW-SNES.
Standard-library-only; Windows DPAPI is used for persisted secrets.
"""
from __future__ import annotations

import argparse
import base64
import ctypes
import getpass
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from collections import deque
from ctypes import wintypes
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_HOME = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'RawSNESObsOverlay'
CONFIG_PATH = DATA_HOME / 'config_local.json'
LOG_PATH = DATA_HOME / 'integracao.log'
SOUND_PATH = HERE / 'som_alerta.wav'
PORT = 8766   # different from MegaRaw OBS Companion's 8765
API_URL = 'https://retroachievements.org/API/API_GetUserRecentAchievements.php'
RA_ORIGIN = 'https://retroachievements.org'
LOCK = threading.RLock()


class State:
    def __init__(self):
        self.seq = 0
        self.events = deque(maxlen=120)
        self.username = ''
        self.status = 'Inicializando'
        self.online = False
        self.last_check = ''
        self.last_unlock = ''
        self.error = ''
        self.interval = 5

    def emit(self, event):
        with LOCK:
            self.seq += 1
            result = {'seq': self.seq, **event}
            self.events.append(result)
            self.last_unlock = result['title']
            return result


STATE = State()


def log(message):
    text = f'[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}'
    print(text, flush=True)
    try:
        DATA_HOME.mkdir(parents=True, exist_ok=True)
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > 800_000:
            LOG_PATH.replace(DATA_HOME / 'integracao_anterior.log')
        with LOG_PATH.open('a', encoding='utf-8') as stream:
            stream.write(text + '\n')
    except OSError:
        pass


def dpapi(secret: str | bytes, decrypt=False) -> str:
    """Protect/decrypt using the logged-in Windows user's DPAPI scope."""
    if sys.platform != 'win32':
        raise RuntimeError('A configuração permanente requer DPAPI do Windows.')

    class BLOB(ctypes.Structure):
        _fields_ = [('cbData', wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_ubyte))]

    value = base64.b64decode(secret, validate=True) if decrypt else secret.encode('utf-8')
    buffer = (ctypes.c_ubyte * len(value)).from_buffer_copy(value)
    src = BLOB(len(value), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    dest = BLOB()
    crypto = ctypes.WinDLL('Crypt32', use_last_error=True)
    kernel = ctypes.WinDLL('Kernel32', use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if decrypt:
        crypto.CryptUnprotectData.argtypes = [ctypes.POINTER(BLOB), ctypes.c_void_p,
                                               ctypes.c_void_p, ctypes.c_void_p,
                                               ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(BLOB)]
        crypto.CryptUnprotectData.restype = wintypes.BOOL
        success = crypto.CryptUnprotectData(ctypes.byref(src), None, None, None,
                                             None, 1, ctypes.byref(dest))
    else:
        crypto.CryptProtectData.argtypes = [ctypes.POINTER(BLOB), wintypes.LPCWSTR,
                                             ctypes.c_void_p, ctypes.c_void_p,
                                             ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(BLOB)]
        crypto.CryptProtectData.restype = wintypes.BOOL
        success = crypto.CryptProtectData(ctypes.byref(src), 'RAW-SNES OBS Companion',
                                            None, None, None, 1, ctypes.byref(dest))
    if not success:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        content = ctypes.string_at(dest.pbData, dest.cbData)
        return content.decode('utf-8') if decrypt else base64.b64encode(content).decode('ascii')
    finally:
        kernel.LocalFree(ctypes.cast(dest.pbData, ctypes.c_void_p))


def load_account():
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
        return data['usuario'], dpapi(data['chave_api_protegida'], decrypt=True)
    print('\nCONFIGURAÇÃO — RAW-SNES OBS Companion')
    print('Entre com sua conta e a WEB API KEY de https://retroachievements.org/controlpanel.php')
    print('Não use o campo ra_token do rawsnes_config.json: é uma credencial diferente.')
    print('A chave será protegida localmente com o DPAPI do Windows e não será enviada ao OBS.\n')
    username = input('Usuário do RetroAchievements: ').strip()
    web_key = getpass.getpass('Web API Key (oculta): ').strip()
    if not username or not web_key:
        raise ValueError('Usuário e Web API Key são obrigatórios.')
    DATA_HOME.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps({'usuario': username,
                                      'chave_api_protegida': dpapi(web_key)},
                                     indent=2, ensure_ascii=False), encoding='utf-8')
    return username, web_key


def field(item, camel, pascal, default=None):
    return item.get(pascal, item.get(camel, default))


def is_snes(item):
    console = str(field(item, 'consoleName', 'ConsoleName', '')).strip().casefold()
    return ('super nintendo' in console or 'super famicom' in console
            or console == 'snes' or console.startswith('snes /')
            or console.startswith('snes/'))


def identity(item):
    return (str(field(item, 'achievementId', 'AchievementID', '')),
            str(field(item, 'date', 'Date', '')),
            str(field(item, 'hardcoreMode', 'HardcoreMode', 0)))


def badge_url(item):
    name = str(field(item, 'badgeName', 'BadgeName', '') or '')
    path = field(item, 'badgeUrl', 'BadgeURL', '')
    if not path and name and all(c.isalnum() or c in '_-' for c in name):
        path = '/Badge/' + name + '.png'
    if not path:
        return ''
    value = urllib.parse.urljoin(RA_ORIGIN, str(path))
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != 'https' or parsed.hostname not in ('retroachievements.org',
                                                             'media.retroachievements.org'):
        return ''
    return value


def to_event(item):
    try:
        points = max(0, int(field(item, 'points', 'Points', 0) or 0))
    except (ValueError, TypeError):
        points = 0
    hardcore = str(field(item, 'hardcoreMode', 'HardcoreMode', 0)).lower() in ('true', '1')
    return {'title': str(field(item, 'title', 'Title', 'Conquista desbloqueada'))[:170],
            'description': str(field(item, 'description', 'Description', ''))[:300],
            'game': str(field(item, 'gameTitle', 'GameTitle', 'Super Nintendo'))[:160],
            'points': points, 'badge': badge_url(item), 'hardcore': hardcore,
            'test': False,
            'achievement_id': str(field(item, 'achievementId', 'AchievementID', ''))}


def fetch_recent(username, web_key):
    query = urllib.parse.urlencode({'u': username, 'y': web_key, 'm': 60})
    req = urllib.request.Request(API_URL + '?' + query,
                                 headers={'User-Agent': 'RAW-SNES-OBS-Companion/1.0 (local)',
                                          'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read(2_000_000).decode('utf-8'))
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise RuntimeError('Limite da API atingido (HTTP 429): aumente o intervalo.') from None
        raise RuntimeError(f'Erro HTTP {exc.code} da API.') from None
    except urllib.error.URLError:
        raise RuntimeError('Falha ao consultar RetroAchievements. Verifique a internet.') from None
    if not isinstance(data, list):
        raise RuntimeError('Resposta inesperada da API; confira usuário e Web API Key.')
    return data


def poll_loop(username, web_key, stop=None):
    stop = stop or threading.Event()
    known = set()
    first = True
    failures = 0
    while not stop.is_set():
        try:
            events = [e for e in fetch_recent(username, web_key) if is_snes(e)]
            fresh = [e for e in events if identity(e) not in known]
            if first:
                first = False
                known.update(map(identity, events))
                log(f'Conexão ativa: ignorando {len(known)} desbloqueios anteriores de SNES.')
            else:
                for record in reversed(fresh[:40]):
                    STATE.emit(to_event(record))
                    log('Conquista SNES confirmada: ' + str(field(record, 'title', 'Title', '?'))[:170])
                known.update(map(identity, events))
            if len(known) > 2000:
                known = set(map(identity, events))
            with LOCK:
                STATE.online = True
                STATE.status = 'Monitorando conquistas do SNES'
                STATE.last_check = datetime.now().strftime('%H:%M:%S')
                STATE.error = ''
            failures = 0
            stop.wait(STATE.interval)
        except Exception as exc:
            failures += 1
            with LOCK:
                STATE.online = False
                STATE.status = 'Aguardando API'
                STATE.error = str(exc)[:180]
            log('Aviso: ' + str(exc)[:180])
            stop.wait(min(300, max(15, STATE.interval) * 2 ** min(failures, 4)))


OVERLAY = r'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box}html,body{width:100%;height:100%;margin:0;background:transparent!important;overflow:hidden;font-family:Segoe UI,Arial,sans-serif}
#host{position:absolute;top:8px;left:8px;width:476px;height:132px;pointer-events:none}
.toast{position:absolute;inset:0;display:flex;align-items:center;gap:13px;padding:16px 14px 16px 18px;border:1px solid rgba(190,160,255,.5);border-radius:15px;background:linear-gradient(120deg,rgba(29,27,46,.98),rgba(13,13,24,.98));color:#fff;box-shadow:0 10px 24px rgba(0,0,0,.45),inset 0 1px rgba(255,255,255,.12);overflow:hidden;animation:flyin .48s cubic-bezier(.2,1.4,.28,1) both}
.toast::before{content:'';position:absolute;inset:-25px;background:linear-gradient(115deg,transparent 25%,rgba(198,173,255,.14) 47%,transparent 60%);transform:translateX(-105%);animation:glint .9s .35s ease-out forwards;pointer-events:none}
.icon{width:83px;height:83px;flex:0 0 83px;object-fit:cover;border:2px solid #9d86e4;background:#151323;border-radius:10px}
.fallback{display:flex;align-items:center;justify-content:center;font-size:42px}
.middle{min-width:0;flex:1;z-index:1}
.eyebrow{font-size:10px;letter-spacing:1.2px;color:#d6bcff;font-weight:800;margin-bottom:5px}
.title{font-size:16px;font-weight:800;line-height:1.18;max-height:39px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.description{font-size:11px;color:#c6c4d4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:5px}
.game{font-size:10px;color:#a8a9c3;margin-top:8px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.points{font-size:12px;align-self:flex-start;white-space:nowrap;color:#e6ccff;font-weight:800;margin-top:2px}
.out{animation:flyout .42s ease-in forwards}
@keyframes flyin{from{transform:translateX(490px);opacity:0}to{transform:translateX(0);opacity:1}}
@keyframes flyout{from{transform:translateX(0);opacity:1}to{transform:translateX(490px);opacity:0}}
@keyframes glint{to{transform:translateX(125%)}}
</style></head><body><div id="host" aria-live="polite"></div><audio id="alertAudio" src="/audio/alert.wav" preload="auto"></audio>
<script>
'use strict';let last=0,ready=false,queue=[],busy=false,fetching=false;
const host=document.getElementById('host'),sound=document.getElementById('alertAudio');
const withSound=new URLSearchParams(location.search).get('som')!=='0';
function playAlert(){if(!withSound)return;try{sound.pause();sound.currentTime=0;const p=sound.play();if(p&&p.catch)p.catch(()=>{});}catch(e){}}
async function boot(){try{const s=await(await fetch('/api/status',{cache:'no-store'})).json();last=s.seq||0;ready=true;setInterval(check,250);}catch(e){setTimeout(boot,1000)}}
async function check(){if(!ready||fetching)return;fetching=true;try{const r=await fetch('/api/events?after='+last,{cache:'no-store'});if(!r.ok)throw Error(r.status);const data=await r.json();for(const e of data.events){last=Math.max(last,e.seq);queue.push(e)}if(!busy)next()}catch(e){}finally{fetching=false}}
function next(){if(!queue.length){busy=false;return}busy=true;const ev=queue.shift();playAlert();const card=document.createElement('div');card.className='toast';
let icon;if(ev.badge){icon=document.createElement('img');icon.className='icon';icon.src=ev.badge;icon.alt='Emblema';icon.onerror=()=>{const f=document.createElement('div');f.className='icon fallback';f.textContent='🏆';icon.replaceWith(f)}}else{icon=document.createElement('div');icon.className='icon fallback';icon.textContent='🏆'}card.appendChild(icon);
const middle=document.createElement('div');middle.className='middle';for(const [cls,value] of [['eyebrow',ev.test?'TESTE DE ALERTA':'ACHIEVEMENT UNLOCKED!'],['title',ev.title],['description',ev.description||'Conquista desbloqueada'],['game',ev.game+(ev.hardcore?' · Hardcore':' · Softcore')]]){const el=document.createElement('div');el.className=cls;el.textContent=value;middle.appendChild(el)}card.appendChild(middle);
const pts=document.createElement('div');pts.className='points';pts.textContent='+'+ev.points+' pts';card.appendChild(pts);host.appendChild(card);
setTimeout(()=>{card.classList.add('out');setTimeout(()=>{card.remove();next()},450)},5800)}boot();
</script></body></html>'''

PANEL = r'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RAW-SNES OBS Companion</title>
<style>body{background:#141223;color:#f4f1ff;font:15px Segoe UI,Arial,sans-serif;max-width:740px;margin:40px auto;padding:0 18px;line-height:1.5}h1{font-size:27px}p{color:#c8c1d9}article{background:#201e32;border:1px solid #433d60;padding:20px;border-radius:12px;margin-bottom:16px}button{background:#7660bf;color:#fff;border:0;padding:12px 17px;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer}button:hover{background:#9a7ff3}pre{padding:14px;border:1px solid #564e73;border-radius:8px;white-space:pre-wrap;color:#d9caff}small{color:#c4b7dc}.state{color:#b0ffd9;font-weight:700}a{color:#b8c9ff}</style>
</head><body><h1>RAW-SNES OBS Companion</h1><p>Alertas do RetroAchievements para o OBS — Super Nintendo / Super Famicom.</p>
<article><strong>Estado: </strong><span id="status" class="state">Carregando...</span><p id="info"></p><small id="error"></small></article>
<article><h2>1. Testar alerta</h2><p>Com a fonte Navegador ativa no OBS, clique abaixo. A demonstração não desbloqueia uma conquista real.</p><button id="test">Exibir notificação de teste</button><small id="feedback" style="margin-left:12px"></small></article>
<article><h2>2. Fonte Navegador no OBS</h2><p>Copie a URL. Configure largura 520 e altura 160; marque <strong>Controlar áudio via OBS</strong>.</p><pre>http://127.0.0.1:8766/overlay</pre><p>O arquivo <code>som_alerta.wav</code> é livre e pode ser substituído por um WAV próprio. Para desativar o som, use <code>http://127.0.0.1:8766/overlay?som=0</code>.</p></article>
<article><h2>3. Durante a transmissão</h2><p>Mantenha RAW-SNES e este auxiliar em execução. O auxiliar acompanha a API do RetroAchievements e ignora conquistas antigas na primeira consulta. Atrasos dependem do servidor da API, da rede e da frequência de consultas.</p><p><small>São exibidos apenas achievements marcados como Super Nintendo, Super Famicom ou SNES na API. Credenciais não são enviadas à fonte Navegador.</small></p></article>
<script>
async function status(){try{const s=await(await fetch('/api/status',{cache:'no-store'})).json();document.getElementById('status').textContent=s.status+(s.online?' ✓':'');document.getElementById('info').textContent='Usuário: '+s.username+' | Última consulta: '+(s.last_check||'—')+' | Último alerta: '+(s.last_unlock||'—')+' | Intervalo: '+s.interval+' s';document.getElementById('error').textContent=s.error||''}catch(e){document.getElementById('status').textContent='Desconectado'}}
document.getElementById('test').addEventListener('click',async()=>{const feedback=document.getElementById('feedback');try{const r=await fetch('/api/test',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});if(!r.ok)throw Error('HTTP '+r.status);feedback.textContent='Notificação enviada ao overlay.'}catch(e){feedback.textContent='Erro: '+e.message}});status();setInterval(status,2000);
</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def local_host(self):
        return self.headers.get('Host', '') in (f'127.0.0.1:{PORT}', f'localhost:{PORT}')

    def reply(self, body, mime, code=200):
        data = body.encode('utf-8') if isinstance(body, str) else body
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.end_headers()
        self.wfile.write(data)

    def as_json(self, payload):
        self.reply(json.dumps(payload, ensure_ascii=False), 'application/json; charset=utf-8')

    def do_GET(self):
        if not self.local_host():
            return self.send_error(403)
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path in ('/', '/painel'):
            return self.reply(PANEL, 'text/html; charset=utf-8')
        if parsed.path == '/overlay':
            return self.reply(OVERLAY, 'text/html; charset=utf-8')
        if parsed.path == '/audio/alert.wav':
            if not SOUND_PATH.is_file():
                return self.send_error(404, 'WAV não encontrado')
            return self.reply(SOUND_PATH.read_bytes(), 'audio/wav')
        if parsed.path == '/api/status':
            with LOCK:
                return self.as_json({'seq': STATE.seq, 'status': STATE.status,
                                    'online': STATE.online, 'username': STATE.username,
                                    'last_check': STATE.last_check,
                                    'last_unlock': STATE.last_unlock,
                                    'error': STATE.error, 'interval': STATE.interval})
        if parsed.path == '/api/events':
            try:
                after = max(0, int(urllib.parse.parse_qs(parsed.query).get('after', ['0'])[0]))
            except (ValueError, IndexError):
                after = 0
            with LOCK:
                return self.as_json({'events': [e for e in STATE.events if e['seq'] > after]})
        self.send_error(404)

    def do_POST(self):
        if not self.local_host():
            return self.send_error(403)
        if self.path != '/api/test':
            return self.send_error(404)
        origin = self.headers.get('Origin', '')
        if origin and origin not in (f'http://127.0.0.1:{PORT}', f'http://localhost:{PORT}'):
            return self.send_error(403)
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.send_error(415)
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return self.send_error(400)
        if length < 0 or length > 1024:
            return self.send_error(413)
        self.rfile.read(length)
        STATE.emit({'title': 'Primeira conquista',
                    'description': 'Notificação demonstrativa sem conquista real',
                    'game': 'Super Nintendo — demonstração', 'points': 5, 'badge': '',
                    'hardcore': False, 'test': True, 'achievement_id': 'demo'})
        log('Notificação demonstrativa enviada ao overlay.')
        self.as_json({'ok': True})


def main(argv=None):
    parser = argparse.ArgumentParser(description='Notificações SNES para OBS Studio')
    parser.add_argument('--demo', action='store_true', help='Modo de teste sem chave de API')
    parser.add_argument('--interval', type=int, choices=(2, 3, 5, 10, 15), default=5)
    parser.add_argument('--reset', action='store_true', help='Remove credenciais locais do companion')
    parser.add_argument('--no-browser', action='store_true', help='Não abrir painel automaticamente')
    options = parser.parse_args(argv)
    if options.reset:
        if CONFIG_PATH.exists():
            CONFIG_PATH.unlink()
            print('Configuração do RAW-SNES OBS Companion removida.')
        else:
            print('Nenhuma configuração do companion para remover.')
        return 0
    STATE.interval = options.interval
    stop = threading.Event()
    if options.demo:
        STATE.username = 'DEMONSTRAÇÃO'
        STATE.status = 'Demonstração — use o botão de teste'
        STATE.online = True
    else:
        try:
            username, api_key = load_account()
        except Exception as exc:
            log('Falha ao configurar conta: ' + str(exc))
            return 1
        STATE.username = username
    try:
        server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    except OSError:
        log(f'Porta {PORT} indisponível. O companion já está aberto?')
        return 1
    if not options.demo:
        monitor = threading.Thread(target=poll_loop, args=(username, api_key, stop), daemon=True)
        monitor.start()
    print('\n===================================================')
    print(' RAW-SNES OBS COMPANION | AUXILIAR INDEPENDENTE')
    print('===================================================')
    print(f' Painel:  http://127.0.0.1:{PORT}/painel')
    print(f' OBS:     http://127.0.0.1:{PORT}/overlay')
    print(' Encerrar: Ctrl+C')
    print('===================================================\n')
    log(f'Servidor iniciado. Modo: {"demonstração" if options.demo else "API"}. '
        f'Intervalo: {STATE.interval}s. Som: {"OK" if SOUND_PATH.is_file() else "ausente"}.')
    if not options.no_browser:
        try:
            webbrowser.open(f'http://127.0.0.1:{PORT}/painel')
        except Exception:
            pass
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print('\nEncerrando companion.')
    finally:
        stop.set()
        server.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())

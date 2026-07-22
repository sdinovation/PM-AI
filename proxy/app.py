import json, os, time, urllib.request, urllib.error, base64, http.client, urllib.parse

FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')
FEISHU_CHAT_ID = os.environ.get('FEISHU_CHAT_ID', 'oc_b7fdf031892ffce3314c0b46303be25d')
FEISHU_WEBHOOK_URL = os.environ.get('FEISHU_WEBHOOK_URL', '')
CHAT_TRAIN = os.environ.get('CHAT_TRAIN', '')
CHAT_ERR = os.environ.get('CHAT_ERR', '')
CHAT_REPORT = os.environ.get('CHAT_REPORT', '')
CHAT_FB = os.environ.get('CHAT_FB', '')
CHAT_DAILY = os.environ.get('CHAT_DAILY', '')
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'deepseek')
LLM_KEY = os.environ.get('LLM_KEY', '')
LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.deepseek.com')
LLM_MODEL = os.environ.get('LLM_MODEL', 'deepseek-chat')

def http_post(url, headers=None, body=None, timeout=60):
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body else None
    hdrs = {'Content-Type': 'application/json; charset=utf-8'}
    if headers: hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors='ignore')
    except Exception as ex:
        return 0, str(ex)

_token = {'t': None, 'e': 0}
def feishu_token():
    n = time.time()
    if _token['t'] and n < _token['e']: return _token['t']
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET: return None
    st, d = http_post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        body={'app_id': FEISHU_APP_ID, 'app_secret': FEISHU_APP_SECRET})
    if isinstance(d, dict) and d.get('tenant_access_token'):
        _token['t'] = d['tenant_access_token']; _token['e'] = n + d.get('expire', 7200) - 60
        return _token['t']
    return None

def send_webhook(webhook_url, text):
    """发 webhook — 手动构造 JSON 确保编码"""
    url = webhook_url.strip()
    if not url.startswith('http'):
        return False, 'bad_url'
    # 手动 \uXXXX 编码中文字符，不依赖 json.dumps
    def escape_unicode(s):
        result = []
        for c in s:
            n = ord(c)
            if n > 127:
                result.append('\\u%04x' % n)
            elif c == '"':
                result.append('\\"')
            elif c == '\\':
                result.append('\\\\')
            elif c == '\n':
                result.append('\\n')
            elif c == '\r':
                result.append('\\r')
            elif c == '\t':
                result.append('\\t')
            else:
                result.append(c)
        return ''.join(result)
    text_esc = escape_unicode(text)
    payload = '{"msg_type":"text","content":{"text":"' + text_esc + '"}}'
    data = payload.encode('ascii')
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Length': str(len(data))
    }, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status == 200, 'wh_ok'
    except urllib.error.HTTPError as e:
        return False, f'wh_{e.code}'
    except Exception as ex:
        return False, str(ex)[:100]

def ok(data, status=200):
    return {'statusCode': status,
            'headers': {'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(data, ensure_ascii=False)}

def parse_body(raw):
    if isinstance(raw, bytes):
        try: raw = json.loads(raw.decode('utf-8'))
        except: return {}
    if isinstance(raw, str):
        try: raw = json.loads(raw)
        except: return {}
    if not isinstance(raw, dict):
        return {}
    if 'body' in raw and isinstance(raw['body'], str):
        b = raw['body']
        if raw.get('isBase64Encoded'):
            try: b = base64.b64decode(b).decode('utf-8')
            except: pass
        try: return json.loads(b)
        except: return raw
    return raw

def handler(event, context=None):
    body = parse_body(event)

    # LLM 代理
    if body.get('prompt') or body.get('systemPrompt'):
        if not LLM_KEY: return ok({'error': 'LLM Key not configured'}, 503)
        try:
            st, d = http_post(f'{LLM_BASE_URL}/v1/chat/completions',
                headers={'Authorization': f'Bearer {LLM_KEY}'},
                body={'model': LLM_MODEL, 'max_tokens': 2048, 'temperature': 0,
                      'messages': [{'role': 'system', 'content': body.get('systemPrompt', '')},
                                   {'role': 'user', 'content': body.get('prompt', '')}]}, timeout=90)
            if st != 200: return ok({'error': f'API {st}'}, 502)
            ch = d.get('choices', [])
            return ok({'text': ch[0].get('message', {}).get('content', '') if ch else ''})
        except Exception as ex:
            return ok({'error': str(ex)}, 500)

    # 飞书消息
    text = body.get('text', '')
    route = body.get('route', '')
    if not text:
        return ok({'code': 400, 'msg': 'no text'}, 400)

    # 路由表
    route_map = {
        'training': CHAT_TRAIN,
        'error':    CHAT_ERR,
        'report':   CHAT_REPORT,
        'feedback': CHAT_FB,
        'daily':    CHAT_DAILY,
    }
    target = route_map.get(route, '').strip()

    if target.startswith('http'):
        # Webhook 群
        ok_flag, detail = send_webhook(target, text)
        return ok({'code': 0, 'feishu_ok': ok_flag, 'feishu_detail': detail, 'route': route, 'via': 'webhook'})
    elif target:
        # chat_id 群（API）
        t = feishu_token()
        if t:
            inner = json.dumps({'text': text}, ensure_ascii=False)
            outer = json.dumps({'receive_id': target, 'msg_type': 'text', 'content': inner}, ensure_ascii=False)
            data = outer.encode('utf-8')
            u = urllib.parse.urlparse('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id')
            conn = http.client.HTTPSConnection(u.hostname, timeout=30)
            try:
                conn.request('POST', u.path + '?' + u.query, body=data, headers={
                    'Authorization': f'Bearer {t}', 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': str(len(data))
                })
                resp = conn.getresponse()
                ok_flag = resp.status == 200
                detail = 'ok' if ok_flag else f'api_{resp.status}_{resp.read().decode(errors="ignore")[:200]}'
                return ok({'code': 0, 'feishu_ok': ok_flag, 'feishu_detail': detail, 'route': route, 'via': 'api'})
            except Exception as ex:
                return ok({'code': 0, 'feishu_ok': False, 'feishu_detail': str(ex)[:100], 'route': route})
            finally:
                conn.close()
        return ok({'code': 0, 'feishu_ok': False, 'feishu_detail': 'no_token', 'route': route})

    # 没有路由 → 回退到主群（token API）
    t = feishu_token()
    if t:
        inner = json.dumps({'text': text}, ensure_ascii=False)
        outer = json.dumps({'receive_id': FEISHU_CHAT_ID, 'msg_type': 'text', 'content': inner}, ensure_ascii=False)
        data = outer.encode('utf-8')
        u = urllib.parse.urlparse('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id')
        conn = http.client.HTTPSConnection(u.hostname, timeout=30)
        try:
            conn.request('POST', u.path + '?' + u.query, body=data, headers={
                'Authorization': f'Bearer {t}', 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': str(len(data))
            })
            resp = conn.getresponse()
            ok_flag = resp.status == 200
            detail = 'ok' if ok_flag else f'api_{resp.status}_{resp.read().decode(errors="ignore")[:200]}'
            return ok({'code': 0, 'feishu_ok': ok_flag, 'feishu_detail': detail, 'via': 'default_api'})
        except Exception as ex:
            return ok({'code': 0, 'feishu_ok': False, 'feishu_detail': str(ex)[:100]})
        finally:
            conn.close()

    # 回退到 FEISHU_WEBHOOK_URL
    if FEISHU_WEBHOOK_URL:
        ok_flag, detail = send_webhook(FEISHU_WEBHOOK_URL, text)
        return ok({'code': 0, 'feishu_ok': ok_flag, 'feishu_detail': detail, 'via': 'default_webhook'})

    return ok({'code': 0, 'feishu_ok': False, 'feishu_detail': 'no_send_method'})

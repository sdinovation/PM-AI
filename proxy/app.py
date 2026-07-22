import json, os, time, urllib.request, urllib.error, base64, http.client, urllib.parse

FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')
FEISHU_CHAT_ID = os.environ.get('FEISHU_CHAT_ID', 'oc_b7fdf031892ffce3314c0b46303be25d')
FEISHU_WEBHOOK_URL = os.environ.get('FEISHU_WEBHOOK_URL', '')
# 多群路由：每类消息可推不同群，不填则推默认群
# 阿里云 FC 环境变量命名限制：字母开头 + 字母数字下划线（部分版本不允许连续下划线）
# 改用短前缀避免命名冲突
FC = os.environ.get('FC', '')  # 兼容老变量名，也可忽略
# 5 个群的环境变量（短前缀）
CHAT_TRAIN = os.environ.get('CHAT_TRAIN', '')     # #待训练
CHAT_ERR = os.environ.get('CHAT_ERR', '')         # 错误告警
CHAT_REPORT = os.environ.get('CHAT_REPORT', '')   # 报告导出
CHAT_FB = os.environ.get('CHAT_FB', '')           # 点踩/点赞
CHAT_DAILY = os.environ.get('CHAT_DAILY', '')     # 日汇总
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
    
def send_to_feishu_by_route(text, route=''):
    """按路由推送到不同群"""
    chat_id_map = {
        'training': CHAT_TRAIN,
        'error':    CHAT_ERR,
        'report':   CHAT_REPORT,
        'feedback': CHAT_FB,
        'daily':    CHAT_DAILY,
    }
    target_chat = chat_id_map.get(route) or FEISHU_CHAT_ID
    return send_to_feishu_text(text, target_chat)

def send_to_feishu_text(text, target_chat):
    # 去除可能的空格或不可见字符
    target_chat = target_chat.strip()
    # 判断是 chat_id (oc_xxx) 还是 webhook URL
    if target_chat.startswith('http'):
        # 用 webhook 直接发
        inner = json.dumps({'text': text}, ensure_ascii=False)
        data = inner.encode('utf-8')
        u = urllib.parse.urlparse(target_chat)
        conn = http.client.HTTPSConnection(u.hostname, timeout=30)
        try:
            conn.request('POST', u.path, body=data, headers={'Content-Type': 'application/json; charset=utf-8', 'Content-Length': str(len(data))})
            resp = conn.getresponse()
            if resp.status == 200: return True, 'webhook_ok'
            return False, f'webhook_{resp.status}_{resp.read().decode(errors="ignore")[:200]}'
        except Exception as ex:
            return False, str(ex)[:200]
        finally:
            conn.close()
    elif target_chat.startswith('oc_'):
        # 用 token + chat_id
        t = feishu_token()
        if t:
            inner = json.dumps({'text': text}, ensure_ascii=False)
            outer = json.dumps({'receive_id': target_chat, 'msg_type': 'text', 'content': inner}, ensure_ascii=False)
            data = outer.encode('utf-8')
            u = urllib.parse.urlparse('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id')
            conn = http.client.HTTPSConnection(u.hostname, timeout=30)
            try:
                conn.request('POST', u.path + '?' + u.query, body=data, headers={'Authorization': f'Bearer {t}', 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': str(len(data))})
                resp = conn.getresponse()
                if resp.status == 200: return True, 'ok'
                return False, f'api_{resp.status}_{resp.read().decode(errors="ignore")[:200]}'
            except Exception as ex:
                return False, str(ex)[:200]
            finally:
                conn.close()
    return False, 'no_route'

def send_to_feishu(text):
    """默认推主群"""
    t = feishu_token()
    if t:
        inner = json.dumps({'text': text}, ensure_ascii=False)
        outer = json.dumps({'receive_id': FEISHU_CHAT_ID, 'msg_type': 'text', 'content': inner}, ensure_ascii=False)
        data = outer.encode('utf-8')
        u = urllib.parse.urlparse('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id')
        conn = http.client.HTTPSConnection(u.hostname, timeout=30)
        try:
            conn.request('POST', u.path + '?' + u.query, body=data, headers={
                'Authorization': f'Bearer {t}',
                'Content-Type': 'application/json; charset=utf-8',
                'Content-Length': str(len(data))
            })
            resp = conn.getresponse()
            if resp.status == 200: return True, 'ok'
            return False, f'api_{resp.status}_{resp.read().decode(errors="ignore")[:200]}'
        except Exception as ex:
            return False, str(ex)[:200]
        finally:
            conn.close()
    return False, 'no_token_no_webhook'

def fmt(p):
    e = p.get('event_type', ''); ts = p.get('time_local', '')
    u = (p.get('user_fingerprint') or '?')[:8]; s = (p.get('session_id') or '?')[:6]
    v = p.get('app_version', '?'); ft = f'\n\n---\n👤 {u} · #{s} · v{v}'
    if e in ('page_view', 'session_start'):
        return f'🟢 数分精灵 · 新会话\n\n🕐 {ts}\n📱 {p.get("screen_size","?")} · {"深色" if p.get("dark_mode") else "浅色"}\n🔑 已配Key：{"是" if p.get("has_key") else "否"}\n🔗 {p.get("referrer","直接访问")}{ft}'
    if e == 'file_upload':
        return f'📁 数分精灵 · 文件上传\n\n🕐 {ts}\n📄 {p.get("file_name","?")} · {p.get("file_size_kb",0)}KB\n📊 {p.get("row_count",0)} 行 × {p.get("column_count",0)} 列\n🏷️ {(p.get("column_names","") or "").replace(",",", ")[:80]}{ft}'
    if e == 'analysis_complete':
        return f'📊 数分精灵 · 分析日志\n\n🕐 {ts}\n📂 {p.get("data_source","?")}（{p.get("data_rows",0)}行×{p.get("data_columns",0)}列）\n🔄 第{p.get("round_index",1)}轮 · 🎯{p.get("intent","?")}\n🔑 {p.get("api_provider","?")} {p.get("api_model","")}\n\n🙋 问题：{p.get("user_question","")[:200]}\n\n💡 回复：{p.get("ai_response","")[:300]}\n\n📝 SQL：\n{p.get("sql","无")[:300]}{ft}'
    if e == 'report_export':
        return f'📄 数分精灵 · 报告导出\n\n🕐 {ts}\n📝 {p.get("report_title","?")}\n📦 {p.get("export_format","?")} · 📈 {p.get("chart_count",0)}张图表\n🤖 {"LLM填充" if p.get("has_llm") else "本地生成"}{ft}'
    if e == 'error':
        return f'🚨 数分精灵 · 错误告警\n\n🕐 {ts}\n📂 {p.get("data_source","?")} · 第{p.get("round_index",1)}轮\n🏷️ {p.get("error_type","?")}\n\n📝 {p.get("error_message","")[:500]}\n\n📋 上下文：{p.get("context","")[:300]}{ft}'
    return f'📌 数分精灵 · {e}\n🕐 {ts}{ft}'

def do_llm_proxy(body):
    prompt = body.get('prompt', ''); sp = body.get('systemPrompt', '')
    if not LLM_KEY: return {'error': 'LLM Key not configured'}
    try:
        if LLM_PROVIDER == 'anthropic':
            st, d = http_post(f'{LLM_BASE_URL}/v1/messages',
                headers={'x-api-key': LLM_KEY, 'anthropic-version': '2023-06-01'},
                body={'model': LLM_MODEL, 'max_tokens': 2048, 'temperature': 0, 'system': sp,
                      'messages': [{'role': 'user', 'content': prompt}]}, timeout=90)
            if st != 200: return {'error': f'API {st}'}
            cl = d.get('content', []); return {'text': cl[0].get('text', '') if isinstance(cl, list) and cl else ''}
        else:
            st, d = http_post(f'{LLM_BASE_URL}/v1/chat/completions',
                headers={'Authorization': f'Bearer {LLM_KEY}'},
                body={'model': LLM_MODEL, 'max_tokens': 2048, 'temperature': 0,
                      'messages': [{'role': 'system', 'content': sp}, {'role': 'user', 'content': prompt}]}, timeout=90)
            if st != 200: return {'error': f'API {st}'}
            ch = d.get('choices', []); return {'text': ch[0].get('message', {}).get('content', '') if ch else ''}
    except Exception as ex:
        return {'error': str(ex)}

def ok(data, status=200):
    return {'statusCode': status,
            'headers': {'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(data, ensure_ascii=False)}

def parse_body(raw):
    # bytes/str → dict，所有 decode 都必须显式 utf-8
    if isinstance(raw, bytes):
        try: raw = json.loads(raw.decode('utf-8'))
        except: return {}
    if isinstance(raw, str):
        try: raw = json.loads(raw)
        except: return {}
    if not isinstance(raw, dict):
        return {}

    # 如果有 'body' 字段，说明是阿里云 FC event 包装，解包内层
    if 'body' in raw and isinstance(raw['body'], str):
        b = raw['body']
        if raw.get('isBase64Encoded'):
            try: b = base64.b64decode(b).decode('utf-8')
            except: pass
        try: return json.loads(b)
        except: return raw
    return raw

def get_path(raw):
    if isinstance(raw, dict):
        p = raw.get('rawPath') or raw.get('path') or raw.get('PATH_INFO') or '/'
        # 阿里云 FC HTTP 触发器默认 path 是 /，从 queryString 或 headers 取路由信息
        qs = raw.get('queryParameters') or {}
        if qs and qs.get('route'):
            p = '/' + qs.get('route')
        return p.rstrip('/') or '/'
    return '/'

def handler(event, context=None):
    body = parse_body(event)
    path = get_path(event)

    # action 字段分发（兼容无 path 路由的场景）
    action = body.get('action', '')

    if action == 'llm_proxy' or '/api/llm/proxy' in path or '/llm/proxy' in path:
        res = do_llm_proxy(body)
        return ok(res, 200 if 'text' in res else 503)

    elif action == 'feishu_log' or '/api/feishu/log' in path or '/feishu/log' in path:
        text = fmt(body) if body.get('event_type') else body.get('text', '')
        route = body.get('route', '')
        if text:
            ok_flag, detail = send_to_feishu_by_route(text, route)
            return ok({'code': 0, 'feishu_ok': ok_flag, 'feishu_detail': detail, 'route': route})
        return ok({'code': 400, 'msg': 'no text'}, 400)

    else:
        # 兼容旧接口：根据 payload 内容自动判断
        if body.get('prompt') or body.get('systemPrompt'):
            res = do_llm_proxy(body)
            return ok(res, 200 if 'text' in res else 503)
        text = body.get('text', '')
        route = body.get('route', '')
        if text:
            ok_flag, detail = send_to_feishu_by_route(text, route)
            return ok({'code': 0, 'feishu_ok': ok_flag, 'feishu_detail': detail, 'route': route})
        return ok({'code': 400, 'msg': 'no text'}, 400)

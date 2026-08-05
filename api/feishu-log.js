// Vercel Serverless Function — 飞书日志代理（绕过 CORS）
export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const FEISHU_APP_ID = process.env.FEISHU_APP_ID;
  const FEISHU_APP_SECRET = process.env.FEISHU_APP_SECRET;
  const { chat_id, text } = req.body || {};
  if (!chat_id || !text) return res.status(400).json({ error: 'Missing chat_id or text' });

  try {
    // 获取 token
    const tokenRes = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_id: FEISHU_APP_ID, app_secret: FEISHU_APP_SECRET })
    });
    const tokenData = await tokenRes.json();
    const token = tokenData.tenant_access_token;
    if (!token) return res.status(500).json({ error: 'Token failed', raw: tokenData });

    // 发送消息
    const content = JSON.stringify({ text });
    const msgRes = await fetch(`https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ receive_id: chat_id, msg_type: 'text', content })
    });
    const result = await msgRes.json();
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).json({ code: result.code, msg: result.msg || 'sent' });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}

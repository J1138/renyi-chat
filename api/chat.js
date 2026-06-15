const https = require('https');

exports.handler = async function(event, context) {
  // Handle CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
      },
      body: ''
    };
  }

  try {
    const body = JSON.parse(event.body || '{}');
    const message = body.message;

    if (!message) {
      return {
        statusCode: 400,
        headers: { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'Message is required' })
      };
    }

    const DEEPSEEK_API_KEY = "sk-02e8b626ffae44f7bb32a4764fd11400";

    const PRODUCT_KNOWLEDGE = `你是仁义纸业销售助手，专门回答客户关于纸类产品的问题。

公司信息：
- 公司名称：东莞市仁义纸业有限公司
- 地址：东莞市寮步镇岭厦建设1号
- 电话：0769-82223130
- QQ：215041417

主营产品：
1. 双胶纸/书卡系列（宁美、东美、华语、宁盛、金华超感、百旺、联盛等品牌）- 克数：60g-350g，正大度/卷筒可分切
2. 铜版纸系列（双铜/单铜，80g-400g）
3. 白板纸/灰板纸系列
4. 白卡纸/食品卡系列（250g-450g）
5. 精牛/再生牛卡系列（230g-450g）
6. 箱板纸/瓦楞纸系列
7. 数码打印纸系列
8. 特种纸系列

回答要求：简洁专业，突出产品优势，主动提供联系方式，如果询问库存说明需要确认，语气友好像专业销售员。`;

    // Call DeepSeek API
    const payload = JSON.stringify({
      model: 'deepseek-chat',
      messages: [
        { role: 'system', content: PRODUCT_KNOWLEDGE },
        { role: 'user', content: message }
      ],
      max_tokens: 1024,
      temperature: 0.3,
      stream: false
    });

    const result = await new Promise((resolve, reject) => {
      const req = https.request('https://api.deepseek.com/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${DEEPSEEK_API_KEY}`,
          'Content-Length': Buffer.byteLength(payload)
        }
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch(e) {
            reject(new Error(`Parse error: ${data}`));
          }
        });
      });
      req.on('error', reject);
      req.write(payload);
      req.end();
    });

    const reply = result.choices[0].message.content;

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ reply })
    };

  } catch (e) {
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ error: e.message })
    };
  }
};

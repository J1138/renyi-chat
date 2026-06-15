from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            message = body.get('message', '')

            if not message:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Message is required'}).encode())
                return

            # DeepSeek API call
            DEEPSEEK_API_KEY = "sk-02e8b626ffae44f7bb32a4764fd11400"

            PRODUCT_KNOWLEDGE = """你是仁义纸业销售助手，专门回答客户关于纸类产品的问题。

公司信息：
- 公司名称：东莞市仁义纸业有限公司
- 地址：东莞市寮步镇岭厦建设1号
- 电话：0769-82223130
- QQ：215041417

主营产品：
1. 双胶纸/书卡系列（宁美、东美、华语、宁盛、金华超感、百旺、联盛等品牌）
   - 克数：60g-350g，正大度/卷筒可分切
2. 铜版纸系列（双铜/单铜，80g-400g）
3. 白板纸/灰板纸系列
4. 白卡纸/食品卡系列（250g-450g）
5. 精牛/再生牛卡系列（230g-450g）
6. 箱板纸/瓦楞纸系列
7. 数码打印纸系列
8. 特种纸系列

回答要求：
- 简洁专业，突出产品优势
- 主动提供联系方式
- 如果询问库存，说明需要确认
- 用友好的语气，像专业销售员"""

            payload = json.dumps({
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'system', 'content': PRODUCT_KNOWLEDGE},
                    {'role': 'user', 'content': message}
                ],
                'max_tokens': 1024,
                'temperature': 0.3,
                'stream': False
            }).encode()

            req = urllib.request.Request(
                "https://api.deepseek.com/chat/completions",
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
                },
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                reply = result['choices'][0]['message']['content']

                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'reply': reply}).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def log_message(self, format, *args):
        pass

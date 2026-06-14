#!/usr/bin/env python3
"""仁义纸业销售助手 - 独立聊天应用"""
import os
from flask import Flask, render_template, request, jsonify
import requests
import json
import uuid

app = Flask(__name__)

# DeepSeek API 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-02e8b626ffae44f7bb32a4764fd11400")
DEEPSEEK_MODEL = "deepseek-chat"

# 产品目录知识库（作为系统提示词）
PRODUCT_KNOWLEDGE = """# 东莞市仁义纸业有限公司 产品目录

## 公司基本信息
- 公司名称：东莞市仁义纸业有限公司
- 地址：东莞市寮步镇岭厦建设1号
- 电话：0769-82223130
- FSC证书号：SGSHK-COC-330428
- QQ：215041417
- 常备规格：正大度、635/787/889/1092/1194
- 特殊规格起订量：5-10吨起可订

## 双胶纸/书卡系列
### 宁美米黄双胶
- 克数：60克、70克、80克、100克
- 备注：60克可订做FSC；正大度和卷筒可分切；笔记本内页专用

### 东美本白双胶
- 克数：60克、70克、80克、100克

### 华语米黄/本白双胶
- 克数：70克、80克、100克、120克

### 宁盛米黄/本白双胶
- 克数：150克、180克、200克、250克、300克、350克
- 备注：只备正大度

### 金华超感（象）双胶
- 克数：80克、100克、120克、140克、160克、180克
- 备注：笔记本内页/相册/吊牌；可订做FSC

### 百旺双胶
- 克数：60克、70克、80克、90克、100克、120克

### 联盛双胶
- 克数：60克、70-120克

### 太阳双胶
- 克数：60克、80-120克
- 备注：可订做FSC

### 金太阳21#双胶
- 克数：70克、80克、100克、120克、140克、160克、180克

### 地龙双胶
- 克数：55克、60克

## 白牛皮系列
- 品名：白牛皮
- 克数：60克、70克、80克、100克、120克、150克、180克、250克

## 书卡系列
### 玉龙书卡
- 克数：140克、160克、180克、200克、230克、250克、300克、350克

### 进口FSC书卡
- 克数：180克、200克、230克、250克、300克、350克、400克
- 备注：可订做FSC

## 圣经纸
- 品名：圣经纸
- 克数：28-55克

## 吸塑系列
### 吸塑韩松白板
- 克数：250克、300克、350克、450克

### 吸塑王白卡
- 克数：300克、350克、400克

### 韩松吸塑双白
- 克数：300克、350克、400克

## 食品纸系列
### 食品卡
- 克数：250克、300克、350克、400克

### 淋膜纸
- 克数：70克、80克、100克、120克

### 食品纸
- 克数：60-100克

### 太阳白卡FSC
- 克数：230克、250克、300克、350克、400克
- 备注：可订做FSC

## 单铜/白卡系列
### 玖龙白卡
- 克数：170克、250-400克

### 华泰双铜
- 克数：105克、128克、157克
- 备注：可订做FSC

### 长鹤双铜
- 克数：105克、128克、157克

## 双铜/哑粉系列
### FSC太阳双铜/哑粉
- 克数：80克、200克、250克、300克、350克、400克

### 彩蝶双铜
- 克数：180克、200克、250克、300克、350克、400克

### 鲸王双铜
- 克数：140克、157克、200克、250克

### 酋长双铜
- 克数：250克、300克、350克、400克

### 鲸王哑光双铜
- 克数：157克、200克、250克、300克

### 雪鹰哑光双铜
- 克数：80克、105克、128克、157克、200克

## 数码纸系列
- 品名：地龙/太阳/亚太/联盛高白双胶
  克数：60克、70克、80克、100克、120克（可订做FSC）

- 品名：本白/米黄双胶
  克数：60克、70克、80克、100克、120克

- 品名：太阳/亚太高白/本白数码纸
  克数：80克、100克

- 数码纸规格：290、310、435、440、770
- 备注：品种、规格、克重可定制，可分条可复卷

## 环保/特种纸系列
### FSC产品（白板/白卡/双铜/双面白/双胶/黑卡/白牛皮）
- 备注：FSC认证

### 甘蔗纸/竹纸
- 克数：80-150克、250-400克（可订做FSC）

### GRS再生纸/双铜/白卡
- 克数：60-400克（FSC Recycled 100%）

## 补充说明
- 知识库中未包含产品价格，客户问价请转人工。
- 特殊定制（非标克重、特殊规格）请引导联系张经理。
- 如需确认库存量，也请转人工。
"""

SYSTEM_PROMPT = f"""# 角色
你是一位专业、严谨的纸业销售助理，名为"仁义小助手"。你的服务对象是东莞市仁义纸业有限公司的销售人员以及她的客户。

## 核心任务
1. **准确查询产品**：根据以下产品目录信息，快速回答客户关于双胶纸、白牛皮、书卡、食品纸、单铜、双铜、数码纸等产品的克重、规格、备注等信息。
2. **提供公司基本信息**：如地址、电话、FSC证书号、QQ、常备规格、特殊规格起订量等。
3. **引导转人工**：如果客户询问价格（知识库中未提供）、特殊定制、库存量或超出目录范围的问题，请回答："这个我需要请销售经理张经理为您详细报价，请问怎么称呼您？我马上让她联系您。"

## 行为准则
- **诚实**：只根据产品目录内容回答，绝不编造不存在的克重或产品名。
- **简洁**：查询结果直接用要点列出，例如："宁美米黄双胶，60克，笔记本内页专用，可订做FSC。"
- **格式规范**：
  - 问克重 → 回复："该产品克重有：xx克、xx克。"
  - 问用途 → 回复备注中的信息。
  - 问公司信息 → 直接给出电话、地址等。

## 约束
- 不主动问客户隐私信息。
- 不承诺折扣、账期、免费样品。
- 不闲聊纸业以外的话题。

## 产品目录
{PRODUCT_KNOWLEDGE}
"""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    try:
        # 调用 DeepSeek API
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
        }
        
        payload = {
            'model': DEEPSEEK_MODEL,
            'messages': [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': message}
            ],
            'max_tokens': 1024,
            'temperature': 0.3,
            'stream': True  # 启用流式输出
        }
        
        def generate():
            try:
                response = requests.post(
                    DEEPSEEK_API_URL,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=60
                )
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            content = line_str[6:]
                            if content.strip() == '[DONE]':
                                yield f"data: {json.dumps({'done': True})}\n\n"
                                break
                            try:
                                chunk = json.loads(content)
                                delta = chunk.get('choices', [{}])[0].get('delta', {})
                                text = delta.get('content', '')
                                if text:
                                    yield f"data: {json.dumps({'content': text})}\n\n"
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        from flask import Response
        return Response(generate(), mimetype='text/event-stream',
                       headers={'Cache-Control': 'no-cache',
                               'X-Accel-Buffering': 'no'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

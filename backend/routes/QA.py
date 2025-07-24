import os
import requests  
from flask import Blueprint, jsonify, request

qa_bp = Blueprint('qa', __name__)

@qa_bp.route('/', methods=['POST', 'OPTIONS'])
def qa():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
    except Exception:
        return jsonify({'answer': '无效的请求格式'}), 400

    question = data.get('question', '').strip()
    if not question:
        return jsonify({'answer': '请输入问题'}), 400

    prompt = '你是医疗系统智能客服，请用中文简洁回答用户问题。\n用户问题：' + question

    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('DASHSCOPE_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen-plus",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.3
            },
            timeout=10
        )
        if response.status_code != 200:
            return jsonify({'answer': 'AI 服务返回异常'}), 503

        answer = response.json()['choices'][0]['message']['content'].strip()
        return jsonify({'answer': answer})

    except requests.exceptions.RequestException as e:
        print("❗ 网络或 API 错误：", e)
        return jsonify({'answer': 'AI 服务访问失败'}), 503
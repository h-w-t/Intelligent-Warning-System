from flask import Blueprint, jsonify, request
import os
import requests
import json
import logging
import re

# 配置日志记录
logging.basicConfig(level=logging.INFO)

# 创建 Blueprint
risk_bp = Blueprint('risk_prediction', __name__)

# 获取环境变量中的 API Key
API_KEY = os.getenv('DASHSCOPE_API_KEY')
# 定义 DashScope 的 API 终端地址
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

@risk_bp.route('/', methods=['POST'])
def risk_prediction():
    try:
        # 获取请求体中的 JSON 数据
        data = request.get_json() or {}
        age = data.get('age')
        gender = data.get('gender')
        smoking_status = data.get('smoking_status')
        diagnosis = data.get('diagnosis')
        origin_province = data.get('origin_province')

        # 检查是否有必要的字段
        if None in (age, gender, smoking_status, diagnosis, origin_province):
            return jsonify({'error': '缺少必要字段'}), 400

        # 构造提示信息
        prompt = (
            "你是肺癌专科医生，请根据以下信息给出 5 年发病风险（0-100 整数）"
            "和 30 字以内中文原因，并以 JSON 格式返回：\n"
            "年龄={age} 岁；性别={gender}；吸烟={smoking_status}；"
            "癌症类型={diagnosis}；省份={origin_province}\n"
            "返回格式示例：\n"
            "'{{\"risk\": 75, \"reason\": \"年龄大、男性、腺癌史、上海环境因素\"}}'"
        ).format(
            age=age, gender=gender, smoking_status=smoking_status,
            diagnosis=diagnosis, origin_province=origin_province
        )

        # 构造请求负载
        payload = {
            "model": "qwen-plus",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.2
        }

        # 记录请求负载
        logging.info(f"[risk] 请求 payload={payload}")

        # 发起 POST 请求到 DashScope
        response = requests.post(
            ENDPOINT,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json=payload,
            timeout=15
        )

        # 记录返回状态码
        logging.info(f"[risk] 返回码={response.status_code}")

        # 检查响应状态码
        response.raise_for_status()

        # 解析响应内容
        content = response.json()["choices"][0]["message"]["content"].strip()

        # 去掉前后 Markdown 标签
        content = re.sub(r'```(?:json)?', '', content, flags=re.I).strip()

        # 提取第一个合法 JSON 对象
        match = re.search(r'\{.*?\}', content, flags=re.S)
        if not match:
            logging.error("[risk] 未找到 JSON: %s", content)
            return jsonify({"error": "返回格式异常"}), 500

        try:
            result = json.loads(match.group(0))
        except json.JSONDecodeError:
            logging.exception("[risk] JSON 解析失败: %s", match.group(0))
            return jsonify({"error": "返回解析失败"}), 500

        return jsonify(result)

    except requests.exceptions.RequestException as e:
        logging.exception("[risk] 网络/超时异常")
        return jsonify({"error": "网络或 DashScope 异常"}), 503
    except json.JSONDecodeError as e:
        logging.exception("[risk] JSON 解析异常")
        return jsonify({"error": "返回格式错误"}), 500
    except Exception as e:
        logging.exception("[risk] 未知异常")
        return jsonify({"error": str(e)}), 500
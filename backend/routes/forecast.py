from flask import Blueprint, jsonify, request
from config.db import get_cursor
import requests

forecast_bp = Blueprint('forecast', __name__)

@forecast_bp.route('/', methods=['POST'])
def batch_forecast():
    try:
        data = request.get_json()
        ids = data.get('ids', [])
        if not ids:
            return jsonify({'error': '缺少 ids'}), 400

        sql = """
        SELECT sequence_number AS caseId, age, gender, smoking_status,
               lung_cancer_classification AS diagnosis, origin_province
        FROM lung_cancer_patients
        WHERE sequence_number IN ({})
        """.format(','.join(['%s'] * len(ids)))

        with get_cursor() as cur:
            cur.execute(sql, ids)
            rows = cur.fetchall()

        results = []
        for row in rows:
            payload = {
                'age': row['age'],
                'gender': row['gender'],
                'smoking_status': row['smoking_status'],
                'diagnosis': row['diagnosis'],
                'origin_province': row['origin_province']
            }
            resp = requests.post('http://localhost:3000/api/riskPrediction/', json=payload, timeout=5)
            resp.raise_for_status()
            results.append({'caseId': row['caseId'], **resp.json()})

        return jsonify(results)

    except Exception as e:
        print('批量预测异常:', e)
        return jsonify({'error': '批量预测失败'}), 500

@forecast_bp.route('/', methods=['GET'])
def get_forecast_by_ids():
    try:
        ids_str = request.args.get('ids')
        if not ids_str:
            return jsonify({'error': '缺少 ids 参数'}), 400

        ids = [int(i) for i in ids_str.split(',') if i.strip().isdigit()]
        if not ids:
            return jsonify({'error': 'ids 参数格式不正确'}), 400

        sql = """
        SELECT sequence_number AS caseId, age, gender, smoking_status,
               lung_cancer_classification AS diagnosis, origin_province
        FROM lung_cancer_patients
        WHERE sequence_number IN ({})
        """.format(','.join(['%s'] * len(ids)))

        with get_cursor() as cur:
            cur.execute(sql, ids)
            rows = cur.fetchall()

        results = []
        for row in rows:
            payload = {
                'age': row['age'],
                'gender': row['gender'],
                'smoking_status': row['smoking_status'],
                'diagnosis': row['diagnosis'],
                'origin_province': row['origin_province']
            }
            # 调用本地的风险预测API
            resp = requests.post('http://localhost:3000/api/riskPrediction/', json=payload, timeout=5)
            resp.raise_for_status()
            results.append({'caseId': row['caseId'], **resp.json()})

        return jsonify(results)

    except requests.exceptions.RequestException as req_e:
        print(f'请求风险预测API异常: {req_e}')
        return jsonify({'error': f'请求风险预测API失败: {str(req_e)}'}), 500
    except Exception as e:
        print(f'获取预测数据异常: {e}')
        return jsonify({'error': f'获取预测数据失败: {str(e)}'}), 500

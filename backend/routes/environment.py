from flask import Blueprint, jsonify, request
from config.db import get_cursor

environment_bp = Blueprint('environment', __name__)

@environment_bp.route('/', methods=['GET'])
def get_environment_data():
    try:
        # 获取查询参数中的 months，默认为 36
        months_str = request.args.get('months', '36')
        months = int(months_str)

        # 白名单校验
        allowed = [3, 6, 12, 24, 36]
        if months not in allowed:
            return jsonify({'error': 'Invalid months parameter'}), 400

        # 构建 SQL 查询语句
        suffix = f"{months}_month_avg"
        sql = f"""
        SELECT
            CONCAT(diag_year, '-', LPAD(diag_month, 2, '0')) AS measure_period,
            aqi_{suffix} AS aqi,
            pm2_5_{suffix} AS pm25,
            pm10_{suffix} AS pm10,
            o3_{suffix} AS o3,
            co_{suffix} AS co,
            no2_{suffix} AS no2,
            so2_{suffix} AS so2
        FROM environmental_data
        ORDER BY diag_year ASC, diag_month ASC
        """

        # 执行 SQL 查询
        with get_cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        # 返回查询结果
        return jsonify(rows)

    except ValueError:
        return jsonify({'error': 'Invalid months parameter'}), 400
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Database query failed'}), 500
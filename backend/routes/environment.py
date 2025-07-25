from flask import Blueprint, jsonify, request
from flask_cors import CORS  # 如需要跨域
from config.db import get_cursor

environment_bp = Blueprint('environment', __name__)
CORS(environment_bp)  # 允许跨域

# ---------------- GET ----------------
@environment_bp.route('/', methods=['GET'])
def get_environment_data():
    try:
        months = int(request.args.get('months', 36))
        if months not in {3, 6, 12, 24, 36}:
            return jsonify({'error': 'Invalid months parameter'}), 400

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
        with get_cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------- POST ----------------
@environment_bp.route('/', methods=['POST'])
def add_environment_data():
    try:
        data = request.get_json(force=True)  # ✅ 确保这行存在
        print("🔍 收到前端数据：", data)  # ✅ 调试打印

        year = int(data['diag_year'])
        month = int(data['diag_month'])
        win = int(data.get('window_months', 12))
        if win not in {3, 6, 12, 24, 36}:
            return jsonify({'error': 'window_months must be 3/6/12/24/36'}), 400

        suffix = f"{win}_month_avg"

        # 字段映射
        map_front2back = {
            'aqi_12_month_avg': f'aqi_12_month_avg',
            'pm2_5_12_month_avg': f'pm2_5_12_month_avg',
            'pm10_12_month_avg': f'pm10_12_month_avg',
            'o3_12_month_avg': f'o3_12_month_avg',
            'co_12_month_avg': f'co_12_month_avg',
            'no2_12_month_avg': f'no2_12_month_avg',
            'so2_12_month_avg': f'so2_12_month_avg'
        }   


        fields = ['diag_year', 'diag_month'] + list(map_front2back.values())
        values = [year, month] + [data.get(k) for k in map_front2back.keys()]

        placeholders = ','.join(['%s'] * len(fields))
        updates = ','.join([f"{f}=VALUES({f})" for f in fields[2:]])

        sql = f"""
        INSERT INTO environmental_data ({','.join(fields)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {updates}
        """

        with get_cursor() as cur:
            print("✅ 最终 SQL：", sql)
            print("✅ 最终 values：", values)
            cur.execute(sql, values)
            print("✅ 插入成功，影响行数：", cur.rowcount)  # ✅ 调试打印

        return jsonify({'success': True}), 201
    except Exception as e:
        print("❌ 插入失败：", e)
        return jsonify({'error': str(e)}), 500


@environment_bp.route('/<int:year>/<int:month>', methods=['DELETE'])
def delete_environment_data(year, month):
    with get_cursor() as cur:
        cur.execute("DELETE FROM environmental_data WHERE diag_year=%s AND diag_month=%s", (year, month))
    return jsonify({'success': True}), 200

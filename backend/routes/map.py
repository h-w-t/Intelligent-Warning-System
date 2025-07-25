# backend/routes/map.py
from flask import Blueprint, jsonify
from config.db import get_cursor

map_bp = Blueprint('map', __name__, url_prefix='/api/map')

# ----------上海各区肺癌确诊人数 ----------
@map_bp.route('/lung-cancer-by-district', methods=['GET'])
def lung_cancer_by_district():
    """
    返回格式：
    [
        {"district": "浦东新区", "count": 1250},
        {"district": "黄浦区",   "count": 780},
        ...
    ]
    """
    sql = """
        SELECT
    REPLACE(shanghai_administrative_division, '上海市', '') AS district,
    COUNT(*) AS count
    FROM lung_cancer_patients
    WHERE shanghai_administrative_division IS NOT NULL
    AND TRIM(shanghai_administrative_division) != ''
     AND lung_cancer_classification IS NOT NULL
    GROUP BY district
    ORDER BY count DESC

    """
    with get_cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return jsonify([{"district": row["district"], "count": int(row["count"])} for row in rows])

@map_bp.route('/district-details', methods=['GET'])
def district_details():
    """
    返回格式：
    {
      "浦东新区": { "total": 4059, "breakdown": { "腺癌": 50.2, "鳞癌": 30.1, ... } },
      "宝山区":   { "total": 2173, "breakdown": { "腺癌": 12.0, "小细胞癌": 13.0, ... } },
      ...
    }
    """
    sql = """
        SELECT
            REPLACE(shanghai_administrative_division, '上海市', '') AS district,
            lung_cancer_classification                             AS cancer_type,
            COUNT(*)                                               AS cnt
        FROM lung_cancer_patients
        WHERE shanghai_administrative_division IS NOT NULL
          AND TRIM(shanghai_administrative_division) != ''
          AND lung_cancer_classification IS NOT NULL
        GROUP BY district, cancer_type
        ORDER BY district, cnt DESC
    """
    with get_cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    # 转成分区嵌套字典
    result = {}
    for r in rows:
        d = r["district"]
        c = r["cancer_type"]
        n = int(r["cnt"])
        if d not in result:
            result[d] = {"total": 0, "breakdown": {}}
        result[d]["breakdown"][c] = n
        result[d]["total"] += n

    # 把绝对数转成百分比（保留 1 位小数）
    for d, data in result.items():
        total = data["total"]
        data["breakdown"] = {
            k: round(v * 100 / total, 1)
            for k, v in data["breakdown"].items()
        }

    return jsonify(result)



# ----------  空接口占位 ，可以是热力图等的接口 ----------
@map_bp.route('/air-quality-heatmap', methods=['GET'])
def air_quality_heatmap():
    return jsonify({"message": "待实现"})

@map_bp.route('/age-distribution', methods=['GET'])
def age_distribution():
    return jsonify({"message": "待实现"})

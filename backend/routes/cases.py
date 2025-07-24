from flask import Blueprint, jsonify, request
from config.db import get_cursor
import math

cases_bp = Blueprint('cases', __name__)

# ---------- 工具 ----------
def clean_id(_id: str) -> str:
    """去掉可能的前导 #"""
    return _id[1:] if _id.startswith('#') else _id


# ---------- 1. GET /api/cases ----------
@cases_bp.route('/', methods=['GET'])
def get_cases():
    try:
        # 获取查询参数
        search      = request.args.get('search')
        patient     = request.args.get('patient')
        year        = request.args.get('year', type=int)
        month       = request.args.get('month', type=int)
        age         = request.args.get('age', type=int)
        gender      = request.args.get('gender')
        cancer_type = request.args.get('cancerType')
        is_smoker   = request.args.get('isSmoker')

        # 分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit

        # 构建基础 SQL 和参数
        base_sql = """
            FROM lung_cancer_patients
            WHERE 1=1
        """
        params = []

        # 动态拼接条件
        if search:
            like = f"%{search}%"
            base_sql += " AND (patient_SN LIKE %s OR sequence_number LIKE %s OR lung_cancer_classification LIKE %s)"
            params.extend([like, like, like])
        if patient:
            base_sql += " AND patient_SN = %s"
            params.append(patient)
        if year:
            base_sql += " AND diagnosis_year = %s"
            params.append(year)
        if month:
            base_sql += " AND diagnosis_month = %s"
            params.append(month)
        if age:
            base_sql += " AND age = %s"
            params.append(age)
        if gender:
            base_sql += " AND gender = %s"
            params.append(gender)
        if cancer_type:
            base_sql += " AND lung_cancer_classification = %s"
            params.append(cancer_type)
        if is_smoker is not None:
            base_sql += " AND smoking_status = %s"
            params.append('是' if is_smoker == 'true' else '否')

        # 获取总记录数
        count_sql = "SELECT COUNT(*) AS total_count " + base_sql
        with get_cursor() as cur:
            cur.execute(count_sql, params)
            total_count = cur.fetchone()['total_count']

        # 获取分页数据
        data_sql = f"""
            SELECT
                patient_SN,
                sequence_number AS caseId,
                gender,
                age,
                smoking_status,
                lung_cancer_classification AS diagnosis,
                diagnosis_year,
                diagnosis_month
            {base_sql}
            ORDER BY diagnosis_year DESC, diagnosis_month DESC
            LIMIT %s OFFSET %s
        """
        data_params = params + [limit, offset]

        with get_cursor() as cur:
            cur.execute(data_sql, data_params)
            rows = cur.fetchall()

        # 格式化月份
        for r in rows:
            r['diagnosis_month'] = str(r['diagnosis_month']).zfill(2) if r['diagnosis_month'] else ''

        return jsonify({
            'cases': rows,
            'total_count': total_count,
            'page': page,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------- 2. POST /api/cases ----------
@cases_bp.route('/', methods=['POST'])
def create_case():
    try:
        data = request.json
        values = (
            data['sequence_number'],
            data['patient_SN'],
            data['gender'],
            int(data['age']),
            data.get('origin_province') or None,
            data.get('shanghai_administrative_division') or None,
            data['diagnosis'],
            data['smoking_status'],
            int(data['diagnosis_year']),
            int(data['diagnosis_month'])
        )
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
        sql = """
            INSERT INTO lung_cancer_patients (
                sequence_number, patient_SN, gender, age,
                origin_province, shanghai_administrative_division,
                lung_cancer_classification, smoking_status,
                diagnosis_year, diagnosis_month
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        with get_cursor() as cur:
            cur.execute(sql, values)

        return jsonify({'message': '病例已创建', 'caseId': data['sequence_number']}), 201
    except Exception as e:
        code = 409 if 'Duplicate entry' in str(e) else 500
        return jsonify({'error': str(e)}), code


# ---------- 3. DELETE /api/cases/:id ----------
@cases_bp.route('/<case_id>', methods=['DELETE'])
def delete_case(case_id):
    try:
        case_id = clean_id(case_id)
        sql = "DELETE FROM lung_cancer_patients WHERE sequence_number = %s"
        with get_cursor() as cur:
            cur.execute(sql, (case_id,))
            if cur.rowcount == 0:
                return jsonify({'error': '病例未找到'}), 404
        return jsonify({'success': True, 'message': '已删除'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------- 4. GET /api/cases/lung-cancer-types ----------
@cases_bp.route('/lung-cancer-types', methods=['GET'])
def get_cancer_types():
    try:
        sql = """
            SELECT lung_cancer_classification AS cancer_type, COUNT(*) AS total_cases
            FROM lung_cancer_patients
            GROUP BY lung_cancer_classification
        """
        with get_cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        total = sum(r['total_cases'] for r in rows)
        result = [
            {'cancer_type': r['cancer_type'],
             'percentage': round(r['total_cases'] / total * 100)}
            for r in rows
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------- 5. GET /api/cases/stats ----------
@cases_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        sql = """
            SELECT
                COUNT(*) AS total_cases,
                GROUP_CONCAT(DISTINCT diagnosis_year ORDER BY diagnosis_year) AS years,
                ROUND(AVG(age), 1) AS avg_age,
                ROUND(SUM(gender = '男') * 100 / COUNT(*), 0) AS male_percentage
            FROM lung_cancer_patients
        """
        with get_cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()

        if not row:
            return jsonify({'error': '无数据'}), 404

        years = row['years'].split(',') if row['years'] else []
        year_range = f"{years[0]}-{years[-1]}" if years else ''

        return jsonify({
            'total_cases': row['total_cases'],
            'diagnosis_year_range': year_range,
            'avg_age': row['avg_age'],
            'male_percentage': row['male_percentage']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------- 6. GET /api/cases/:id ----------
@cases_bp.route('/<case_id>', methods=['GET'])
def get_case(case_id):
    try:
        case_id = clean_id(case_id)
        sql = """
            SELECT
                patient_SN,
                sequence_number AS caseId,
                gender,
                age,
                smoking_status,
                origin_province,
                shanghai_administrative_division,
                lung_cancer_classification AS diagnosis,
                diagnosis_year,
                diagnosis_month
            FROM lung_cancer_patients
            WHERE sequence_number = %s
        """
        with get_cursor() as cur:
            cur.execute(sql, (case_id,))
            row = cur.fetchone()

        if not row:
            return jsonify({'error': '未找到该病例'}), 404

        row['diagnosis_month'] = str(row['diagnosis_month']).zfill(2) if row['diagnosis_month'] else ''
        return jsonify(row)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------- 7. 预留影像学数据接口（MongoDB 示例） ----------
@cases_bp.route('/<case_id>/imaging', methods=['GET'])
def get_case_imaging(case_id):
    try:
        # 如果你用的是 MongoDB，这里替换为 pymongo 逻辑
        # 下面仅做示意
        return jsonify({'message': '暂未实现'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

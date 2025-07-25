import random
import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.config.db import get_cursor

def _generate_risk_data():
    """
    生成随机风险分数和评级
    
    Returns:
        tuple: (risk_score, risk_rating)
            - risk_score (float): 1-100之间的风险分数，保留2位小数
            - risk_rating (str): 风险等级，'low'|'medium'|'high'
    """
    # 生成1到100之间的随机浮点数，保留2位小数
    risk_score = round(random.uniform(1.0, 100.0), 2)
    
    # 根据风险分数划分等级
    if risk_score <= 33:
        risk_rating = 'low'  # 低风险
    elif risk_score <= 66:
        risk_rating = 'medium'  # 中风险
    else:
        risk_rating = 'high'  # 高风险
    
    return risk_score, risk_rating

def calculate_and_store_risk_score(patient_sn: str, cursor=None):
    """
    为指定患者生成随机风险分数和评级，并存储到 risk_scores 表中
    
    Args:
        patient_sn (str): 患者序列号
        cursor (cursor, optional): 数据库游标，如果提供则使用，否则创建新游标
        
    Returns:
        None: 无返回值，直接更新数据库
    """
    # 生成风险数据
    risk_score, risk_rating = _generate_risk_data()

    try:
        if cursor:
            # 使用传入的游标
            # 检查 patient_SN 是否存在于 lung_cancer_patients 表中
            check_patient_sql = "SELECT patient_SN FROM lung_cancer_patients WHERE patient_SN = %s"
            cursor.execute(check_patient_sql, (patient_sn,))
            if not cursor.fetchone():
                print(f"⚠️ 患者 {patient_sn} 不存在于 lung_cancer_patients 表中，无法计算和存储风险评分。")
                return

            # 插入或更新 risk_scores 表
            upsert_sql = """
            INSERT INTO risk_scores (patient_SN, risk_score, risk_rating)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                risk_score = VALUES(risk_score),
                risk_rating = VALUES(risk_rating);
            """
            cursor.execute(upsert_sql, (patient_sn, risk_score, risk_rating))
            print(f"✅ 患者 {patient_sn} 的风险评分 {risk_score} ({risk_rating}) 已更新。")
        else:
            # 创建新的游标
            with get_cursor() as new_cursor:
                # 检查 patient_SN 是否存在于 lung_cancer_patients 表中
                check_patient_sql = "SELECT patient_SN FROM lung_cancer_patients WHERE patient_SN = %s"
                new_cursor.execute(check_patient_sql, (patient_sn,))
                if not new_cursor.fetchone():
                    print(f"⚠️ 患者 {patient_sn} 不存在于 lung_cancer_patients 表中，无法计算和存储风险评分。")
                    return

                # 插入或更新 risk_scores 表
                upsert_sql = """
                INSERT INTO risk_scores (patient_SN, risk_score, risk_rating)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    risk_score = VALUES(risk_score),
                    risk_rating = VALUES(risk_rating);
                """
                new_cursor.execute(upsert_sql, (patient_sn, risk_score, risk_rating))
                # print(f"✅ 患者 {patient_sn} 的风险评分 {risk_score} ({risk_rating}) 已更新。") # 减少输出
    except Exception as e:
        print(f"❌ 存储患者 {patient_sn} 风险评分失败: {e}")

def batch_calculate_and_store_risk_scores(limit=None):
    """
    遍历所有患者，计算并存储他们的风险评分
    
    使用单个连接和游标进行批量操作，提高性能
    
    Args:
        limit (int, optional): 限制处理的患者数量。默认为 None，表示处理所有患者
        
    Returns:
        None: 无返回值，直接更新数据库
    """
    try:
        # 获取数据库连接和游标
        with get_cursor() as cursor:
            # 构建查询SQL，获取所有患者的 patient_SN
            get_all_patients_sql = "SELECT patient_SN FROM lung_cancer_patients"
            if limit:
                get_all_patients_sql += f" LIMIT {limit}"
            get_all_patients_sql += ";"
            
            # 执行查询
            cursor.execute(get_all_patients_sql)
            patients = cursor.fetchall()

            # 检查是否有患者数据
            if not patients:
                print("ℹ️ lung_cancer_patients 表中没有患者数据。")
                return

            # 开始批量处理
            print(f"开始批量计算和存储 {len(patients)} 位患者的风险评分...")
            for i, patient in enumerate(patients):
                # 为每个患者计算并存储风险评分
                calculate_and_store_risk_score(patient['patient_SN'], cursor=cursor)
                
                # 每处理100个患者输出一次进度，或处理完所有患者
                if (i + 1) % 100 == 0 or (i + 1) == len(patients):
                    print(f"已处理 {i + 1} / {len(patients)} 位患者...")
            print("✅ 批量风险评分计算和存储完成。")
    except Exception as e:
        print(f"❌ 批量计算和存储风险评分失败: {e}")

if __name__ == '__main__':
    # 这是一个独立的脚本，需要模拟 Flask 应用上下文来使用 get_cursor
    from flask import Flask
    
    app = Flask(__name__)
    
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_USER'] = os.getenv('DB_USER', 'root')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '123456') # 修改为 123456
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'medical')

    from mysql.connector import pooling, Error
    try:
        pool = pooling.MySQLConnectionPool(
            pool_name='flask_pool_temp',
            pool_size=1,
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME'],
            autocommit=True,
            connection_timeout=5
        )
        app.config['db_pool'] = pool
        print("🔌 临时数据库连接池已初始化。")
    except Error as e:
        print(f"❌ 初始化临时数据库连接池失败: {e}")
        sys.exit(1)

    with app.app_context():
        # 示例：为单个患者计算并存储风险评分
        # calculate_and_store_risk_score('示例患者SN') 
        
        # 示例：批量计算并存储所有患者的风险评分 (限制为10个)
        # batch_calculate_and_store_risk_scores(limit=10)

        # 示例：批量计算并存储所有患者的风险评分
        batch_calculate_and_store_risk_scores()

    if 'db_pool' in app.config:
        app.config['db_pool']._remove_connections()
        print("🔌 临时数据库连接池已关闭。")

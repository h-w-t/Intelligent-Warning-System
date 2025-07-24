import pymysql
import csv
import re
import os
from datetime import datetime

# 连接数据库
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    db='medical',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(CUR_DIR, 'preprocessed_data.csv')

## 检查建表情况
try:
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES LIKE 'lung_cancer_patients'")
    if cursor.fetchone() is None:
        print("Table 'lung_cancer_patients' does not exist. Creating table...")
        create_patients_table_sql = """
        CREATE TABLE lung_cancer_patients (
            patient_SN VARCHAR(255) PRIMARY KEY,
            sequence_number VARCHAR(255),
            gender VARCHAR(50),
            origin_province VARCHAR(255),
            shanghai_administrative_division VARCHAR(255),
            age INT,
            smoking_status VARCHAR(255),
            lung_cancer_classification VARCHAR(255),
            diagnosis_year INT,
            diagnosis_month INT
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        cursor.execute(create_patients_table_sql)
        print("Table 'lung_cancer_patients' created successfully.")
    
    cursor.execute("SHOW TABLES LIKE 'gene_detection'")
    if cursor.fetchone() is None:
        print("Table 'gene_detection' does not exist. Creating table...")
        create_gene_detection_table_sql = """
        CREATE TABLE gene_detection (
            patient_SN VARCHAR(255) PRIMARY KEY,
            egfr_first_detection_date VARCHAR(255),
            egfr_last_detection_date VARCHAR(255),
            egfr_total_detections INT,
            FOREIGN KEY (patient_SN) REFERENCES lung_cancer_patients(patient_SN)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        cursor.execute(create_gene_detection_table_sql)
        print("Table 'gene_detection' created successfully.")
    connection.commit() # 提交表创建
except Exception as e:
    print(f"Error during table check/creation: {e}")
    # 如果表创建失败，可能需要退出或进一步处理
    exit() # 退出程序，因为没有表无法继续

## 读取CSV文件


def parse_date(date_str):
    """智能解析日期，返回 datetime 对象或 None"""
    if not date_str:
        return None
    
    # 尝试多种日期格式
    formats = [
        '%Y-%m-%d',  # YYYY-MM-DD
        '%Y-%m',     # YYYY-MM
        '%Y'         # YYYY
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    # 如果以上格式都不匹配，尝试从字符串中提取年份
    year_match = re.search(r'(\d{4})', date_str)
    if year_match:
        try:
            return datetime(int(year_match.group(1)), 1, 1) # 默认为1月1日
        except ValueError:
            pass
            
    return None

def extract_month(date_str):
    """专门提取月份部分"""
    # 此函数在 parse_date 优化后可能不再需要，但为了兼容性保留
    dt = parse_date(date_str)
    if dt:
        return dt.month
    return None

with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for i, row in enumerate(csv_reader):
        print(f"处理第 {i+1} 行...")
        
        try:
            # 提取基础信息
            patient_SN = row['patient_SN']
            sequence_number = row['序号']
            gender = row['性别']
            origin_province = row['籍贯(省)'] or None
            shanghai_administrative_division = row['上海十六行政区归属'] or None
            age = int(row['年龄']) if row['年龄'] and row['年龄'].isdigit() else None
            smoking_status = row['是否吸烟']
            lung_cancer_classification = row['肺癌分类']
            
            diagnosis_year = None
            diagnosis_month = None

            # 优先使用“确诊年月”来获取年份和月份
            diagnosis_date_obj = parse_date(row.get('确诊年月'))
            if diagnosis_date_obj:
                diagnosis_year = diagnosis_date_obj.year
                diagnosis_month = diagnosis_date_obj.month
            else:
                # 如果“确诊年月”无效，尝试从“确诊年份”获取年份
                diagnosis_year_str = row.get('确诊年份')
                if diagnosis_year_str:
                    year_obj = parse_date(diagnosis_year_str)
                    if year_obj:
                        diagnosis_year = year_obj.year
            
            print(f"诊断日期: 年份={diagnosis_year}, 月份={diagnosis_month}")
            
            with connection.cursor() as cursor:
                # 插入患者信息
                sql_patients = """
                INSERT INTO lung_cancer_patients (
                    patient_SN, sequence_number, gender, origin_province,
                    shanghai_administrative_division, age, smoking_status,
                    lung_cancer_classification, diagnosis_year, diagnosis_month
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    sequence_number=VALUES(sequence_number), gender=VALUES(gender),
                    origin_province=VALUES(origin_province), shanghai_administrative_division=VALUES(shanghai_administrative_division),
                    age=VALUES(age), smoking_status=VALUES(smoking_status),
                    lung_cancer_classification=VALUES(lung_cancer_classification),
                    diagnosis_year=VALUES(diagnosis_year), diagnosis_month=VALUES(diagnosis_month);
                """
                cursor.execute(sql_patients, (
                    patient_SN, sequence_number, gender, origin_province,
                    shanghai_administrative_division, age, smoking_status,
                    lung_cancer_classification, diagnosis_year, diagnosis_month
                ))
                
                # 处理基因检测数据
                egfr_first_detection_date_str = None
                first_date_obj = parse_date(row.get('首次检测日期EGFR'))
                if first_date_obj:
                    egfr_first_detection_date_str = first_date_obj.strftime('%Y-%m') # 统一格式为 YYYY-MM

                egfr_last_detection_date_str = None
                last_date_obj = parse_date(row.get('末次检测日期EGFR'))
                if last_date_obj:
                    egfr_last_detection_date_str = last_date_obj.strftime('%Y-%m') # 统一格式为 YYYY-MM
                
                egfr_total_detections = None
                if '总检测次数EGFR' in row and row['总检测次数EGFR'] and row['总检测次数EGFR'].isdigit():
                    egfr_total_detections = int(row['总检测次数EGFR'])
                
                # 插入基因检测数据
                sql_gene_detection = """
                INSERT INTO gene_detection (
                    patient_SN,
                    egfr_first_detection_date,
                    egfr_last_detection_date,
                    egfr_total_detections
                ) VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    egfr_first_detection_date=VALUES(egfr_first_detection_date),
                    egfr_last_detection_date=VALUES(egfr_last_detection_date),
                    egfr_total_detections=VALUES(egfr_total_detections);
                """
                cursor.execute(sql_gene_detection, (
                    patient_SN,
                    egfr_first_detection_date_str,
                    egfr_last_detection_date_str,
                    egfr_total_detections
                ))
                
            connection.commit()
            print(f"第 {i+1} 行 (SN: {patient_SN}) 成功插入/更新")
            
        except Exception as e:
            connection.rollback()
            print(f"处理第 {i+1} 行 (SN: {row.get('patient_SN', 'N/A')}) 时出错: {e}")
            print(f"出错行数据: {row}")

connection.close()
print("数据导入完成")
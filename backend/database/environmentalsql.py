#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
import csv
import re
from datetime import datetime
import os

DB_CFG = dict(
    host='localhost',
    user='root',
    password='123456',
    db='medical',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CUR_DIR, 'preprocessed_data.csv')

# ---------- 建表 ----------
CREATE_SQL = [
    "DROP TABLE IF EXISTS environmental_data;",
    """
    CREATE TABLE environmental_data (
        patient_SN VARCHAR(64) PRIMARY KEY,
        diag_year  SMALLINT NULL,
        diag_month TINYINT  NULL,
        aqi_12_month_avg            DOUBLE NULL,
        co_12_month_avg             DOUBLE NULL,
        co_24h_12_month_avg         DOUBLE NULL,
        no2_12_month_avg            DOUBLE NULL,
        no2_24h_12_month_avg        DOUBLE NULL,
        o3_12_month_avg             DOUBLE NULL,
        o3_24h_12_month_avg         DOUBLE NULL,
        o3_8h_12_month_avg          DOUBLE NULL,
        o3_8h_24h_12_month_avg      DOUBLE NULL,
        pm10_12_month_avg           DOUBLE NULL,
        pm10_24h_12_month_avg       DOUBLE NULL,
        pm2_5_12_month_avg          DOUBLE NULL,
        pm2_5_24h_12_month_avg      DOUBLE NULL,
        so2_12_month_avg            DOUBLE NULL,
        so2_24h_12_month_avg        DOUBLE NULL,
        aqi_24_month_avg            DOUBLE NULL,
        co_24_month_avg             DOUBLE NULL,
        co_24h_24_month_avg         DOUBLE NULL,
        no2_24_month_avg            DOUBLE NULL,
        no2_24h_24_month_avg        DOUBLE NULL,
        o3_24_month_avg             DOUBLE NULL,
        o3_24h_24_month_avg         DOUBLE NULL,
        o3_8h_24_month_avg          DOUBLE NULL,
        o3_8h_24h_24_month_avg      DOUBLE NULL,
        pm10_24_month_avg           DOUBLE NULL,
        pm10_24h_24_month_avg       DOUBLE NULL,
        pm2_5_24_month_avg          DOUBLE NULL,
        pm2_5_24h_24_month_avg      DOUBLE NULL,
        so2_24_month_avg            DOUBLE NULL,
        so2_24h_24_month_avg        DOUBLE NULL,
        aqi_36_month_avg            DOUBLE NULL,
        co_36_month_avg             DOUBLE NULL,
        co_24h_36_month_avg         DOUBLE NULL,
        no2_36_month_avg            DOUBLE NULL,
        no2_24h_36_month_avg        DOUBLE NULL,
        o3_36_month_avg             DOUBLE NULL,
        o3_24h_36_month_avg         DOUBLE NULL,
        o3_8h_36_month_avg          DOUBLE NULL,
        o3_8h_24h_36_month_avg      DOUBLE NULL,
        pm10_36_month_avg           DOUBLE NULL,
        pm10_24h_36_month_avg       DOUBLE NULL,
        pm2_5_36_month_avg          DOUBLE NULL,
        pm2_5_24h_36_month_avg      DOUBLE NULL,
        so2_36_month_avg            DOUBLE NULL,
        so2_24h_36_month_avg        DOUBLE NULL,
        aqi_3_month_avg             DOUBLE NULL,
        co_3_month_avg              DOUBLE NULL,
        co_24h_3_month_avg          DOUBLE NULL,
        no2_3_month_avg             DOUBLE NULL,
        no2_24h_3_month_avg         DOUBLE NULL,
        o3_3_month_avg              DOUBLE NULL,
        o3_24h_3_month_avg          DOUBLE NULL,
        o3_8h_3_month_avg           DOUBLE NULL,
        o3_8h_24h_3_month_avg       DOUBLE NULL,
        pm10_3_month_avg            DOUBLE NULL,
        pm10_24h_3_month_avg        DOUBLE NULL,
        pm2_5_3_month_avg           DOUBLE NULL,
        pm2_5_24h_3_month_avg       DOUBLE NULL,
        so2_3_month_avg             DOUBLE NULL,
        so2_24h_3_month_avg         DOUBLE NULL,
        aqi_6_month_avg             DOUBLE NULL,
        co_6_month_avg              DOUBLE NULL,
        co_24h_6_month_avg          DOUBLE NULL,
        no2_6_month_avg             DOUBLE NULL,
        no2_24h_6_month_avg         DOUBLE NULL,
        o3_6_month_avg              DOUBLE NULL,
        o3_24h_6_month_avg          DOUBLE NULL,
        o3_8h_6_month_avg           DOUBLE NULL,
        o3_8h_24h_6_month_avg       DOUBLE NULL,
        pm10_6_month_avg            DOUBLE NULL,
        pm10_24h_6_month_avg        DOUBLE NULL,
        pm2_5_6_month_avg           DOUBLE NULL,
        pm2_5_24h_6_month_avg       DOUBLE NULL,
        so2_6_month_avg             DOUBLE NULL,
        so2_24h_6_month_avg         DOUBLE NULL,
        INDEX idx_year_month (diag_year, diag_month)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
]

# ---------- 字段映射 ----------
FIELD_MAP = {
    'AQI_12_month_avg': 'aqi_12_month_avg',
    'CO_12_month_avg': 'co_12_month_avg',
    'CO_24h_12_month_avg': 'co_24h_12_month_avg',
    'NO2_12_month_avg': 'no2_12_month_avg',
    'NO2_24h_12_month_avg': 'no2_24h_12_month_avg',
    'O3_12_month_avg': 'o3_12_month_avg',
    'O3_24h_12_month_avg': 'o3_24h_12_month_avg',
    'O3_8h_12_month_avg': 'o3_8h_12_month_avg',
    'O3_8h_24h_12_month_avg': 'o3_8h_24h_12_month_avg',
    'PM10_12_month_avg': 'pm10_12_month_avg',
    'PM10_24h_12_month_avg': 'pm10_24h_12_month_avg',
    'PM2.5_12_month_avg': 'pm2_5_12_month_avg',
    'PM2.5_24h_12_month_avg': 'pm2_5_24h_12_month_avg',
    'SO2_12_month_avg': 'so2_12_month_avg',
    'SO2_24h_12_month_avg': 'so2_24h_12_month_avg',
    'AQI_24_month_avg': 'aqi_24_month_avg',
    'CO_24_month_avg': 'co_24_month_avg',
    'CO_24h_24_month_avg': 'co_24h_24_month_avg',
    'NO2_24_month_avg': 'no2_24_month_avg',
    'NO2_24h_24_month_avg': 'no2_24h_24_month_avg',
    'O3_24_month_avg': 'o3_24_month_avg',
    'O3_24h_24_month_avg': 'o3_24h_24_month_avg',
    'O3_8h_24_month_avg': 'o3_8h_24_month_avg',
    'O3_8h_24h_24_month_avg': 'o3_8h_24h_24_month_avg',
    'PM10_24_month_avg': 'pm10_24_month_avg',
    'PM10_24h_24_month_avg': 'pm10_24h_24_month_avg',
    'PM2.5_24_month_avg': 'pm2_5_24_month_avg',
    'PM2.5_24h_24_month_avg': 'pm2_5_24h_24_month_avg',
    'SO2_24_month_avg': 'so2_24_month_avg',
    'SO2_24h_24_month_avg': 'so2_24h_24_month_avg',
    'AQI_36_month_avg': 'aqi_36_month_avg',
    'CO_36_month_avg': 'co_36_month_avg',
    'CO_24h_36_month_avg': 'co_24h_36_month_avg',
    'NO2_36_month_avg': 'no2_36_month_avg',
    'NO2_24h_36_month_avg': 'no2_24h_36_month_avg',
    'O3_36_month_avg': 'o3_36_month_avg',
    'O3_24h_36_month_avg': 'o3_24h_36_month_avg',
    'O3_8h_36_month_avg': 'o3_8h_36_month_avg',
    'O3_8h_24h_36_month_avg': 'o3_8h_24h_36_month_avg',
    'PM10_36_month_avg': 'pm10_36_month_avg',
    'PM10_24h_36_month_avg': 'pm10_24h_36_month_avg',
    'PM2.5_36_month_avg': 'pm2_5_36_month_avg',
    'PM2.5_24h_36_month_avg': 'pm2_5_24h_36_month_avg',
    'SO2_36_month_avg': 'so2_36_month_avg',
    'SO2_24h_36_month_avg': 'so2_24h_36_month_avg',
    'AQI_3_month_avg': 'aqi_3_month_avg',
    'CO_3_month_avg': 'co_3_month_avg',
    'CO_24h_3_month_avg': 'co_24h_3_month_avg',
    'NO2_3_month_avg': 'no2_3_month_avg',
    'NO2_24h_3_month_avg': 'no2_24h_3_month_avg',
    'O3_3_month_avg': 'o3_3_month_avg',
    'O3_24h_3_month_avg': 'o3_24h_3_month_avg',
    'O3_8h_3_month_avg': 'o3_8h_3_month_avg',
    'O3_8h_24h_3_month_avg': 'o3_8h_24h_3_month_avg',
    'PM10_3_month_avg': 'pm10_3_month_avg',
    'PM10_24h_3_month_avg': 'pm10_24h_3_month_avg',
    'PM2.5_3_month_avg': 'pm2_5_3_month_avg',
    'PM2.5_24h_3_month_avg': 'pm2_5_24h_3_month_avg',
    'SO2_3_month_avg': 'so2_3_month_avg',
    'SO2_24h_3_month_avg': 'so2_24h_3_month_avg',
    'AQI_6_month_avg': 'aqi_6_month_avg',
    'CO_6_month_avg': 'co_6_month_avg',
    'CO_24h_6_month_avg': 'co_24h_6_month_avg',
    'NO2_6_month_avg': 'no2_6_month_avg',
    'NO2_24h_6_month_avg': 'no2_24h_6_month_avg',
    'O3_6_month_avg': 'o3_6_month_avg',
    'O3_24h_6_month_avg': 'o3_24h_6_month_avg',
    'O3_8h_6_month_avg': 'o3_8h_6_month_avg',
    'O3_8h_24h_6_month_avg': 'o3_8h_24h_6_month_avg',
    'PM10_6_month_avg': 'pm10_6_month_avg',
    'PM10_24h_6_month_avg': 'pm10_24h_6_month_avg',
    'PM2.5_6_month_avg': 'pm2_5_6_month_avg',
    'PM2.5_24h_6_month_avg': 'pm2_5_24h_6_month_avg',
    'SO2_6_month_avg': 'so2_6_month_avg',
    'SO2_24h_6_month_avg': 'so2_24h_6_month_avg'
}

# ---------- 日期解析 ----------
def parse_date(date_str):
    """智能解析日期，优先处理完整日期"""
    if not date_str:
        return None, None
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.year, dt.month
        if re.match(r'^\d{4}-\d{2}$', date_str):
            dt = datetime.strptime(date_str, '%Y-%m')
            return dt.year, dt.month
        if re.match(r'^\d{4}$', date_str):
            return int(date_str), None
    except Exception:
        pass
    # 兜底提取年份
    year_match = re.search(r'(\d{4})', date_str)
    if year_match:
        return int(year_match.group(1)), None
    return None, None

def extract_month(date_str):
    """专门提取月份"""
    if not date_str:
        return None
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return int(date_str.split('-')[1])
        if re.match(r'^\d{4}-\d{2}$', date_str):
            return int(date_str.split('-')[1])
        month_match = re.search(r'-(\d{1,2})', date_str)
        if month_match:
            month = int(month_match.group(1))
            if 1 <= month <= 12:
                return month
        digits = re.findall(r'\d{1,2}', date_str)
        if len(digits) >= 2:
            return int(digits[1])
    except Exception:
        pass
    return None

# ---------- 主流程 ----------
def main():
    conn = pymysql.connect(**DB_CFG)
    try:
        # 1. 建表
        with conn.cursor() as cur:
            for sql in CREATE_SQL:
                cur.execute(sql)
        conn.commit()
        print("✅ environmental_data 表已重建")

        # 2. 读取 CSV
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # 列名统一小写，避免大小写不一致
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

            # 固定列顺序
            base_cols = ['patient_sn', 'diag_year', 'diag_month']
            env_cols  = list(FIELD_MAP.values())
            all_cols  = base_cols + env_cols

            total = succ = 0
            batch = []

            for row in reader:
                total += 1

                # 解析年月
                year, month = parse_date(row.get('确诊年月', ''))
                if month is None:
                    month = extract_month(row.get('确诊年月', ''))

                # 基础值
                values = [row.get('patient_sn'), year, month]

                # 其余环境字段
                for k in FIELD_MAP:
                    val = row.get(k.lower(), '')
                    try:
                        values.append(float(val) if val.strip() else None)
                    except ValueError:
                        values.append(None)

                batch.append(values)

                # 每 1000 行批量提交
                if len(batch) == 1000:
                    with conn.cursor() as cur:
                        sql = f"INSERT INTO environmental_data ({','.join(all_cols)}) VALUES ({','.join(['%s']*len(all_cols))})"
                        cur.executemany(sql, batch)
                    conn.commit()
                    succ += len(batch)
                    print(f"已插入 {succ}/{total} 行")
                    batch.clear()

            # 剩余不足 1000 行
            if batch:
                with conn.cursor() as cur:
                    sql = f"INSERT INTO environmental_data ({','.join(all_cols)}) VALUES ({','.join(['%s']*len(all_cols))})"
                    cur.executemany(sql, batch)
                conn.commit()
                succ += len(batch)

            print(f"\n🎉 完成！共 {total} 行，成功 {succ} 行")

    except Exception as e:
        conn.rollback()
        print("❌ 错误：", e)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
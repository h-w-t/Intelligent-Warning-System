# config/db.py
import os
import mysql.connector
from mysql.connector import pooling, Error
from flask import current_app
from contextlib import contextmanager
import logging

# 初始化日志
logging.basicConfig(level=logging.INFO)

def init_app(app):
    """初始化数据库连接池并绑定到 Flask app"""
    try:
        pool = pooling.MySQLConnectionPool(
            pool_name='flask_pool',
            pool_size=10,
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '123123'),
            database=os.getenv('DB_NAME', 'lung_cancer'),
            autocommit=True,
            connection_timeout=5
        )
        app.config['db_pool'] = pool
        logging.info("🔌 数据库连接池已初始化")
    except Error as e:
        logging.error(f"❌ 初始化数据库连接池失败: {e}")
        raise

@contextmanager
def get_cursor(dictionary=True):
    """获取数据库连接和游标"""
    try:
        conn = current_app.config['db_pool'].get_connection()
        cur = conn.cursor(dictionary=dictionary)
        logging.info("✅ 成功获取数据库连接")
        yield cur
    except mysql.connector.Error as e:
        logging.error(f"❌ 数据库操作失败: {e}")
        raise
    except Exception as e:
        logging.error(f"⚠️ 未知错误: {e}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
            logging.info("🔌 数据库连接已释放")
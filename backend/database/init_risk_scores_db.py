import pymysql
import os
import sys

# 将项目根目录添加到 Python 路径，以便导入模块
# os.path.abspath 获取当前文件的绝对路径
# os.path.dirname 获取当前文件的目录
# os.path.join 将目录、'..' 和文件名组合成路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# 从数据库配置模块导入 get_cursor 函数
from backend.config.db import get_cursor

def create_risk_scores_table():
    """
    在数据库中创建 risk_scores 表。
    如果表已存在，则忽略。
    """
    try:
        # 使用 get_cursor 获取数据库游标，它会自动处理连接和释放
        with get_cursor() as cursor:
            # 定义创建表的 SQL 语句
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS risk_scores (
                patient_SN VARCHAR(255) PRIMARY KEY,  -- 患者序列号，作为主键
                risk_score FLOAT,                     -- 风险分数
                risk_rating VARCHAR(50),              -- 风险评级（如 'low', 'medium', 'high'）
                FOREIGN KEY (patient_SN) REFERENCES lung_cancer_patients(patient_SN) -- 外键约束，关联到患者表
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; -- 设置字符集和排序规则
            """
            # 执行 SQL 语句
            cursor.execute(create_table_sql)
            # 打印成功信息
            print("✅ 表 'risk_scores' 创建成功或已存在。")
    except Exception as e:
        # 捕获并打印任何异常
        print(f"❌ 创建表 'risk_scores' 失败: {e}")

# 当脚本直接运行时执行以下代码
if __name__ == '__main__':
    # 这是一个独立的脚本，需要模拟 Flask 应用上下文来使用 get_cursor
    # 实际应用中，get_cursor 会在 Flask 应用上下文中自动获取 db_pool
    # 这里为了测试和独立运行，需要手动设置一个临时的 db_pool
    
    # 导入 Flask 和 current_app
    from flask import Flask
    
    # 创建一个临时的 Flask 应用实例
    app = Flask(__name__)
    
    # 设置数据库连接信息，这里直接使用环境变量或默认值
    # 注意：这里需要确保环境变量已设置，或者提供默认值
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_USER'] = os.getenv('DB_USER', 'root')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '123456') # 修改为 123456
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'medical') # 确保这里是 medical

    # 初始化数据库连接池
    from mysql.connector import pooling, Error
    try:
        pool = pooling.MySQLConnectionPool(
            pool_name='flask_pool_temp',  # 连接池名称
            pool_size=1,                  # 临时池，大小设为1
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME'],
            autocommit=True,              # 自动提交
            connection_timeout=5          # 连接超时时间
        )
        # 将连接池绑定到 Flask 应用的配置中
        app.config['db_pool'] = pool
        print("🔌 临时数据库连接池已初始化。")
    except Error as e:
        # 如果初始化失败，打印错误并退出
        print(f"❌ 初始化临时数据库连接池失败: {e}")
        sys.exit(1)

    # 在应用上下文中运行创建表的函数
    with app.app_context():
        create_risk_scores_table()

    # 关闭临时连接池
    if 'db_pool' in app.config:
        app.config['db_pool']._remove_connections()
        print("🔌 临时数据库连接池已关闭。")

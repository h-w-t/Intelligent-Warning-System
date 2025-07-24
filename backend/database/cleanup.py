import pymysql
import pandas as pd
from sqlalchemy import create_engine
import sys

def clean_database_data():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'db': 'medical',
        'charset': 'utf8mb4'
    }
    
    try:
        # 创建SQLAlchemy引擎
        engine = create_engine(
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['db']}?charset={db_config['charset']}"
        )
        
        # 连接数据库
        connection = pymysql.connect(**db_config)
        
        # 获取所有表名
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
        
        print(f"开始数据库清理，共发现 {len(tables)} 张表")
        print("="*50)
        
        # 处理每个表
        for table in tables:
            print(f"\n处理表: {table}")
            
            try:
                # 读取表数据到DataFrame
                df = pd.read_sql(f"SELECT * FROM {table}", engine)
                
                # 计算处理前的行数
                initial_count = len(df)
                print(f"初始行数: {initial_count}")
                
                # 定义无效数据计数器
                deleted_sn_duplicates = 0
                deleted_invalid_month = 0
                deleted_invalid_age = 0
                
                if table == 'environmental_data':
                    # 步骤1: 删除所有列都为NULL的行
                    non_null_counts = df.notnull().sum(axis=1)
                    df_cleaned = df[non_null_counts > 0]
                    null_rows_deleted = initial_count - len(df_cleaned)
                    
                    if null_rows_deleted > 0:
                        print(f"已删除 {null_rows_deleted} 行全NULL数据")
                    
                    # 步骤2: 删除SN码重复的行
                    # 统计重复行
                    duplicate_counts = df_cleaned.duplicated(subset=['patient_SN'], keep=False)
                    duplicates_to_check = df_cleaned[duplicate_counts]
                    
                    if not duplicates_to_check.empty:
                        print(f"发现 {len(duplicates_to_check)} 行可能的SN码重复数据")
                        print("正在分析重复数据...")
                        
                        # 找出确实重复的SN码
                        duplicate_sns = duplicates_to_check['patient_SN'].value_counts()
                        duplicate_sns = duplicate_sns[duplicate_sns > 1].index.tolist()
                        
                        # 删除重复行（保留第一条）
                        df_deduplicated = df_cleaned.drop_duplicates(subset=['patient_SN'], keep='first')
                        
                        # 计算删除的重复行数
                        deleted_sn_duplicates = len(df_cleaned) - len(df_deduplicated)
                        print(f"已删除 {deleted_sn_duplicates} 行SN码重复数据")
                        
                        print("删除的重复数据样例:")
                        print(df_cleaned[df_cleaned['patient_SN'].isin(duplicate_sns)].head(5))
                        
                        df_cleaned = df_deduplicated
                    
                    # 最终将清理后的数据写回数据库
                    df_cleaned.to_sql(table, engine, if_exists='replace', index=False)
                    final_count = len(df_cleaned)
                    
                elif table == 'lung_cancer_patients':
                    # 处理病例表 - 严格数据清洗
                    print("处理病例表 - 严格数据清洗逻辑")
                    print("一位患者只能有一份数据，去除SN码重复、月份不合理的行")
                    
                    # 步骤1: 删除所有列都为NULL的行
                    non_null_counts = df.notnull().sum(axis=1)
                    df_cleaned = df[non_null_counts > 0]
                    null_rows_deleted = initial_count - len(df_cleaned)
                    
                    if null_rows_deleted > 0:
                        print(f"已删除 {null_rows_deleted} 行全NULL数据")
                    
                    # 步骤2: 删除SN码重复的行（每个患者只保留一条记录）
                    duplicate_counts = df_cleaned.duplicated(subset=['patient_SN'], keep=False)
                    duplicates_to_check = df_cleaned[duplicate_counts]
                    
                    if not duplicates_to_check.empty:
                        print(f"发现 {len(duplicates_to_check)} 行可能的SN码重复数据")
                        print("正在分析重复数据...")
                        
                        # 找出确实重复的SN码
                        duplicate_sns = duplicates_to_check['patient_SN'].value_counts()
                        duplicate_sns = duplicate_sns[duplicate_sns > 1].index.tolist()
                        
                        # 删除重复行（保留第一条）
                        df_deduplicated = df_cleaned.drop_duplicates(subset=['patient_SN'], keep='first')
                        
                        # 计算删除的重复行数
                        deleted_sn_duplicates = len(df_cleaned) - len(df_deduplicated)
                        print(f"已删除 {deleted_sn_duplicates} 行SN码重复数据")
                        
                        print("删除的重复数据样例:")
                        print(df_cleaned[df_cleaned['patient_SN'].isin(duplicate_sns)].head(5))
                        
                        df_cleaned = df_deduplicated
                    
                    # 步骤3: 删除月份不合理的行
                    if 'diagnosis_month' in df_cleaned.columns:
                        # 有效的月份范围是1-12
                        invalid_month_mask = (
                            ~df_cleaned['diagnosis_month'].isnull() &
                            (df_cleaned['diagnosis_month'] < 1) | 
                            (df_cleaned['diagnosis_month'] > 12)
                        )
                        
                        invalid_month_rows = df_cleaned[invalid_month_mask]
                        
                        if not invalid_month_rows.empty:
                            print(f"发现 {len(invalid_month_rows)} 行无效月份数据 (范围应在1-12之间)")
                            print("无效月份数据样例:")
                            print(invalid_month_rows[['patient_SN', 'sequence_number', 'diagnosis_month']].head(5))
                            
                            # 删除无效月份行
                            df_cleaned = df_cleaned[~invalid_month_mask]
                            deleted_invalid_month = len(invalid_month_rows)
                    
                    # 步骤4: 删除年龄不合理的行（保留199测试数据）
                    if 'age' in df_cleaned.columns:
                        # 有效的年龄范围是0-200，但199作为特殊测试值保留
                        invalid_age_mask = (
                            ~df_cleaned['age'].isnull() &
                            (
                                (df_cleaned['age'] < 0) | 
                                (df_cleaned['age'] > 200) | 
                                (df_cleaned['age'] == 0)  # 0岁通常无效
                            ) &
                            (df_cleaned['age'] != 199)  # 保留199测试值
                        )
                        
                        invalid_age_rows = df_cleaned[invalid_age_mask]
                        
                        if not invalid_age_rows.empty:
                            print(f"发现 {len(invalid_age_rows)} 行无效年龄数据 (范围应在1-200之间)")
                            print("无效年龄数据样例:")
                            print(invalid_age_rows[['patient_SN', 'sequence_number', 'age']].head(5))
                            
                            # 删除无效年龄行
                            df_cleaned = df_cleaned[~invalid_age_mask]
                            deleted_invalid_age = len(invalid_age_rows)
                    
                    # 步骤5: 确保存在199岁测试数据
                    if 'age' in df_cleaned.columns:
                        test_patients = df_cleaned[df_cleaned['age'] == 199]
                        if test_patients.empty:
                            print("添加199岁测试患者数据")
                            
                            # 创建测试数据行
                            test_data = pd.DataFrame({
                                'patient_SN': ['TEST_199_AGE'],
                                'sequence_number': ['TEST199'],
                                'gender': ['男'],
                                'age': [199],
                                'smoking_status': ['否'],
                                'lung_cancer_classification': ['测试数据'],
                                'diagnosis_year': [2025],
                                'diagnosis_month': [7],
                                # 添加其他必要字段...
                            })
                            
                            # 合并数据
                            df_cleaned = pd.concat([df_cleaned, test_data], ignore_index=True)
                    
                    # 将清理后的数据写回数据库
                    df_cleaned.to_sql(table, engine, if_exists='replace', index=False)
                    final_count = len(df_cleaned)
                    
                    # 输出删除统计
                    print(f"总计删除数据: {initial_count - final_count} 行")
                    print(f"  - SN码重复删除: {deleted_sn_duplicates} 行")
                    print(f"  - 无效月份删除: {deleted_invalid_month} 行")
                    print(f"  - 无效年龄删除: {deleted_invalid_age} 行")
                    
                elif table == 'gene_detection':
                    # 处理基因检测表 - 删除SN码重复的行
                    print("处理基因检测表 - 去除SN码重复的行")
                    
                    # 步骤1: 删除所有列都为NULL的行
                    non_null_counts = df.notnull().sum(axis=1)
                    df_cleaned = df[non_null_counts > 0]
                    null_rows_deleted = initial_count - len(df_cleaned)
                    
                    if null_rows_deleted > 0:
                        print(f"已删除 {null_rows_deleted} 行全NULL数据")
                    
                    # 步骤2: 删除SN码重复的行
                    duplicate_counts = df_cleaned.duplicated(subset=['patient_SN'], keep=False)
                    duplicates_to_check = df_cleaned[duplicate_counts]
                    
                    if not duplicates_to_check.empty:
                        print(f"发现 {len(duplicates_to_check)} 行可能的SN码重复数据")
                        print("正在分析重复数据...")
                        
                        # 找出确实重复的SN码
                        duplicate_sns = duplicates_to_check['patient_SN'].value_counts()
                        duplicate_sns = duplicate_sns[duplicate_sns > 1].index.tolist()
                        
                        # 删除重复行（保留第一条）
                        df_deduplicated = df_cleaned.drop_duplicates(subset=['patient_SN'], keep='first')
                        
                        # 计算删除的重复行数
                        deleted_sn_duplicates = len(df_cleaned) - len(df_deduplicated)
                        print(f"已删除 {deleted_sn_duplicates} 行SN码重复数据")
                        
                        print("删除的重复数据样例:")
                        print(df_cleaned[df_cleaned['patient_SN'].isin(duplicate_sns)].head(5))
                        
                        df_cleaned = df_deduplicated
                    
                    # 最终将清理后的数据写回数据库
                    df_cleaned.to_sql(table, engine, if_exists='replace', index=False)
                    final_count = len(df_cleaned)
                    
                else:
                    # 对于其他表，删除SN码重复的行
                    print("处理普通表 - 去除SN码重复的行")
                    
                    # 步骤1: 删除所有列都为NULL的行
                    non_null_counts = df.notnull().sum(axis=1)
                    df_cleaned = df[non_null_counts > 0]
                    null_rows_deleted = initial_count - len(df_cleaned)
                    
                    if null_rows_deleted > 0:
                        print(f"已删除 {null_rows_deleted} 行全NULL数据")
                    
                    # 步骤2: 删除SN码重复的行
                    duplicate_counts = df_cleaned.duplicated(subset=['patient_SN'], keep=False)
                    duplicates_to_check = df_cleaned[duplicate_counts]
                    
                    if not duplicates_to_check.empty:
                        print(f"发现 {len(duplicates_to_check)} 行可能的SN码重复数据")
                        print("正在分析重复数据...")
                        
                        # 找出确实重复的SN码
                        duplicate_sns = duplicates_to_check['patient_SN'].value_counts()
                        duplicate_sns = duplicate_sns[duplicate_sns > 1].index.tolist()
                        
                        # 删除重复行（保留第一条）
                        df_deduplicated = df_cleaned.drop_duplicates(subset=['patient_SN'], keep='first')
                        
                        # 计算删除的重复行数
                        deleted_sn_duplicates = len(df_cleaned) - len(df_deduplicated)
                        print(f"已删除 {deleted_sn_duplicates} 行SN码重复数据")
                        
                        print("删除的重复数据样例:")
                        print(df_cleaned[df_cleaned['patient_SN'].isin(duplicate_sns)].head(5))
                        
                        df_cleaned = df_deduplicated
                    
                    # 最终将清理后的数据写回数据库
                    df_cleaned.to_sql(table, engine, if_exists='replace', index=False)
                    final_count = len(df_cleaned)
                
                print(f"最终行数: {final_count}")
                print(f"表 {table} 清理完成")
                print("-"*50)
                
            except Exception as e:
                print(f"处理表 {table} 时发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
                print(f"跳过表 {table} 的处理")
                print("-"*50)
        
        print("\n数据库清理完成！")
        
    except Exception as e:
        print(f"数据库连接错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    clean_database_data()
# mcp_server.py
from mcp.server.fastmcp import FastMCP
import sqlite3
import os
import re
from typing import List, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SQLiteMCP")

# 创建 MCP 服务器
mcp = FastMCP("SQLite Data Service")

# 配置数据库路径
DB_PATH = "D:\\python-file\\MCP_test\\mcp.db"
logger.info(f"Using database: {DB_PATH}")

# 数据库连接
def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 返回字典格式结果
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

# 安全验证：只允许 SELECT 查询
def is_readonly_query(sql: str) -> bool:
    """检查是否为只读查询"""
    # 清理SQL语句
    cleaned_sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)  # 移除注释
    cleaned_sql = re.sub(r'/\*.*?\*/', '', cleaned_sql, flags=re.DOTALL)  # 移除块注释
    cleaned_sql = cleaned_sql.strip().upper()

    # 检查是否以SELECT开头
    if not cleaned_sql.startswith("SELECT"):
        return False

    # 检查是否包含禁止的命令
    forbidden_commands = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "ATTACH", "DETACH"]
    for cmd in forbidden_commands:
        if cmd in cleaned_sql:
            return False

    # 检查是否包含可能危险的SQLite特定命令
    if "PRAGMA" in cleaned_sql and not cleaned_sql.startswith("PRAGMA TABLE_INFO"):
        return False

    return True

# 资源：获取所有表名
@mcp.resource("sqlite://tables")
def get_tables() -> List[str]:
    """获取数据库中所有表的名称"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row['name'] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error fetching tables: {str(e)}")
        return []

# 资源：获取表结构
@mcp.resource("sqlite://table/{table_name}")
def get_table_schema(table_name: str) -> List[Dict[str, Any]]:
    """获取指定表的结构信息"""
    try:
        # 验证表名是否有效
        tables = get_tables()
        if table_name not in tables:
            logger.warning(f"Invalid table name requested: {table_name}")
            return []

        with get_db_connection() as conn:
            cursor = conn.execute(f"PRAGMA table_info('{table_name}')")
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error fetching schema for {table_name}: {str(e)}")
        return []

# 工具：执行只读 SQL 查询
@mcp.tool()
def run_sql_query(query: str, limit: int = 100) -> Dict[str, Any]:
    """
    执行只读 SQL 查询（仅支持 SELECT 语句）

    参数:
        query: 要执行的 SQL 查询语句
        limit: 结果集最大行数（默认100）

    返回:
        包含查询结果和元数据的字典
    """
    try:
        # 验证查询是否安全
        if not is_readonly_query(query):
            logger.warning(f"Attempted unsafe query: {query}")
            return {
                "error": "Only SELECT queries are allowed",
                "query": query
            }

        # 自动添加 LIMIT 子句（如果不存在）
        modified_query = query
        upper_query = query.upper()
        if "LIMIT" not in upper_query and limit > 0:
            if ";" in query:
                modified_query = query.replace(";", f" LIMIT {limit};")
            else:
                modified_query += f" LIMIT {limit}"

        with get_db_connection() as conn:
            cursor = conn.execute(modified_query)
            results = [dict(row) for row in cursor.fetchall()]

            # 获取列信息
            columns = [{"name": desc[0], "type": desc[1]} for desc in cursor.description]

            return {
                "query": modified_query,
                "columns": columns,
                "results": results,
                "row_count": len(results),
                "limit_applied": "LIMIT" not in upper_query and limit > 0
            }
    except sqlite3.Error as e:
        logger.error(f"Query error: {str(e)} - Query: {query}")
        return {
            "error": str(e),
            "query": query,
            "suggestion": "检查查询语法和表结构"
        }

# 工具：获取数据库结构摘要
@mcp.tool()
def get_database_summary() -> Dict[str, Any]:
    """
    获取数据库的完整结构摘要

    返回:
        包含数据库元数据的字典
    """
    tables = get_tables()
    database_info = {
        "database": DB_PATH,
        "tables": []
    }

    for table in tables:
        schema = get_table_schema(table)
        columns = [{"name": col["name"], "type": col["type"]} for col in schema]
        database_info["tables"].append({
            "name": table,
            "columns": columns
        })

    return database_info
def main() -> None:
    # 启动 MCP 服务器 (SSE 模式)
    logger.info("Starting SQLite MCP Server on SSE transport...")
    logger.info(f"Database: {DB_PATH}")
    logger.info("Available resources:")
    logger.info(" - sqlite://tables (GET): List all tables")
    logger.info(" - sqlite://table/{table_name} (GET): Get table schema")
    logger.info("Available tools:")
    logger.info(" - run_sql_query (POST): Execute SQL query")
    logger.info(" - get_database_summary (POST): Get database structure")

    try:
        # 测试数据库连接
        with get_db_connection():
            logger.info("Database connection test successful")

        # 启动服务器
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")

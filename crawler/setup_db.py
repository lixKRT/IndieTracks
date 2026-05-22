"""执行 create_database.sql 建表脚本。"""
import psycopg2, sys

SQL_PATH = r"..\database\create_database.sql"

with open(SQL_PATH, "r", encoding="utf-8") as f:
    sql = f.read()

conn = psycopg2.connect(
    host="localhost", port=5432, user="postgres",
    password="54610", database="indietracks",
)
conn.autocommit = True
cur = conn.cursor()

# 按 ; 切割后逐条执行，跳过空块和纯注释
for i, stmt in enumerate(sql.split(";")):
    s = stmt.strip()
    if not s or s.startswith("--"):
        continue
    try:
        cur.execute(s)
        line1 = s.split("\n")[0].strip()[:70]
        print(f"  OK  {line1}")
    except Exception as e:
        line1 = s.split("\n")[0].strip()[:70]
        msg = str(e).split("\n")[0][:80]
        print(f"  SKIP {line1} | {msg}")

cur.close()
conn.close()
print("\n建表完成")

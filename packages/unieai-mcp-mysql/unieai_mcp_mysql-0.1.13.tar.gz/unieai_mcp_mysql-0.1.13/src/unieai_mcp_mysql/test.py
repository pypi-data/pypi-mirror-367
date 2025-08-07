# from sqlalchemy import create_engine, text

# engine = create_engine("mysql+pymysql://root:11111111@127.0.0.1:3306/testdb")

# try:
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT * FROM users"))  # ⚠️ 要用 text() 包起來
#         for row in result:
#             print(row)
#         print("✅ 連線成功")
# except Exception as e:
#     print("❌ 錯誤：", e)



import sys
import json

from fastmcp import FastMCPClient

client = FastMCPClient("unieai-mcp-mysql", transport="stdio")

result = client.invoke({
    "tool": "add_user",
    "args": {
        "name": "Evan",
        "email": "evan@example.com"
    }
})

print(result)

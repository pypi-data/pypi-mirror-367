from fastmcp import FastMCP
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 初始化 SQLAlchemy
Base = declarative_base()

class MeetingBooking(Base):
    __tablename__ = 'meeting_booking'
    id = Column(Integer, primary_key=True, autoincrement=True)
    purpose = Column(String(255), nullable=False)
    room_name = Column(String(100), nullable=False)
    reserved_by = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

DB_URL = "mysql+pymysql://root:unieai2025@192.168.240.1:18018/testdb?charset=utf8mb4"
engine = create_engine(DB_URL, echo=True, future=True)
Session = sessionmaker(bind=engine)
session = Session()

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM meeting_booking"))
        for row in result:
            print(row)
        print("連線成功!!")
except Exception as e:
    print("錯誤：", e)

# 建立資料表（如果尚未建立）
Base.metadata.create_all(engine)

def main():
    mcp = FastMCP("unieai-mcp-mysql-server")

    @mcp.tool()
    def add_booking(purpose: str,room_name: str, reserved_by: str, start_time: str, end_time: str) -> str:
        """新增一筆會議室預約，時間格式為 YYYY-MM-DD HH:MM:SS"""
        try:
            start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            new_booking = MeetingBooking(
                purpose=purpose,
                room_name=room_name,
                reserved_by=reserved_by,
                start_time=start,
                end_time=end
            )
            session.add(new_booking)
            session.commit()
            return f"預約成功，ID：{new_booking.id}"
        except Exception as e:
            return f"新增失敗：{str(e)}"

    @mcp.tool()
    def update_booking(booking_id: int, purpose: str = None, room_name: str = None, reserved_by: str = None,
                       start_time: str = None, end_time: str = None) -> str:
        """更新預約資訊"""
        booking = session.query(MeetingBooking).get(booking_id)
        if not booking:
            return "查無此預約"

        if purpose:
            booking.purpose = purpose
        if room_name:
            booking.room_name = room_name
        if reserved_by:
            booking.reserved_by = reserved_by
        if start_time:
            booking.start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        if end_time:
            booking.end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        session.commit()
        return f"預約 ID {booking_id} 已更新"

    @mcp.tool()
    def delete_booking(booking_id: int) -> str:
        """刪除預約"""
        booking = session.query(MeetingBooking).get(booking_id)
        if not booking:
            return "查無此預約"
        session.delete(booking)
        session.commit()
        return f"預約 ID {booking_id} 已刪除"

    @mcp.tool()
    def get_booking(booking_id: int) -> dict:
        """查詢單筆預約"""
        booking = session.query(MeetingBooking).get(booking_id)
        if not booking:
            return {"error": "查無此預約"}
        return {
            "id": booking.id,
            "purpose": booking.purpose,
            "room_name": booking.room_name,
            "reserved_by": booking.reserved_by,
            "start_time": str(booking.start_time),
            "end_time": str(booking.end_time),
            "created_at": str(booking.created_at)
        }

    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

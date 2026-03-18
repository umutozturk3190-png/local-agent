import sqlite3
import json
from typing import List, Dict, Any

class MemoryDB:
    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                tool_calls TEXT,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        
    def add_message(self, session_id: str, message: Dict[str, Any]):
        role = message.get("role", "")
        content = message.get("content", "")
        def custom_serializer(obj):
            if hasattr(obj, 'model_dump'):
                return obj.model_dump()
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)

        tool_calls_raw = message.get("tool_calls")
        tool_calls = json.dumps(tool_calls_raw, default=custom_serializer) if tool_calls_raw else None
        name = message.get("name", None)
        
        self.conn.execute(
            "INSERT INTO messages (session_id, role, content, tool_calls, name) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, tool_calls, name)
        )
        self.conn.commit()
        
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.execute(
            "SELECT role, content, tool_calls, name FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        messages = []
        for row in cursor.fetchall():
            msg = {"role": row[0]}
            if row[1]:  # content can be an empty string depending on the tool call
                msg["content"] = row[1]
            if row[2]:  # tool_calls
                msg["tool_calls"] = json.loads(row[2])
            if row[3]:  # name for tool response
                msg["name"] = row[3]
            messages.append(msg)
        return messages

    def save_messages(self, session_id: str, new_messages: List[Dict[str, Any]]):
        """Helper to save a batch of messages to the DB."""
        for msg in new_messages:
            self.add_message(session_id, msg)

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class TradeMemory:
    def __init__(self, db_path: str = "data/memory.json"):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """Ensure the memory database exists."""
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"lessons": [], "archived_trades": []}, f, indent=4)

    def _load_db(self) -> Dict:
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
            return {"lessons": [], "archived_trades": []}

    def _save_db(self, data: Dict):
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=4)

    def add_lesson(self, lesson: str, context: str, outcome: str):
        """
        Add a learned lesson to memory.
        
        Args:
            lesson: The insight learned (e.g., "Avoid trading when volume is < 10M")
            context: Market context (e.g., "Low Volatility, Bearish Trend")
            outcome: What triggered this lesson (e.g., "Loss -0.3%")
        """
        db = self._load_db()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "lesson": lesson,
            "context": context,
            "outcome": outcome
        }
        db["lessons"].append(entry)
        # Keep only last 100 lessons to keep it fast/relevant
        if len(db["lessons"]) > 100:
            db["lessons"] = db["lessons"][-100:]
            
        self._save_db(db)
        print(f"🧠 Memory stored: {lesson}")

    def get_relevant_lessons(self, current_context: str = "") -> List[str]:
        """
        Retrieve lessons. For this MVP, we return the most recent 5 lessons.
        In a full vector version, we would semantically search against 'current_context'.
        """
        db = self._load_db()
        # Return last 5 lessons, reversed
        return [l["lesson"] for l in reversed(db["lessons"][-5:])]

    def save_trade_result(self, trade_data: Dict, analysis: str):
        """Archive a trade with AI analysis for future reference."""
        db = self._load_db()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "trade": trade_data,
            "ai_analysis": analysis
        }
        db["archived_trades"].append(entry)
        self._save_db(db)

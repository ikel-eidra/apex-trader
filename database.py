"""
APEX TRADER - Database Module
Handles SQLite operations for trade logging and performance tracking
Engineer: Mane 🔥💙
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import config

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity REAL NOT NULL,
                profit_percent REAL,
                profit_usd REAL,
                status TEXT NOT NULL,
                duration_seconds INTEGER,
                exit_reason TEXT,
                score REAL,
                volatility_score REAL,
                volume_score REAL,
                momentum_score REAL,
                technical_score REAL,
                risk_score REAL,
                notes TEXT
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_profit_usd REAL DEFAULT 0,
                total_profit_percent REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                best_trade_percent REAL DEFAULT 0,
                worst_trade_percent REAL DEFAULT 0,
                avg_trade_duration INTEGER DEFAULT 0
            )
        """)
        
        # System state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_trade_entry(self, symbol: str, entry_price: float, quantity: float, 
                       score: float, scores_breakdown: Dict) -> int:
        """Log a new trade entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trades (
                timestamp, symbol, side, entry_price, quantity, status,
                score, volatility_score, volume_score, momentum_score,
                technical_score, risk_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            symbol,
            'BUY',
            entry_price,
            quantity,
            'OPEN',
            score,
            scores_breakdown.get('volatility', 0),
            scores_breakdown.get('volume', 0),
            scores_breakdown.get('momentum', 0),
            scores_breakdown.get('technical', 0),
            scores_breakdown.get('risk', 0)
        ))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trade_id
    
    def log_trade_exit(self, trade_id: int, exit_price: float, 
                      exit_reason: str, notes: str = None):
        """Log trade exit and calculate profit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get trade entry data
        cursor.execute("""
            SELECT entry_price, quantity, timestamp
            FROM trades WHERE id = ?
        """, (trade_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return
        
        entry_price, quantity, entry_time = row
        
        # Calculate profit
        profit_percent = ((exit_price - entry_price) / entry_price) * 100
        profit_usd = (exit_price - entry_price) * quantity
        
        # Calculate duration
        entry_dt = datetime.fromisoformat(entry_time)
        exit_dt = datetime.now()
        duration = int((exit_dt - entry_dt).total_seconds())
        
        # Update trade
        cursor.execute("""
            UPDATE trades SET
                exit_price = ?,
                profit_percent = ?,
                profit_usd = ?,
                status = ?,
                duration_seconds = ?,
                exit_reason = ?,
                notes = ?
            WHERE id = ?
        """, (
            exit_price,
            profit_percent,
            profit_usd,
            'CLOSED',
            duration,
            exit_reason,
            notes,
            trade_id
        ))
        
        conn.commit()
        conn.close()
        
        # Update daily performance
        self.update_daily_performance()
    
    def update_daily_performance(self):
        """Update daily performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        
        # Get today's trades
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN profit_percent > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN profit_percent < 0 THEN 1 ELSE 0 END) as losses,
                SUM(profit_usd) as total_profit_usd,
                SUM(profit_percent) as total_profit_percent,
                MAX(profit_percent) as best,
                MIN(profit_percent) as worst,
                AVG(duration_seconds) as avg_duration
            FROM trades
            WHERE DATE(timestamp) = ? AND status = 'CLOSED'
        """, (today,))
        
        row = cursor.fetchone()
        if row and row[0] > 0:
            total, wins, losses, profit_usd, profit_pct, best, worst, avg_dur = row
            win_rate = (wins / total * 100) if total > 0 else 0
            
            cursor.execute("""
                INSERT OR REPLACE INTO performance (
                    date, total_trades, winning_trades, losing_trades,
                    total_profit_usd, total_profit_percent, win_rate,
                    best_trade_percent, worst_trade_percent, avg_trade_duration
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                today, total, wins or 0, losses or 0,
                profit_usd or 0, profit_pct or 0, win_rate,
                best or 0, worst or 0, int(avg_dur or 0)
            ))
        
        conn.commit()
        conn.close()
    
    def get_open_trade(self) -> Optional[Dict]:
        """Get currently open trade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, symbol, entry_price, quantity, timestamp, score
            FROM trades
            WHERE status = 'OPEN'
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'symbol': row[1],
                'entry_price': row[2],
                'quantity': row[3],
                'timestamp': row[4],
                'score': row[5]
            }
        return None
    
    def get_recent_trades(self, limit: int = 20) -> List[Dict]:
        """Get recent trades"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, timestamp, symbol, entry_price, exit_price,
                profit_percent, profit_usd, status, duration_seconds,
                exit_reason, score
            FROM trades
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        trades = []
        for row in cursor.fetchall():
            trades.append({
                'id': row[0],
                'timestamp': row[1],
                'symbol': row[2],
                'entry_price': row[3],
                'exit_price': row[4],
                'profit_percent': row[5],
                'profit_usd': row[6],
                'status': row[7],
                'duration_seconds': row[8],
                'exit_reason': row[9],
                'score': row[10]
            })
        
        conn.close()
        return trades
    
    def get_daily_stats(self) -> Dict:
        """Get today's statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        
        cursor.execute("""
            SELECT 
                total_trades, winning_trades, losing_trades,
                total_profit_usd, total_profit_percent, win_rate,
                best_trade_percent, worst_trade_percent
            FROM performance
            WHERE date = ?
        """, (today,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'total_trades': row[0],
                'winning_trades': row[1],
                'losing_trades': row[2],
                'total_profit_usd': row[3],
                'total_profit_percent': row[4],
                'win_rate': row[5],
                'best_trade': row[6],
                'worst_trade': row[7]
            }
        
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit_usd': 0,
            'total_profit_percent': 0,
            'win_rate': 0,
            'best_trade': 0,
            'worst_trade': 0
        }
    
    def get_all_time_stats(self) -> Dict:
        """Get all-time statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN profit_percent > 0 THEN 1 ELSE 0 END) as wins,
                SUM(profit_usd) as total_profit_usd,
                AVG(profit_percent) as avg_profit_percent,
                MAX(profit_percent) as best,
                MIN(profit_percent) as worst
            FROM trades
            WHERE status = 'CLOSED'
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            total, wins, profit_usd, avg_pct, best, worst = row
            win_rate = (wins / total * 100) if total > 0 else 0
            
            return {
                'total_trades': total,
                'winning_trades': wins,
                'total_profit_usd': profit_usd or 0,
                'avg_profit_percent': avg_pct or 0,
                'win_rate': win_rate,
                'best_trade': best or 0,
                'worst_trade': worst or 0
            }
        
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit_usd': 0,
            'avg_profit_percent': 0,
            'win_rate': 0,
            'best_trade': 0,
            'worst_trade': 0
        }
    
    def set_state(self, key: str, value: any):
        """Set system state value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO system_state (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, json.dumps(value), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_state(self, key: str, default=None):
        """Get system state value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM system_state WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return default

if __name__ == "__main__":
    # Test database
    db = Database()
    print("✅ Database initialized successfully!")
    print(f"📁 Database location: {db.db_path}")


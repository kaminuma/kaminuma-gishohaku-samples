"""
データベース管理
SQLiteインメモリDBでのシンプルなデータ永続化
"""

import sqlite3
import logging
from typing import List, Optional
from datetime import datetime

from models.activity import Activity
from models.daily_mood import DailyMood

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    SQLiteインメモリデータベースの管理クラス
    
    【シンプル設計の理由】
    - 教育目的のサンプルアプリのため
    - セットアップが不要
    - データは一時的（アプリ終了時に消去）
    """
    
    def __init__(self):
        """データベース接続の初期化"""
        # インメモリDBを使用（:memory:）
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 辞書形式での結果取得
        self._create_tables()
        logger.info("インメモリデータベースを初期化しました")
    
    def _create_tables(self):
        """テーブルの作成"""
        cursor = self.conn.cursor()
        
        # activitiesテーブル（既存API仕様準拠）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,    -- ユーザーID（サンプル用は固定）
                date TEXT NOT NULL,           -- 日付 (YYYY-MM-DD形式)
                start_time TEXT NOT NULL,     -- 開始時刻 (HH:MM形式)
                end_time TEXT NOT NULL,       -- 終了時刻 (HH:MM形式)
                title TEXT NOT NULL,          -- 活動タイトル
                contents TEXT,                -- 活動内容
                category TEXT,                -- カテゴリ
                category_sub TEXT,            -- サブカテゴリ
                created_at TEXT NOT NULL,     -- 作成日時
                updated_at TEXT NOT NULL      -- 更新日時
            )
        ''')
        
        # daily_moodテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_moods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,    -- 日付 (YYYY-MM-DD形式) 一意制約
                mood INTEGER NOT NULL,        -- ムード (1-5の5段階評価)
                note TEXT,                    -- ムードに関するメモ
                created_at TEXT NOT NULL,     -- 作成日時
                updated_at TEXT NOT NULL      -- 更新日時
            )
        ''')
        
        # インデックスの作成（検索パフォーマンス向上）
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_activities_date 
            ON activities(date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_activities_user_date 
            ON activities(user_id, date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_activities_category
            ON activities(category)
        ''')
        
        self.conn.commit()
        logger.info("データベーステーブルを作成しました (activities, daily_moods)")
    
    def insert_activity(self, activity: Activity) -> int:
        """
        活動データを挿入
        
        Args:
            activity: 挿入する活動データ
            
        Returns:
            挿入されたレコードのID
        """
        cursor = self.conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO activities (
                user_id, date, start_time, end_time, title, contents,
                category, category_sub, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            activity.user_id or 1,  # サンプル用デフォルト
            activity.date.isoformat() if activity.date else None,
            activity.start_time.strftime('%H:%M') if activity.start_time else None,
            activity.end_time.strftime('%H:%M') if activity.end_time else None,
            activity.title,
            activity.contents,
            activity.category,
            activity.category_sub,
            now,
            now
        ))
        
        self.conn.commit()
        activity_id = cursor.lastrowid
        
        logger.debug(f"活動データを挿入しました (ID: {activity_id})")
        return activity_id
    
    def insert_activities_batch(self, activities: List[Activity]) -> int:
        """
        複数の活動データを一括挿入
        
        Args:
            activities: 挿入する活動データのリスト
            
        Returns:
            挿入されたレコード数
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        # バッチ挿入用のデータを準備
        batch_data = []
        for activity in activities:
            batch_data.append((
                activity.user_id or 1,  # サンプル用デフォルト
                activity.date.isoformat() if activity.date else None,
                activity.start_time.strftime('%H:%M') if activity.start_time else None,
                activity.end_time.strftime('%H:%M') if activity.end_time else None,
                activity.title,
                activity.contents,
                activity.category,
                activity.category_sub,
                now,
                now
            ))
        
        # 一括挿入実行
        cursor.executemany('''
            INSERT INTO activities (
                user_id, date, start_time, end_time, title, contents,
                category, category_sub, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', batch_data)
        
        self.conn.commit()
        inserted_count = cursor.rowcount
        
        logger.info(f"活動データを一括挿入しました ({inserted_count}件)")
        return inserted_count
    
    def get_all_activities(self, order_by: str = 'date DESC, start_time DESC') -> List[Activity]:
        """
        全ての活動データを取得
        
        Args:
            order_by: ソート順（デフォルトは日付・時間の降順）
            
        Returns:
            活動データのリスト
        """
        cursor = self.conn.cursor()
        
        query = f'SELECT * FROM activities ORDER BY {order_by}'
        cursor.execute(query)
        
        activities = []
        for row in cursor.fetchall():
            activity = self._row_to_activity(row)
            activities.append(activity)
        
        logger.debug(f"活動データを取得しました ({len(activities)}件)")
        return activities
    
    def get_activities_by_date_range(self, 
                                   start_date: str, 
                                   end_date: str) -> List[Activity]:
        """
        日付範囲で活動データを取得
        
        Args:
            start_date: 開始日（YYYY-MM-DD形式）
            end_date: 終了日（YYYY-MM-DD形式）
            
        Returns:
            指定期間の活動データリスト
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM activities 
            WHERE date BETWEEN ? AND ?
            ORDER BY date, start_time
        ''', (start_date, end_date))
        
        activities = []
        for row in cursor.fetchall():
            activity = self._row_to_activity(row)
            activities.append(activity)
        
        logger.debug(f"日付範囲の活動データを取得しました "
                    f"({start_date}〜{end_date}: {len(activities)}件)")
        return activities
    
    def get_activity_by_id(self, activity_id: int) -> Optional[Activity]:
        """
        IDで特定の活動データを取得
        
        Args:
            activity_id: 活動ID
            
        Returns:
            活動データ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT * FROM activities WHERE id = ?', (activity_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_activity(row)
        else:
            return None
    
    def update_activity(self, activity_id: int, activity: Activity) -> bool:
        """
        活動データを更新
        
        Args:
            activity_id: 更新対象の活動ID
            activity: 更新データ
            
        Returns:
            更新成功の可否
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE activities SET
                user_id = ?, date = ?, start_time = ?, end_time = ?,
                title = ?, contents = ?, category = ?, category_sub = ?,
                updated_at = ?
            WHERE id = ?
        ''', (
            activity.user_id or 1,
            activity.date.isoformat() if activity.date else None,
            activity.start_time.strftime('%H:%M') if activity.start_time else None,
            activity.end_time.strftime('%H:%M') if activity.end_time else None,
            activity.title,
            activity.contents,
            activity.category,
            activity.category_sub,
            datetime.now().isoformat(),
            activity_id
        ))
        
        self.conn.commit()
        success = cursor.rowcount > 0
        
        if success:
            logger.debug(f"活動データを更新しました (ID: {activity_id})")
        else:
            logger.warning(f"更新対象の活動が見つかりませんでした (ID: {activity_id})")
        
        return success
    
    def delete_activity(self, activity_id: int) -> bool:
        """
        活動データを削除
        
        Args:
            activity_id: 削除対象の活動ID
            
        Returns:
            削除成功の可否
        """
        cursor = self.conn.cursor()
        
        cursor.execute('DELETE FROM activities WHERE id = ?', (activity_id,))
        self.conn.commit()
        
        success = cursor.rowcount > 0
        
        if success:
            logger.debug(f"活動データを削除しました (ID: {activity_id})")
        else:
            logger.warning(f"削除対象の活動が見つかりませんでした (ID: {activity_id})")
        
        return success
    
    def get_statistics(self) -> dict:
        """
        データベースの統計情報を取得
        
        Returns:
            統計情報の辞書
        """
        cursor = self.conn.cursor()
        
        # 総活動数
        cursor.execute('SELECT COUNT(*) as total FROM activities')
        total_count = cursor.fetchone()['total']
        
        # 日付範囲
        cursor.execute('''
            SELECT MIN(date) as min_date, MAX(date) as max_date 
            FROM activities
        ''')
        date_range = cursor.fetchone()
        
        # ムード統計（daily_moodテーブルから取得）
        cursor.execute('''
            SELECT AVG(mood) as avg_mood, MIN(mood) as min_mood, MAX(mood) as max_mood
            FROM daily_moods
        ''')
        mood_stats = cursor.fetchone()
        
        return {
            'total_activities': total_count,
            'date_range': {
                'start': date_range['min_date'],
                'end': date_range['max_date']
            },
            'mood_statistics': {
                'average': round(mood_stats['avg_mood'], 2) if mood_stats['avg_mood'] else 0,
                'minimum': mood_stats['min_mood'],
                'maximum': mood_stats['max_mood']
            }
        }
    
    def _row_to_activity(self, row: sqlite3.Row) -> Activity:
        """
        データベース行をActivityオブジェクトに変換
        
        Args:
            row: SQLiteの行データ
            
        Returns:
            Activityオブジェクト
        """
        return Activity(
            id=row['id'],
            user_id=row['user_id'],
            date=datetime.fromisoformat(row['date']).date() if row['date'] else None,
            start_time=datetime.strptime(row['start_time'], '%H:%M').time() if row['start_time'] else None,
            end_time=datetime.strptime(row['end_time'], '%H:%M').time() if row['end_time'] else None,
            title=row['title'],
            contents=row['contents'],
            category=row['category'],
            category_sub=row['category_sub'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
    
    # ===== DailyMood CRUD operations =====
    
    def insert_daily_mood(self, daily_mood: DailyMood) -> int:
        """
        日次ムードデータを挿入（同じ日付の場合は更新）
        
        Args:
            daily_mood: 挿入する日次ムードデータ
            
        Returns:
            挿入されたレコードのID
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_moods (
                date, mood, note, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            daily_mood.date.isoformat() if daily_mood.date else None,
            daily_mood.mood,
            daily_mood.note,
            now,
            now
        ))
        
        self.conn.commit()
        mood_id = cursor.lastrowid
        
        logger.debug(f"日次ムードデータを挿入/更新しました (ID: {mood_id})")
        return mood_id
    
    def insert_daily_moods_batch(self, daily_moods: List[DailyMood]) -> int:
        """
        複数の日次ムードデータを一括挿入
        
        Args:
            daily_moods: 挿入する日次ムードデータのリスト
            
        Returns:
            挿入されたレコード数
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        # バッチ挿入用のデータを準備
        batch_data = []
        for daily_mood in daily_moods:
            batch_data.append((
                daily_mood.date.isoformat() if daily_mood.date else None,
                daily_mood.mood,
                daily_mood.note,
                now,
                now
            ))
        
        # 一括挿入実行
        cursor.executemany('''
            INSERT OR REPLACE INTO daily_moods (
                date, mood, note, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
        ''', batch_data)
        
        self.conn.commit()
        inserted_count = cursor.rowcount
        
        logger.info(f"日次ムードデータを一括挿入しました ({inserted_count}件)")
        return inserted_count
    
    def get_daily_moods(self, start_date: str = None, end_date: str = None) -> List[DailyMood]:
        """
        日次ムードデータを取得
        
        Args:
            start_date: 開始日（YYYY-MM-DD形式）
            end_date: 終了日（YYYY-MM-DD形式）
            
        Returns:
            日次ムードデータのリスト
        """
        cursor = self.conn.cursor()
        
        # 基本クエリ
        query = 'SELECT * FROM daily_moods'
        params = []
        
        # 日付範囲フィルタを追加
        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append('date >= ?')
                params.append(start_date)
            if end_date:
                conditions.append('date <= ?')
                params.append(end_date)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY date ASC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        daily_moods = [self._row_to_daily_mood(row) for row in rows]
        
        logger.debug(f"日次ムードデータを取得しました "
                    f"({start_date}〜{end_date}: {len(daily_moods)}件)")
        return daily_moods
    
    def get_daily_mood_by_date(self, date_str: str) -> Optional[DailyMood]:
        """
        特定の日付の日次ムードデータを取得
        
        Args:
            date_str: 日付（YYYY-MM-DD形式）
            
        Returns:
            日次ムードデータ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT * FROM daily_moods WHERE date = ?', (date_str,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_daily_mood(row)
        else:
            return None
    
    def _row_to_daily_mood(self, row: sqlite3.Row) -> DailyMood:
        """
        データベース行をDailyMoodオブジェクトに変換
        
        Args:
            row: SQLiteの行データ
            
        Returns:
            DailyMoodオブジェクト
        """
        return DailyMood(
            id=row['id'],
            date=datetime.fromisoformat(row['date']).date() if row['date'] else None,
            mood=row['mood'],
            note=row['note'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()
            logger.info("データベース接続を閉じました")
    
    def __del__(self):
        """デストラクタでの自動クリーンアップ"""
        self.close()
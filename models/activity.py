"""
活動データモデル（既存API仕様準拠）
ユーザーの日常活動を表現するデータ構造
Spring Boot版のActivityGetEntityに対応
"""

from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Optional

@dataclass
class Activity:
    """
    活動データを表すモデルクラス（既存API仕様準拠）
    
    日常の活動内容、開始〜終了時間、カテゴリを管理
    Spring Boot版のActivityGetEntityに対応
    """
    id: Optional[int] = None
    user_id: Optional[int] = None         # ユーザーID
    date: Optional[date] = None           # 活動日付
    start_time: Optional[time] = None     # 開始時刻
    end_time: Optional[time] = None       # 終了時刻
    title: Optional[str] = None           # 活動タイトル
    contents: Optional[str] = None        # 活動内容
    category: Optional[str] = None        # カテゴリ
    category_sub: Optional[str] = None    # サブカテゴリ
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def validate(self) -> None:
        """
        活動データの妥当性検証
        """
        if self.title and len(self.title.strip()) == 0:
            raise ValueError("活動タイトルは必須です")
        
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("開始時刻は終了時刻より前である必要があります")
    
    def to_dict(self) -> dict:
        """辞書形式に変換（JSON化用）"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'title': self.title,
            'contents': self.contents,
            'category': self.category,
            'category_sub': self.category_sub,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Activity':
        """辞書からActivityオブジェクトを生成"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            date=datetime.fromisoformat(data['date']).date() if data.get('date') else None,
            start_time=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
            end_time=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            title=data.get('title'),
            contents=data.get('contents'),
            category=data.get('category'),
            category_sub=data.get('category_sub'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def get_duration_minutes(self) -> Optional[int]:
        """活動時間の長さを分単位で取得"""
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(datetime.today(), self.start_time)
            end_datetime = datetime.combine(datetime.today(), self.end_time)
            duration = end_datetime - start_datetime
            return int(duration.total_seconds() / 60)
        return None
    
    def get_time_range_str(self) -> str:
        """時間範囲を文字列で取得"""
        if self.start_time and self.end_time:
            return f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
        elif self.start_time:
            return f"{self.start_time.strftime('%H:%M')}-"
        else:
            return "時間不明"
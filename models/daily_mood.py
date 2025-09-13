"""
日次ムードデータモデル
日単位でのユーザーのムード状態を表現するデータ構造
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

@dataclass
class DailyMood:
    """
    日次ムードデータを表すモデルクラス
    
    1日に1つのムード値を管理
    活動データとは分離して管理される
    """
    id: Optional[int] = None
    date: Optional[date] = None           # ムード記録日付
    mood: Optional[int] = None            # ムード値（1-5の5段階）
    note: Optional[str] = None            # ムードに関するメモ（オプション）
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def validate(self) -> None:
        """
        ムードデータの妥当性検証
        """
        if self.mood is not None and (self.mood < 1 or self.mood > 5):
            raise ValueError("気分値は1-5の範囲で入力してください")
        
        if self.date is None:
            raise ValueError("日付は必須です")
    
    def to_dict(self) -> dict:
        """辞書形式に変換（JSON化用）"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'mood': self.mood,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DailyMood':
        """辞書からDailyMoodオブジェクトを生成"""
        return cls(
            id=data.get('id'),
            date=datetime.fromisoformat(data['date']).date() if data.get('date') else None,
            mood=data.get('mood'),
            note=data.get('note'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def get_mood_emoji(self) -> str:
        """ムード値に対応する絵文字を返す"""
        if self.mood is None:
            return "❓"
        
        mood_emojis = {
            1: "😫",  # とても悪い
            2: "😞",  # 悪い
            3: "😐",  # 普通
            4: "😊",  # 良い
            5: "😄"   # とても良い
        }
        
        return mood_emojis.get(self.mood, "❓")
    
    def get_mood_description(self) -> str:
        """ムード値の説明を返す"""
        if self.mood is None:
            return "未記録"
        
        descriptions = {
            1: "とても悪い",
            2: "悪い", 
            3: "普通",
            4: "良い",
            5: "とても良い"
        }
        
        return descriptions.get(self.mood, "不明")
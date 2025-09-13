"""
分析関連のモデル
Gemini API分析のリクエストと結果を管理
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

class AnalysisFocus(Enum):
    """
    分析の焦点
    どの観点から活動データを分析するかを指定
    """
    MOOD_FOCUSED = "mood"          # 気分中心の分析
    ACTIVITY_FOCUSED = "activities" # 活動中心の分析  
    BALANCED = "balance"           # バランス重視の分析
    WELLNESS_FOCUSED = "wellness"  # ウェルネス全般の分析

class DetailLevel(Enum):
    """
    詳細レベル
    分析結果の詳細度を指定
    """
    CONCISE = "brief"     # 簡潔（要点のみ）
    STANDARD = "standard" # 標準（適度な詳細）
    DETAILED = "detailed" # 詳細（包括的分析）

class ResponseStyle(Enum):
    """
    応答スタイル
    分析結果の文体・口調を指定
    """
    FRIENDLY = "friendly"         # 親しみやすい
    PROFESSIONAL = "professional" # 専門的
    ENCOURAGING = "encouraging"   # 励まし重視
    CASUAL = "casual"            # カジュアル

@dataclass
class AnalysisRequest:
    """
    分析リクエストモデル
    Gemini API分析のパラメータを管理
    """
    analysis_focus: AnalysisFocus
    detail_level: DetailLevel
    response_style: ResponseStyle
    date_from: Optional[str] = None  # YYYY-MM-DD形式
    date_to: Optional[str] = None    # YYYY-MM-DD形式
    
    def validate(self) -> None:
        """リクエストデータの妥当性検証"""
        if not isinstance(self.analysis_focus, AnalysisFocus):
            raise ValueError(f"Invalid analysis_focus: {self.analysis_focus}")
        if not isinstance(self.detail_level, DetailLevel):
            raise ValueError(f"Invalid detail_level: {self.detail_level}")
        if not isinstance(self.response_style, ResponseStyle):
            raise ValueError(f"Invalid response_style: {self.response_style}")
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'analysis_focus': self.analysis_focus.value,
            'detail_level': self.detail_level.value,
            'response_style': self.response_style.value,
            'date_from': self.date_from,
            'date_to': self.date_to
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisRequest':
        """辞書からAnalysisRequestオブジェクトを生成"""
        return cls(
            analysis_focus=AnalysisFocus(data['focus']),
            detail_level=DetailLevel(data['detail_level']),
            response_style=ResponseStyle(data['response_style']),
            date_from=data.get('date_from'),
            date_to=data.get('date_to')
        )

@dataclass
class AnalysisResult:
    """
    分析結果モデル
    Gemini APIからの分析結果とメタデータを保持
    """
    analysis_text: str                    # 分析結果のテキスト
    parameters: AnalysisRequest          # 使用されたパラメータ
    activity_count: int                  # 分析対象活動数
    mood_count: int                      # 分析対象ムード数
    processing_time_ms: Optional[int] = None  # 処理時間（ミリ秒）
    token_count: Optional[int] = None         # 使用トークン数
    prompt_preview: Optional[str] = None      # プロンプトプレビュー
    created_at: Optional[datetime] = None     # 分析実行日時
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換（JSON化用）"""
        return {
            'analysis_text': self.analysis_text,
            'parameters': self.parameters.to_dict(),
            'activity_count': self.activity_count,
            'mood_count': self.mood_count,
            'processing_time_ms': self.processing_time_ms,
            'token_count': self.token_count,
            'prompt_preview': self.prompt_preview,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
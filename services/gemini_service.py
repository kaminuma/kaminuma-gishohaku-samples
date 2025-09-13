"""
Gemini API統合サービス
包括的なエラーハンドリングとリトライ機能を提供
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from models.activity import Activity
from models.daily_mood import DailyMood
from models.analysis import AnalysisRequest, AnalysisResult
from services.prompt_builder import GeminiPromptBuilder

# ログ設定
logger = logging.getLogger(__name__)

class GeminiAnalysisService:
    """
    Gemini APIを使用した分析サービス
    
    【実装のポイント】
    - 包括的なエラーハンドリング
    - レート制限とリトライ機能
    - 安全性設定の適用
    - 詳細なログ出力
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Gemini APIサービスの初期化
        
        Args:
            api_key: Gemini APIキー（Noneの場合は環境変数から取得）
        """
        # APIキーの設定
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini APIキーが設定されていません。環境変数GEMINI_API_KEYを設定してください。")
        
        # Gemini APIの設定
        genai.configure(api_key=self.api_key)
        
        # モデルの初期化
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        
        # プロンプトビルダーの初期化
        self.prompt_builder = GeminiPromptBuilder()
        
        # 生成設定
        self.generation_config = genai.GenerationConfig(
            temperature=0.7,        # 創造性とバランス
            max_output_tokens=1000, # 最大出力トークン数
            top_p=0.9,             # Top-pサンプリング
            top_k=40               # Top-kサンプリング
        )
        
        logger.info("Gemini APIサービスが初期化されました")
    
    def analyze_activities(self, 
                         activities: List[Activity],
                         daily_moods: List[DailyMood],
                         request: AnalysisRequest) -> AnalysisResult:
        """
        活動データと日次ムードデータを分析してインサイトを生成
        
        【エラーハンドリング】
        包括的なエラー処理を実装：
        - API認証エラー
        - レート制限エラー  
        - ネットワークエラー
        - レスポンス解析エラー
        
        Args:
            activities: 分析対象の活動データ
            daily_moods: 分析対象の日次ムードデータ
            request: 分析リクエストパラメータ
            
        Returns:
            分析結果
            
        Raises:
            ValueError: リクエストデータが不正
            RuntimeError: API呼び出しエラー
        """
        
        start_time = time.time()
        
        try:
            # 1. リクエストの妥当性検証
            self._validate_request(activities, daily_moods, request)
            
            # 2. プロンプトの生成
            prompt = self.prompt_builder.build_prompt(activities, daily_moods, request)
            logger.info(f"プロンプトを生成しました（長さ: {len(prompt)}文字）")
            
            # 3. Gemini APIの呼び出し
            logger.info("Gemini API分析を開始します...")
            response = self._call_gemini_api(prompt)
            
            # 4. レスポンスの処理
            analysis_text = self._extract_analysis_text(response)
            
            # 5. メタデータの収集
            processing_time = int((time.time() - start_time) * 1000)
            token_count = self._extract_token_count(response)
            
            # 6. 結果の構築
            result = AnalysisResult(
                analysis_text=analysis_text,
                parameters=request,
                activity_count=len(activities),
                mood_count=len(daily_moods),
                processing_time_ms=processing_time,
                token_count=token_count,
                prompt_preview=prompt[:200] + "..." if len(prompt) > 200 else prompt
            )
            
            logger.info(f"分析が完了しました（処理時間: {processing_time}ms, トークン数: {token_count}）")
            return result
            
        except Exception as e:
            # エラーログを詳細に記録
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f"分析中にエラーが発生しました（処理時間: {processing_time}ms）: {str(e)}")
            raise self._handle_error(e)
    
    def _validate_request(self, activities: List[Activity], daily_moods: List[DailyMood], request: AnalysisRequest) -> None:
        """
        リクエストデータの妥当性検証
        """
        if not activities:
            raise ValueError("分析対象の活動データがありません")
        
        if not daily_moods:
            raise ValueError("分析対象の日次ムードデータがありません")
        
        if len(activities) > 1000:  # 過度に大きなデータセットを防ぐ
            raise ValueError("分析対象の活動データが多すぎます（最大1000件）")
        
        # 各活動データの検証
        for activity in activities:
            try:
                activity.validate()
            except ValueError as e:
                raise ValueError(f"活動データが不正です: {str(e)}")
        
        # 各日次ムードデータの検証
        for daily_mood in daily_moods:
            try:
                daily_mood.validate()
            except ValueError as e:
                raise ValueError(f"日次ムードデータが不正です: {str(e)}")
        
        # リクエストパラメータの検証
        try:
            request.validate()
        except ValueError as e:
            raise ValueError(f"分析リクエストが不正です: {str(e)}")
    
    def _call_gemini_api(self, prompt: str, max_retries: int = 3) -> Any:
        """
        Gemini APIを呼び出し（リトライ機能付き）
        
        【リトライロジック】
        レート制限対応とネットワークエラー対応
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # API呼び出し実行
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                
                # レスポンスの基本検証
                if not response.text:
                    raise RuntimeError("Gemini APIから空のレスポンスが返されました")
                
                return response
                
            except Exception as e:
                last_exception = e
                error_message = str(e).lower()
                
                # リトライするエラーかどうかを判定
                if attempt < max_retries - 1:
                    if any(keyword in error_message for keyword in 
                          ['rate limit', 'quota', 'timeout', 'network', '503', '429']):
                        
                        # 指数バックオフでリトライ
                        wait_time = (2 ** attempt) + 1
                        logger.warning(f"API呼び出しに失敗（試行{attempt + 1}/{max_retries}）、"
                                     f"{wait_time}秒後にリトライします: {str(e)}")
                        time.sleep(wait_time)
                        continue
                
                # リトライしないエラーの場合は即座に例外を発生
                break
        
        # 全てのリトライが失敗した場合
        raise RuntimeError(f"Gemini API呼び出しが失敗しました: {str(last_exception)}")
    
    def _extract_analysis_text(self, response: Any) -> str:
        """
        Gemini APIレスポンスから分析テキストを抽出
        """
        try:
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                # candidates構造を確認
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            return candidate.content.parts[0].text.strip()
                
                raise RuntimeError("レスポンスから分析テキストを抽出できませんでした")
                
        except Exception as e:
            logger.error(f"レスポンス解析エラー: {str(e)}")
            raise RuntimeError(f"レスポンスの解析に失敗しました: {str(e)}")
    
    def _extract_token_count(self, response: Any) -> Optional[int]:
        """
        レスポンスからトークン使用量を抽出
        """
        try:
            # usage_metadataからトークン数を取得
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                if hasattr(usage, 'total_token_count'):
                    return usage.total_token_count
                elif hasattr(usage, 'prompt_token_count') and hasattr(usage, 'candidates_token_count'):
                    return usage.prompt_token_count + usage.candidates_token_count
            
            return None  # トークン数が取得できない場合
            
        except Exception as e:
            logger.warning(f"トークン数の取得に失敗しました: {str(e)}")
            return None
    
    def _handle_error(self, error: Exception) -> RuntimeError:
        """
        エラーを適切な形式に変換
        """
        error_message = str(error).lower()
        
        # 認証エラー
        if any(keyword in error_message for keyword in ['api key', 'unauthorized', '401']):
            return RuntimeError("APIキーが無効です。Gemini APIキーを確認してください。")
        
        # レート制限エラー
        if any(keyword in error_message for keyword in ['rate limit', 'quota', '429']):
            return RuntimeError("API利用制限に達しました。しばらく時間をおいてから再試行してください。")
        
        # ネットワークエラー
        if any(keyword in error_message for keyword in ['network', 'connection', 'timeout']):
            return RuntimeError("ネットワークエラーが発生しました。インターネット接続を確認してください。")
        
        # サーバーエラー
        if any(keyword in error_message for keyword in ['500', '502', '503', 'server error']):
            return RuntimeError("Gemini APIサーバーエラーが発生しました。しばらく時間をおいてから再試行してください。")
        
        # その他のエラー
        return RuntimeError(f"分析中にエラーが発生しました: {str(error)}")
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        API接続状態を確認（デバッグ用）
        """
        try:
            # 簡単なテストリクエストを送信
            test_response = self.model.generate_content(
                "こんにちは",
                generation_config=genai.GenerationConfig(max_output_tokens=10)
            )
            
            return {
                'status': 'healthy',
                'api_key_valid': True,
                'test_response': test_response.text[:50] if test_response.text else None
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'api_key_valid': False,
                'error': str(e)
            }
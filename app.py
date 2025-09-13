"""
Gemini AI振り返り分析サンプルアプリケーション
書籍執筆用のモジュール分割された実装

【アーキテクチャ】
- Models: データモデル定義
- Services: ビジネスロジック 
- Database: データアクセス層
- Routes: APIエンドポイント

【特徴】
- 高度なプロンプトエンジニアリング技術を活用
- 柔軟なパラメータ設定による分析カスタマイズ
- 包括的なエラーハンドリング
"""

import os
import logging
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# 自作モジュールのインポート
from models import AnalysisRequest, AnalysisFocus, DetailLevel, ResponseStyle, DailyMood
from services import GeminiAnalysisService, SampleDataGenerator
from database import DatabaseManager

# 環境変数の読み込み
load_dotenv()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LifeAnalysisApp:
    """
    メインアプリケーションクラス
    依存性注入とサービス管理を担当
    """
    
    def __init__(self):
        """アプリケーションの初期化"""
        # Flaskアプリの作成
        self.app = Flask(__name__)
        
        # サービスの初期化
        self._init_services()
        
        # ルートの登録
        self._register_routes()
        
        # サンプルデータの生成と挿入
        self._initialize_sample_data()
        
        logger.info("アプリケーションの初期化が完了しました")
    
    def _init_services(self):
        """各種サービスの初期化"""
        try:
            # データベース管理
            self.db_manager = DatabaseManager()
            
            # Gemini分析サービス
            self.gemini_service = GeminiAnalysisService()
            
            # サンプルデータ生成サービス
            self.data_generator = SampleDataGenerator()
            
            logger.info("全てのサービスが正常に初期化されました")
            
        except Exception as e:
            logger.error(f"サービス初期化エラー: {str(e)}")
            raise
    
    def _register_routes(self):
        """APIルートの登録"""
        
        @self.app.route('/')
        def index():
            """
            メインページの表示
            """
            return render_template('index.html')
        
        @self.app.route('/api/activities')
        def get_activities():
            """
            活動データ取得API
            生成された活動データを JSON 形式で返却
            """
            try:
                # データベースから全活動を取得
                activities = self.db_manager.get_all_activities()
                
                # レスポンス形式（JSON 標準形式）
                response_data = {
                    'status': 'success',
                    'data': [activity.to_dict() for activity in activities],
                    'count': len(activities)
                }
                
                logger.info(f"活動データを返却しました ({len(activities)}件)")
                return jsonify(response_data)
                
            except Exception as e:
                logger.error(f"活動データ取得エラー: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': '活動データの取得に失敗しました',
                    'code': 'DATA_FETCH_ERROR'
                }), 500
        
        @self.app.route('/api/daily-moods')
        def get_daily_moods():
            """
            日次ムードデータ取得API
            生成された日次ムードデータを JSON 形式で返却
            """
            try:
                # データベースから全日次ムードを取得
                daily_moods = self.db_manager.get_daily_moods()
                
                # レスポンス形式（JSON 標準形式）
                response_data = {
                    'status': 'success',
                    'data': [mood.to_dict() for mood in daily_moods],
                    'count': len(daily_moods)
                }
                
                logger.info(f"日次ムードデータを返却しました ({len(daily_moods)}件)")
                return jsonify(response_data)
                
            except Exception as e:
                logger.error(f"日次ムードデータ取得エラー: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': '日次ムードデータの取得に失敗しました',
                    'code': 'MOOD_FETCH_ERROR'
                }), 500
        
        @self.app.route('/api/analyze', methods=['POST'])
        def analyze():
            """
            Gemini分析実行API
            活動データを分析してインサイトを生成
            
            リクエスト形式:
            {
                "focus": "mood|activities|balance|wellness",
                "detail_level": "brief|standard|detailed", 
                "response_style": "friendly|professional|encouraging|casual"
            }
            """
            try:
                # 1. リクエストパラメータの取得と検証
                request_data = request.get_json()
                if not request_data:
                    return jsonify({
                        'status': 'error',
                        'message': 'リクエストボディが必要です',
                        'code': 'MISSING_REQUEST_BODY'
                    }), 400
                
                # 2. 分析リクエストオブジェクトの作成
                try:
                    analysis_request = AnalysisRequest.from_dict(request_data)
                    analysis_request.validate()
                except ValueError as e:
                    return jsonify({
                        'status': 'error',
                        'message': f'リクエストパラメータが不正です: {str(e)}',
                        'code': 'INVALID_PARAMETERS'
                    }), 400
                
                # 3. 活動データと日次ムードデータの取得
                activities = self.db_manager.get_all_activities()
                daily_moods = self.db_manager.get_daily_moods()
                
                if not activities:
                    return jsonify({
                        'status': 'error',
                        'message': '分析対象の活動データがありません',
                        'code': 'NO_DATA'
                    }), 400
                
                if not daily_moods:
                    return jsonify({
                        'status': 'error',
                        'message': '分析対象のムードデータがありません',
                        'code': 'NO_MOOD_DATA'
                    }), 400
                
                # 4. Gemini分析の実行
                logger.info(f"分析を開始します（パラメータ: {analysis_request.to_dict()}）")
                analysis_result = self.gemini_service.analyze_activities(
                    activities, daily_moods, analysis_request
                )
                
                # 5. レスポンスの構築
                response_data = {
                    'status': 'success',
                    'data': analysis_result.to_dict()
                }
                
                logger.info("分析が正常に完了しました")
                return jsonify(response_data)
                
            except RuntimeError as e:
                # Gemini APIエラー
                logger.error(f"Gemini分析エラー: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'code': 'GEMINI_API_ERROR'
                }), 500
                
            except Exception as e:
                # 予期しないエラー
                logger.error(f"予期しないエラーが発生しました: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': '分析中に内部エラーが発生しました',
                    'code': 'INTERNAL_ERROR'
                }), 500
        
        @self.app.route('/api/status')
        def get_status():
            """
            アプリケーション状態確認API（デバッグ用）
            """
            try:
                # データベース統計
                db_stats = self.db_manager.get_statistics()
                
                # Gemini API状態
                gemini_status = self.gemini_service.get_api_status()
                
                return jsonify({
                    'status': 'success',
                    'data': {
                        'application': 'healthy',
                        'database': db_stats,
                        'gemini_api': gemini_status
                    }
                })
                
            except Exception as e:
                logger.error(f"状態確認エラー: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'状態確認に失敗しました: {str(e)}'
                }), 500
        
        @self.app.route('/api/regenerate-data', methods=['POST'])
        def regenerate_data():
            """
            サンプルデータ再生成API（開発・デモ用）
            """
            try:
                # データを削除（簡易実装のため全削除）
                # 本来はDELETE文を実行するが、インメモリDBなので再初期化
                self.db_manager = DatabaseManager()
                
                # 新しいサンプルデータを生成
                self._initialize_sample_data()
                
                # 統計情報を取得
                stats = self.db_manager.get_statistics()
                
                return jsonify({
                    'status': 'success',
                    'message': 'サンプルデータを再生成しました',
                    'data': stats
                })
                
            except Exception as e:
                logger.error(f"データ再生成エラー: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'データ再生成に失敗しました: {str(e)}'
                }), 500
    
    def _initialize_sample_data(self):
        """
        サンプルデータの生成と挿入
        アプリ起動時に1回実行
        """
        try:
            logger.info("サンプルデータの生成を開始します...")
            
            # 1週間分のサンプルデータを生成
            sample_activities, sample_daily_moods = self.data_generator.generate_week_data()
            
            # データベースに一括挿入
            activities_count = self.db_manager.insert_activities_batch(sample_activities)
            moods_count = self.db_manager.insert_daily_moods_batch(sample_daily_moods)
            
            inserted_count = activities_count + moods_count
            
            logger.info(f"サンプルデータの挿入が完了しました ({activities_count}件の活動, {moods_count}日分のムード)")
            
            # 統計情報をログ出力
            stats = self.db_manager.get_statistics()
            logger.info(f"データベース統計: {stats}")
            
        except Exception as e:
            logger.error(f"サンプルデータ初期化エラー: {str(e)}")
            raise
    
    def run(self, debug: bool = True, port: int = 5000):
        """
        アプリケーションの起動
        
        Args:
            debug: デバッグモードの有効/無効
            port: ポート番号
        """
        logger.info(f"アプリケーションを起動します (ポート: {port}, デバッグ: {debug})")
        
        try:
            self.app.run(debug=debug, port=port, host='0.0.0.0')
        except KeyboardInterrupt:
            logger.info("アプリケーションが停止されました")
        except Exception as e:
            logger.error(f"アプリケーション実行エラー: {str(e)}")
        finally:
            # クリーンアップ
            self._cleanup()
    
    def _cleanup(self):
        """アプリケーション終了時のクリーンアップ"""
        try:
            if hasattr(self, 'db_manager'):
                self.db_manager.close()
            logger.info("クリーンアップが完了しました")
        except Exception as e:
            logger.error(f"クリーンアップエラー: {str(e)}")

# ========================================
# アプリケーションエントリーポイント
# ========================================

def create_app() -> Flask:
    """
    Flaskアプリケーションファクトリ
    テスト用途やWSGI起動時に使用
    """
    app_instance = LifeAnalysisApp()
    return app_instance.app

def main():
    """
    メイン関数
    直接実行時のエントリーポイント
    """
    # 注意: APIキーは実際のGemini API呼び出し時にチェックされます
    # アプリケーションは常に起動し、UIでの操作確認が可能です
    
    # アプリケーションの作成と起動
    try:
        app_instance = LifeAnalysisApp()
        
        print("🚀 Gemini AI 振り返り分析サンプルアプリが起動しました")
        print("📱 ブラウザで http://localhost:8080 にアクセスしてください")
        print("⏹  停止するには Ctrl+C を押してください")
        print("-" * 50)
        
        app_instance.run(debug=True, port=8080)
        
    except Exception as e:
        logger.error(f"アプリケーション起動エラー: {str(e)}")
        print(f"❌ エラー: {str(e)}")

# 直接実行時のハンドリング
if __name__ == '__main__':
    main()
"""
Gemini APIプロンプト生成サービス
一般的なプロンプトエンジニアリング技術を活用したプロンプト生成

【使用されているプロンプトエンジニアリング技術】
1. System Message: システム役割の明確な定義
2. Few-shot Prompting: ユーザーデータを文脈として提供
3. Template-based Generation: 応答スタイルの動的調整
4. Output Formatting: 一貫した出力形式の確保
5. Parameter Control: パラメータによる出力制御
"""

from typing import List, Dict, Any
from models.activity import Activity
from models.daily_mood import DailyMood
from models.analysis import AnalysisRequest, AnalysisFocus, DetailLevel, ResponseStyle

class GeminiPromptBuilder:
    """
    Gemini API用のプロンプトを生成するクラス
    一般的なプロンプトエンジニアリング技術を活用
    
    【プロンプト技術の詳細解説】
    
    1. System Message (システムメッセージ)
       - AIに「健康とウェルネスの専門家」としての役割を与える
       - 一貫性のある専門的な回答を引き出すため
    
    2. Few-shot Prompting (フューショットプロンプティング)
       - ユーザーの実際の活動データとムードデータを文脈として提供
       - データに基づいた具体的で実用的な分析を生成
    
    3. Template-based Generation (テンプレートベース生成)
       - ユーザーの好みに応じた口調・文体の動的調整
       - パーソナライゼーションの実現
    
    4. Output Formatting (出力フォーマット指定)
       - 分析の焦点、詳細レベルを明確に指定
       - 期待する出力形式の明示
    """
    
    # ベースとなるシステムメッセージ
    SYSTEM_ROLE = """あなたは健康とウェルネスの専門家です。
ユーザーの生活パターンを分析し、データに基づいた洞察と建設的なアドバイスを提供します。
以下のデータを詳しく分析して、ユーザーの生活の質向上に役立つフィードバックをお願いします。"""
    
    # 分析焦点別の指示（Focus-specific Prompting）
    FOCUS_INSTRUCTIONS = {
        AnalysisFocus.MOOD_FOCUSED: """
【分析の焦点: 気分パターンの分析】
特に以下の点に注目して分析してください：
- ムードの変化パターンとトレンド
- 高いムード・低いムードの時間帯や活動との関連性
- ムード改善につながる要因の特定
- 気分の波を安定させるための具体的な提案
""",
        AnalysisFocus.ACTIVITY_FOCUSED: """
【分析の焦点: 活動パターンの分析】
特に以下の点に注目して分析してください：
- 活動の多様性と時間配分
- 健康的な活動とそうでない活動のバランス
- 活動パターンの改善点
- 新しく取り入れるべき活動の提案
""",
        AnalysisFocus.BALANCED: """
【分析の焦点: 生活バランスの評価】
特に以下の点に注目して分析してください：
- 仕事、休息、趣味、運動、社交のバランス
- 各カテゴリーの時間配分の適切性
- バランスの崩れている部分の特定
- 全体的な生活バランス改善のための提案
""",
        AnalysisFocus.WELLNESS_FOCUSED: """
【分析の焦点: 総合的なウェルネス評価】
特に以下の点に注目して分析してください：
- 身体的、精神的、社会的な健康の総合評価
- ストレス要因とリラクゼーション要素の分析
- 長期的な健康維持のための提案
- ライフスタイル全般の改善点
"""
    }
    
    # 詳細レベル別の出力指示（Output Control Prompting）
    DETAIL_INSTRUCTIONS = {
        DetailLevel.CONCISE: """
【出力形式: 簡潔版】
以下の形式で要点のみを3-5個の箇条書きでまとめてください：
■ 主要な発見
・（最も重要な洞察1つ）

■ 推奨アクション
・（最重要な改善提案2-3個）
""",
        DetailLevel.STANDARD: """
【出力形式: 標準版】
以下の形式で適度な詳細と共に分析してください：
■ データの概要
・（期間、活動数、平均ムードなど）

■ 主要な洞察
・（2-3個の重要な発見）

■ 改善提案
・（具体的な提案2-3個）

■ 次のステップ
・（実行可能なアクション）
""",
        DetailLevel.DETAILED: """
【出力形式: 詳細版】
以下の形式で包括的に分析してください：
■ データサマリー
・（詳細な統計情報）

■ 詳細分析
・（時系列変化、パターン、相関関係）

■ 強みの確認
・（良い習慣や傾向）

■ 改善エリア
・（具体的な問題点と原因）

■ 詳細な改善計画
・（5個以上の具体的提案）

■ 長期的な目標設定
・（継続的な改善のための方向性）
"""
    }
    
    # 応答スタイル別の口調指示（Style-based Prompting）
    STYLE_INSTRUCTIONS = {
        ResponseStyle.FRIENDLY: """
【応答スタイル: 親しみやすい】
友人のように温かく親しみやすい口調で回答してください。
励ましの言葉を含め、ポジティブで支援的な雰囲気を心がけてください。
「〜ですね」「〜してみませんか？」などの優しい表現を使用してください。
""",
        ResponseStyle.PROFESSIONAL: """
【応答スタイル: 専門的】
健康・ウェルネス専門家として客観的で専門的な口調で回答してください。
データと事実に基づいた分析を重視し、科学的根拠のある提案をしてください。
「〜と考えられます」「データによると〜」などの専門的表現を使用してください。
""",
        ResponseStyle.ENCOURAGING: """
【応答スタイル: 励まし重視】
ユーザーのモチベーションを高めることを最優先に回答してください。
できていること、改善していることを積極的に評価し、前向きな気持ちになれる内容にしてください。
「素晴らしいですね！」「確実に改善していますね」などの励ましの表現を多用してください。
""",
        ResponseStyle.CASUAL: """
【応答スタイル: カジュアル】
リラックスした気軽な口調で回答してください。
硬すぎず、普段の会話のような自然な表現を使用してください。
「〜な感じですね」「〜してみるといいかも」などのカジュアルな表現を使用してください。
"""
    }
    
    def build_prompt(self, activities: List[Activity], daily_moods: List[DailyMood], request: AnalysisRequest) -> str:
        """
        活動データと日次ムードデータ、分析リクエストからGemini API用のプロンプトを生成
        
        【プロンプト構造の解説】
        1. システムメッセージ → AIの役割設定
        2. データ提供 → Few-shot prompting
        3. 分析焦点指示 → タスク特化
        4. 詳細レベル設定 → Output formatting
        5. スタイル指定 → Template-based generation
        
        Args:
            activities: 分析対象の活動データリスト
            daily_moods: 分析対象の日次ムードデータリスト
            request: 分析リクエスト（パラメータ含む）
            
        Returns:
            生成されたプロンプト文字列
        """
        
        # 1. システムメッセージの設定
        prompt_parts = [self.SYSTEM_ROLE]
        
        # 2. データコンテキストの提供（Few-shot Prompting）
        prompt_parts.append("\n" + self._format_activity_data(activities))
        prompt_parts.append("\n" + self._format_daily_mood_data(daily_moods))
        prompt_parts.append("\n" + self._calculate_mood_statistics(daily_moods))
        
        # 3. 分析焦点の指示（Task-specific Prompting）
        prompt_parts.append(self.FOCUS_INSTRUCTIONS[request.analysis_focus])
        
        # 4. 詳細レベルの設定（Output Formatting）
        prompt_parts.append(self.DETAIL_INSTRUCTIONS[request.detail_level])
        
        # 5. 応答スタイルの指定（Template-based Generation）
        prompt_parts.append(self.STYLE_INSTRUCTIONS[request.response_style])
        
        # 6. 最終指示（Quality Assurance）
        prompt_parts.append("""
【重要な注意事項】
- 提供されたデータに基づいて分析してください
- 推測ではなく、実際のデータから読み取れる事実を重視してください
- 実行可能で具体的な提案をしてください
- ユーザーの生活の質向上を最優先に考えてください
""")
        
        return "\n".join(prompt_parts)
    
    def _format_activity_data(self, activities: List[Activity]) -> str:
        """
        活動データを分析しやすい形式に整形（既存API仕様準拠）
        
        【データ構造化技術】
        - 時系列順での並び替え
        - 視覚的に分かりやすいフォーマット
        - カテゴリ・時間範囲を含む詳細な活動情報
        """
        if not activities:
            return "【活動データ】\nデータがありません。"
        
        formatted_lines = ["【活動データ（時系列順）】"]
        
        # 日付でグループ化
        activities_by_date = {}
        for activity in activities:
            date_str = activity.date.strftime('%Y-%m-%d (%A)') if activity.date else "不明"
            if date_str not in activities_by_date:
                activities_by_date[date_str] = []
            activities_by_date[date_str].append(activity)
        
        # 各日の活動を整形
        for date_str, daily_activities in sorted(activities_by_date.items()):
            formatted_lines.append(f"\n◆ {date_str}")
            
            # 開始時刻順にソート
            daily_activities.sort(key=lambda x: x.start_time if x.start_time else "")
            
            for activity in daily_activities:
                # 時間範囲の表示
                time_range = activity.get_time_range_str()
                
                # 基本活動情報
                activity_line = f"  {time_range} - {activity.title}"
                
                # カテゴリ情報を追加
                if activity.category:
                    category_info = f"[{activity.category}"
                    if activity.category_sub:
                        category_info += f"/{activity.category_sub}"
                    category_info += "]"
                    activity_line += f" {category_info}"
                
                formatted_lines.append(activity_line)
                
                # 活動内容がある場合は追加
                if activity.contents and activity.contents.strip():
                    formatted_lines.append(f"    内容: {activity.contents}")
                
                # 活動時間の長さを表示
                duration = activity.get_duration_minutes()
                if duration:
                    formatted_lines.append(f"    時間: {duration}分")
        
        return "\n".join(formatted_lines)
    
    def _format_daily_mood_data(self, daily_moods: List[DailyMood]) -> str:
        """
        日次ムードデータを分析しやすい形式に整形
        
        【データ構造化技術】
        - 時系列順での並び替え
        - 視覚的に分かりやすいフォーマット
        - ムードの絵文字表現でデータの可読性向上
        """
        if not daily_moods:
            return "【日次ムードデータ】\nデータがありません。"
        
        formatted_lines = ["【日次ムードデータ（時系列順）】"]
        
        # 日付でソート
        sorted_moods = sorted(daily_moods, key=lambda x: x.date if x.date else "")
        
        for daily_mood in sorted_moods:
            date_str = daily_mood.date.strftime('%Y-%m-%d (%A)') if daily_mood.date else "不明"
            mood_emoji = daily_mood.get_mood_emoji()
            mood_description = daily_mood.get_mood_description()
            
            mood_line = f"◆ {date_str}: {daily_mood.mood}/5 {mood_emoji} ({mood_description})"
            formatted_lines.append(mood_line)
            
            # メモがある場合は追加
            if daily_mood.note and daily_mood.note.strip():
                formatted_lines.append(f"   メモ: {daily_mood.note}")
        
        return "\n".join(formatted_lines)
    
    def _calculate_mood_statistics(self, daily_moods: List[DailyMood]) -> str:
        """
        ムードデータの統計情報を計算
        
        【統計分析技術】
        - 基本統計量の算出
        - 分布の可視化
        - トレンド分析のためのデータ整理
        """
        moods = [dm.mood for dm in daily_moods if dm.mood is not None]
        
        if not moods:
            return "【ムード統計】\nムードデータがありません。"
        
        # 基本統計量を計算
        avg_mood = sum(moods) / len(moods)
        max_mood = max(moods)
        min_mood = min(moods)
        
        # ムードの分布を計算
        mood_counts = {i: moods.count(i) for i in range(1, 6)}
        total_mood_records = len(moods)
        
        # 統計情報をフォーマット
        stats_lines = [
            "【日次ムード統計】",
            f"平均ムード: {avg_mood:.1f}/5.0",
            f"最高ムード: {max_mood}/5 (記録日数: {mood_counts[max_mood]}日)",
            f"最低ムード: {min_mood}/5 (記録日数: {mood_counts[min_mood]}日)",
            f"総記録日数: {total_mood_records}日",
            "",
            "ムード分布:"
        ]
        
        # 分布を視覚的に表現
        for mood_value in range(1, 6):
            count = mood_counts[mood_value]
            percentage = (count / total_mood_records) * 100 if total_mood_records > 0 else 0
            emoji = "😊" * mood_value
            bar = "■" * (count // 2) if count > 0 else ""  # 簡易棒グラフ
            
            stats_lines.append(
                f"  {mood_value}点 {emoji}: {count}日 ({percentage:.1f}%) {bar}"
            )
        
        return "\n".join(stats_lines)
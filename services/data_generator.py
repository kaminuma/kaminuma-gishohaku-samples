"""
サンプルデータ生成サービス（既存API仕様準拠）
リアルな活動パターンを模倣したダミーデータの自動生成
"""

import random
from datetime import datetime, timedelta, time, date
from typing import List
import logging

from models.activity import Activity
from models.daily_mood import DailyMood

logger = logging.getLogger(__name__)

class SampleDataGenerator:
    """
    1週間分のリアルなサンプル活動データを生成するクラス（既存API仕様準拠）
    
    【データ生成の特徴】
    - 時間帯に応じた活動パターンの模倣
    - 平日と週末の違いを反映
    - 日次ムードと活動の分離管理
    - カテゴリ・サブカテゴリを含む詳細な活動データ
    - 開始時刻〜終了時刻の時間範囲
    """
    
    # 活動テンプレートの定義（既存API仕様準拠）
    # (category, category_sub, title, contents, typical_duration_minutes)
    ACTIVITY_TEMPLATES = [
        # 仕事関連
        ("仕事", "メール", "メール確認・返信", "受信メールの確認と返信作業", 30),
        ("仕事", "会議", "チームミーティング", "週次チーム進捗会議に参加", 60),
        ("仕事", "資料作成", "プレゼン資料作成", "次回プレゼン用の資料作成", 90),
        ("仕事", "コーディング", "システム開発", "新機能の実装作業", 120),
        ("仕事", "企画", "新企画の検討", "次期プロジェクトの企画立案", 75),
        
        # 運動関連
        ("運動", "ランニング", "朝ランニング", "公園での30分ジョギング", 30),
        ("運動", "筋トレ", "筋力トレーニング", "ジムでのウェイトトレーニング", 45),
        ("運動", "ヨガ", "モーニングヨガ", "家でのヨガセッション", 30),
        ("運動", "散歩", "午後の散歩", "近所の公園を散歩", 20),
        ("運動", "ストレッチ", "ストレッチタイム", "体をほぐすストレッチ", 15),
        
        # 食事関連
        ("食事", "朝食", "朝食時間", "パンとコーヒーで朝食", 20),
        ("食事", "昼食", "お昼時間", "オフィス近くのレストランでランチ", 45),
        ("食事", "夕食", "夕食時間", "家族と一緒に夕食", 30),
        ("食事", "料理", "夕食の料理", "今日の夕食を作る", 40),
        ("食事", "軽食", "おやつタイム", "コーヒーとお菓子でブレイク", 15),
        
        # 趣味関連
        ("趣味", "読書", "本を読む", "気になっていた本を読進", 60),
        ("趣味", "映画", "映画鑑賞", "配信サービスで映画を観る", 90),
        ("趣味", "音楽", "音楽鑑賞", "お気に入りの音楽を聞く", 30),
        ("趣味", "ゲーム", "ゲームプレイ", "スマホゲームでリラックス", 45),
        ("趣味", "創作", "創作活動", "絵を描いたり文章を書いたり", 60),
        
        # 家事関連
        ("家事", "掃除", "部屋の掃除", "リビングと寝室の掃除", 40),
        ("家事", "洗濯", "洗濯・洗濯物干し", "洗濯機を回して洗濯物を干す", 20),
        ("家事", "買い物", "スーパーで買い物", "今日の材料を買いに行く", 30),
        ("家事", "整理", "部屋の整理整頓", "クローゼットや机の整理", 45),
        
        # 学習関連
        ("学習", "プログラミング", "プログラミング学習", "オンライン講座でPythonを学ぶ", 60),
        ("学習", "語学", "英語の勉強", "英会話アプリでレッスン", 30),
        ("学習", "資格", "資格試験勉強", "来月の試験に向けて勉強", 90),
        ("学習", "読書", "専門書を読む", "仕事に関連する技術書を読む", 45),
        
        # 交流関連
        ("交流", "家族", "家族との時間", "家族と会話しながら過ごす", 45),
        ("交流", "友人", "友人との電話", "久しぶりに友人と電話", 30),
        ("交流", "SNS", "SNSチェック", "ソーシャルメディアをチェック", 15),
        ("交流", "コミュニティ", "オンライン交流", "趣味のコミュニティで交流", 30),
        
        # 移動関連
        ("移動", "通勤", "会社への通勤", "電車で会社まで移動", 40),
        ("移動", "帰宅", "会社から帰宅", "会社から家まで帰る", 40),
        ("移動", "外出", "買い物の移動", "ショッピングセンターへ移動", 25),
        
        # 休憩関連
        ("休憩", "仮眠", "昼休み", "ソファで少し仮眠", 20),
        ("休憩", "コーヒー", "コーヒーブレイク", "カフェでコーヒーを飲む", 15),
        ("休憩", "入浴", "お風呂タイム", "リラックスしながら入浴", 25),
        ("休憩", "瞑想", "瞑想・深呼吸", "心を落ち着かせる時間", 10),
    ]
    
    # 時間帯の定義（開始時刻の選択肢）
    TIME_START_OPTIONS = [
        "07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
        "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", 
        "19:00", "20:00", "21:00", "22:00"
    ]
    
    def __init__(self):
        """データ生成器の初期化"""
        # 一貫したランダムシードで再現性を確保（開発時）
        # random.seed(42)  # 本番では削除
        
    def generate_week_data(self, base_date: date = None) -> tuple[List[Activity], List[DailyMood]]:
        """
        1週間分のサンプル活動データと日次ムードデータを生成
        
        Args:
            base_date: 基準日（Noneの場合は今日から過去7日間）
            
        Returns:
            (活動データリスト, 日次ムードデータリスト)のタプル
        """
        if base_date is None:
            base_date = datetime.now().date()
        
        activities = []
        daily_moods = []
        
        # 過去7日間のデータを生成
        for days_ago in range(7):
            current_date = base_date - timedelta(days=days_ago)
            
            # 活動データを生成
            daily_activities = self._generate_daily_activities(current_date)
            activities.extend(daily_activities)
            
            # 日次ムードを生成
            daily_mood = self._generate_daily_mood(current_date)
            daily_moods.append(daily_mood)
        
        logger.info(f"サンプルデータを生成しました: {len(activities)}件の活動, {len(daily_moods)}日分のムード")
        return activities, daily_moods
    
    def _generate_daily_activities(self, target_date: date) -> List[Activity]:
        """
        特定の日の活動データを生成（既存API仕様準拠）
        
        【リアルなパターンの実装】
        - 曜日による活動パターンの違い
        - 時間帯による活動の重み付け
        - カテゴリ・サブカテゴリ付きの詳細活動
        - 開始〜終了時刻の時間範囲
        
        Args:
            target_date: 対象日
            
        Returns:
            その日の活動データリスト
        """
        is_weekend = target_date.weekday() >= 5  # 土日判定
        
        # 1日の活動数を決定（週末は少なめ）
        if is_weekend:
            num_activities = random.randint(4, 7)  # 週末: 4-7個
        else:
            num_activities = random.randint(5, 9)  # 平日: 5-9個
        
        # 開始時刻をランダムに選択（重複回避）
        used_start_times = set()
        daily_activities = []
        
        for _ in range(num_activities):
            # 重複しない開始時刻を選択
            available_times = [t for t in self.TIME_START_OPTIONS if t not in used_start_times]
            if not available_times:
                break  # 使用可能な時間がなくなったら終了
                
            start_time_str = random.choice(available_times)
            used_start_times.add(start_time_str)
            
            # 時間帯に基づいて活動テンプレートを選択
            activity_template = self._select_activity_template(start_time_str, is_weekend)
            
            # Activity オブジェクトを作成
            activity = self._create_activity_from_template(
                target_date, start_time_str, activity_template
            )
            
            daily_activities.append(activity)
        
        # 開始時刻順にソート
        daily_activities.sort(key=lambda x: x.start_time if x.start_time else time(0, 0))
        
        return daily_activities
    
    def _select_activity_template(self, start_time_str: str, is_weekend: bool) -> tuple:
        """
        時間帯と曜日に応じた活動テンプレートを選択
        
        Args:
            start_time_str: 開始時刻文字列（HH:MM形式）
            is_weekend: 週末フラグ
            
        Returns:
            選択された活動テンプレート
        """
        hour = int(start_time_str.split(':')[0])
        
        # 時間帯による重み付け
        if 7 <= hour < 9:
            # 朝の時間帯：食事、移動、運動
            weights = [1 if cat in ["食事", "移動", "運動"] else 0.1 for cat, _, _, _, _ in self.ACTIVITY_TEMPLATES]
        elif 9 <= hour < 12:
            # 午前中：仕事（平日）、家事・趣味（週末）
            if is_weekend:
                weights = [1 if cat in ["家事", "趣味", "運動"] else 0.2 for cat, _, _, _, _ in self.ACTIVITY_TEMPLATES]
            else:
                weights = [1 if cat == "仕事" else 0.1 for cat, _, _, _, _ in self.ACTIVITY_TEMPLATES]
        elif 12 <= hour < 14:
            # 昼の時間帯：食事、休憩
            weights = [1 if cat in ["食事", "休憩"] else 0.2 for cat, _, _, _, _ in self.ACTIVITY_TEMPLATES]
        elif 14 <= hour < 18:
            # 午後：仕事（平日）、趣味・学習（週末）
            if is_weekend:
                weights = [1 if cat in ["趣味", "学習", "家事"] else 0.3 for cat, _, _, _, _ in self.ACTIVITY_TEMPLATES]
            else:
                weights = [1 if cat == "仕事" else 0.2 for cat, _, _, _, _ in self.ACTIVITY_TEMPLATES]
        elif 18 <= hour < 21:
            # 夕方〜夜：食事、家事、趣味、交流
            weights = [1 if cat in ["食事", "家事", "趣味", "交流"] else 0.3 for cat, _, _, _, _ in self.ACTIVITY_TEMPLATES]
        else:
            # 夜遅く：趣味、休憩、学習
            weights = [1 if cat in ["趣味", "休憩", "学習"] else 0.2 for cat, _, _, _, _ in self.ACTIVITY_TEMPLATES]
        
        # 重み付きランダム選択
        return random.choices(self.ACTIVITY_TEMPLATES, weights=weights)[0]
    
    def _create_activity_from_template(self, target_date: date, start_time_str: str, template: tuple) -> Activity:
        """
        活動テンプレートからActivityオブジェクトを生成
        
        Args:
            target_date: 対象日
            start_time_str: 開始時刻文字列
            template: 活動テンプレート
            
        Returns:
            生成されたActivityオブジェクト
        """
        category, category_sub, title, contents, typical_duration = template
        
        # 開始時刻を解析
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        
        # 終了時刻を計算（典型的な長さ + ランダムな変動）
        duration_variation = random.randint(-10, 15)  # -10〜+15分の変動
        actual_duration = max(5, typical_duration + duration_variation)  # 最低5分
        
        start_datetime = datetime.combine(target_date, start_time)
        end_datetime = start_datetime + timedelta(minutes=actual_duration)
        end_time = end_datetime.time()
        
        return Activity(
            user_id=1,  # サンプル用固定値
            date=target_date,
            start_time=start_time,
            end_time=end_time,
            title=title,
            contents=contents,
            category=category,
            category_sub=category_sub,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _generate_daily_mood(self, target_date: date) -> DailyMood:
        """
        特定の日の日次ムードを生成
        
        Args:
            target_date: 対象日
            
        Returns:
            生成された日次ムードデータ
        """
        is_weekend = target_date.weekday() >= 5  # 土日判定
        
        # 曜日による基本ムードの調整
        if is_weekend:
            # 週末は少し高めの傾向
            base_mood_options = [3, 3, 4, 4, 5]
        else:
            # 平日は中程度
            base_mood_options = [2, 3, 3, 4, 4]
        
        # ベースムードを選択
        base_mood = random.choice(base_mood_options)
        
        # ランダムな変動を加える
        variation = random.choice([-1, 0, 0, 1])  # 0の重みを高く
        final_mood = base_mood + variation
        
        # 1-5の範囲に制限
        mood_value = max(1, min(5, final_mood))
        
        # メモを生成（ランダム）
        mood_notes = [
            "今日は調子が良い",
            "普通の一日",
            "少し疲れている", 
            "気分爽快！",
            "まあまあの気分",
            "充実した一日",
            "リラックスできた",
            None,  # メモなしも含める
            None,
            None
        ]
        
        note = random.choice(mood_notes)
        
        # DailyMoodオブジェクトを作成
        return DailyMood(
            date=target_date,
            mood=mood_value,
            note=note,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def generate_custom_data(self, 
                           date_range: int = 7,
                           min_activities_per_day: int = 4,
                           max_activities_per_day: int = 9,
                           mood_bias: float = 0.0) -> tuple[List[Activity], List[DailyMood]]:
        """
        カスタマイズ可能なデータ生成
        
        Args:
            date_range: 生成する日数
            min_activities_per_day: 1日あたりの最小活動数
            max_activities_per_day: 1日あたりの最大活動数
            mood_bias: ムードのバイアス（-2.0 〜 +2.0）
            
        Returns:
            (活動データリスト, 日次ムードデータリスト)のタプル
        """
        activities = []
        daily_moods = []
        base_date = datetime.now().date()
        
        for days_ago in range(date_range):
            current_date = base_date - timedelta(days=days_ago)
            is_weekend = current_date.weekday() >= 5
            
            # 活動データを生成
            num_activities = random.randint(min_activities_per_day, max_activities_per_day)
            used_start_times = set()
            
            for _ in range(num_activities):
                available_times = [t for t in self.TIME_START_OPTIONS if t not in used_start_times]
                if not available_times:
                    break
                    
                start_time_str = random.choice(available_times)
                used_start_times.add(start_time_str)
                
                activity_template = self._select_activity_template(start_time_str, is_weekend)
                activity = self._create_activity_from_template(current_date, start_time_str, activity_template)
                activities.append(activity)
            
            # 日次ムードを生成（バイアス適用）
            daily_mood = self._generate_daily_mood(current_date)
            
            # ムードバイアスを適用
            adjusted_mood = daily_mood.mood + mood_bias
            daily_mood.mood = max(1, min(5, int(round(adjusted_mood))))
            
            daily_moods.append(daily_mood)
        
        logger.info(f"カスタムサンプルデータを生成しました: {len(activities)}件の活動, {len(daily_moods)}日分のムード")
        return activities, daily_moods
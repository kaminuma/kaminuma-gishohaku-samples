# 🤖 Gemini AI 振り返り分析サンプルアプリケーション

**プロンプトエンジニアリング学習用**のGemini API活用サンプルアプリケーションです。1週間分の活動データとムードデータを自動生成し、Gemini APIで個人の振り返り分析を行います。

## 📋 特徴

- **学習目的**: プロンプトエンジニアリング技術の実践的な学習
- **シンプルな実装**: 認証不要、ユーザー管理不要で即座に動作確認可能
- **自動データ生成**: リアルな活動データ・日次ムードデータを起動時に自動生成
- **プロンプト技術学習**: 5つのプロンプトエンジニアリング技術を実装・活用
- **モジュラー設計**: 保守しやすい分離されたアーキテクチャ

## 📈 学習効果

このサンプルアプリケーションで学習できる内容：

### プロンプトエンジニアリング技術
1. **System Message** - AI専門家の役割設定
2. **Few-shot Prompting** - データコンテキスト提供
3. **出力制御** - 一貫した出力形式とテンプレート制御
4. **動的調整** - パラメータによる分析内容の柔軟な調整
5. **スタイル調整** - ユーザー好みの応答スタイル調整

### Web開発技術
- Flask によるRESTful API設計
- SQLite データベース操作
- フロントエンド・バックエンド分離
- レスポンシブWebデザイン

### AI API統合
- エラーハンドリング戦略
- レート制限対応
- レスポンス処理最適化

## 🚀 セットアップ・起動手順

### 1. 環境要件

- **Python**: 3.9以上
- **OS**: Windows, macOS, Linux
- **メモリ**: 最低1GB（推奨2GB以上）

### 2. リポジトリの取得

```bash
# Gitでクローンする場合
git clone https://github.com/kaminuma/kaminuma-gishohaku-samples.git
cd kaminuma-gishohaku-samples

# またはZIPファイルを展開してディレクトリに移動
```

### 3. 仮想環境の作成（推奨）

```bash
# Python仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows
```

### 4. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 5. Gemini APIキーの取得・設定

#### APIキーの取得手順
手順は原則として、UIの変更などがありえるので公式に従ってください。
また、APIキーは当アプリ作成時は無料枠がありましたが、無料枠があることを保証するものではありません。

**無料枠が切れると重要課金制になる点に注意してください。**

上記を加味した上で、一般的なAPIキー作成手順は下記となります。
1. ブラウザで [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. 「Get API key」または「APIキーを作成」ボタンをクリック
3. Googleアカウントでログイン（初回は利用規約に同意）
4. 「Create API Key」→「Create API key in new project」を選択
5. 生成されたAPIキーをコピー

> **注意**: APIキーは他人と共有しないでください

#### 環境変数の設定

```bash
# .env.example をコピーして .env ファイルを作成
cp .env.example .env
```

`.env` ファイルを開き、取得したAPIキーを設定：

```env
# 変更前
GEMINI_API_KEY=your-api-key-here

# 変更後（実際のAPIキーに置き換える）
GEMINI_API_KEY=実際のAPIキー
```

### 6. アプリケーションの起動

```bash
python3 app.py
```

### 7. ブラウザでアクセス

```
http://localhost:8080
```

> **ポート変更**: デフォルトでポート8080を使用しています（ポート5000が他のサービスで使用されている場合があるため）

## 📖 使い方

1. **データの確認**
   - 右側のパネルに自動生成された1週間分の活動データと日次ムードが表示されます
   - 活動データ: 生成したサンプルデータを用いて分析体験可能
   - ムードデータ: 1-5の5段階評価での日次ムード記録

2. **分析パラメータの選択**
   - **分析の焦点**: 気分、活動、バランス、ウェルネスから選択
   - **詳細レベル**: 簡潔、標準、詳細から選択
   - **応答スタイル**: 親しみやすい、専門的、励まし、カジュアルから選択

3. **分析の実行**
   - 「🚀 分析を実行」ボタンをクリック
   - Gemini APIが活動データとムードデータを総合的に分析
   - パーソナライズされた振り返り分析結果を表示

## 📁 プロジェクト構成

```
sample_prompt_kit/
├── app.py                      # メインアプリケーション
├── models/
│   ├── __init__.py
│   ├── activity.py             # 活動データモデル
│   ├── daily_mood.py           # 日次ムードデータモデル
│   └── analysis.py             # 分析リクエスト・結果モデル
├── services/
│   ├── __init__.py
│   ├── prompt_builder.py       # プロンプト生成サービス
│   ├── gemini_service.py       # Gemini API統合サービス
│   └── data_generator.py       # サンプルデータ生成
├── database/
│   ├── __init__.py
│   └── database.py             # データベース管理
├── templates/
│   └── index.html              # フロントエンドHTML
├── requirements.txt            # Pythonパッケージ一覧
├── .env.example               # 環境変数テンプレート
├── .env                       # 環境変数（要作成）
└── README.md                  # このファイル
```

## 🔧 技術スタック

- **バックエンド**: Flask (Python)
- **フロントエンド**: HTML + Vanilla JavaScript
- **データベース**: SQLite (インメモリ)
- **AI API**: Google Gemini API

## 💡 実装されているプロンプトエンジニアリング技術

本実装では以下の5つのプロンプトエンジニアリング技術を組み合わせています：

1. **System Message**: AIの専門家役割設定
2. **Few-shot Prompting**: データに基づく文脈提供
3. **出力制御**: 一貫した出力形式とテンプレート制御
4. **動的調整**: パラメータによる分析内容の柔軟な調整
5. **スタイル調整**: ユーザー好みの応答スタイル調整

### 分析パラメータ詳細

#### Focus（分析の焦点）
- **mood**: ムードパターンの分析
- **activities**: 活動の多様性と配分
- **balance**: 生活バランスの評価
- **wellness**: 総合的な健康評価

#### Detail Level（詳細レベル）
- **brief**: 3-5個の要点
- **standard**: 適度な詳細と提案
- **detailed**: 詳細な分析と5個以上の提案

#### Response Style（応答スタイル）
- **friendly**: 親しみやすい語り口
- **professional**: データ重視の客観的分析
- **encouraging**: モチベーション向上重視
- **casual**: リラックスした雰囲気

## 🐛 トラブルシューティング

### Gemini APIエラー

**Invalid API key**
```
→ .env ファイルのAPIキーを確認してください
```

**Quota exceeded**
```
→ API利用制限に達しています。少し待ってから再試行してください
```

**API not enabled**
```
→ Google Cloud ConsoleでGenerative Language APIを有効化してください
```

### インストール・起動エラー

**インポートエラーが発生する場合**
```bash
# 仮想環境の再作成
python3 -m venv venv
source venv/bin/activate  # Linux/Mac または venv\Scripts\activate  # Windows

# 依存関係の再インストール
pip install -r requirements.txt
```

**ポートが使用中の場合**
```python
# app.pyの最後の行を変更してポート番号を調整
app_instance.run(debug=True, port=8081)
```

**Pythonバージョンエラー**
```bash
python3 --version  # 3.9以上であることを確認
```

### セキュリティ関連

**APIキーの適切な管理**
```python
# ✅ 良い例：環境変数から読み込む
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
```

```python
# ❌ 悪い例：ハードコーディング
api_key = "実際のAPIキー"  # 絶対にやらない！
```

## 📚 参考リンク

- [Google AI Studio](https://ai.google.dev/aistudio)
- [Gemini API ドキュメント](https://ai.google.dev/docs)
- [Flask公式ドキュメント](https://flask.palletsprojects.com/)
- [Python公式チュートリアル](https://docs.python.org/ja/3/tutorial/)

## ⚠️ 注意事項

- **学習目的**: このアプリケーションはプロンプトエンジニアリングの学習目的で作成されています
- **本番非対応**: 本番環境での使用は想定していません
- **APIキー管理**: APIキーは適切に管理し、絶対に公開リポジトリにコミットしないでください
- **データ保持**: インメモリデータベースのため、アプリ終了時にデータは消去されます

## 🤝 貢献・ライセンス

書籍のサンプルコードのため、プルリクエストは受け付けていません。
フィードバックやご質問は、Issueでお知らせください。

---

**更新**: 2025年9月
**用途**: プロンプトエンジニアリング学習目的
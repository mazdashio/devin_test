# AI くるまデザイナー (AI Car Designer)

子供の車の塗り絵を、北海道の雪山テストコースで走るフォトリアリスティックな車の画像に変換するFlaskウェブアプリケーションです。

## 機能

- **画像アップロード**: ドラッグ＆ドロップまたはクリックで画像をアップロード（PNG, JPG, JPEG対応）
- **車種選択**: MAZDA3 FASTBACK、EUNOS ROADSTER、MAZDA 787Bから選択
- **走行モード選択**:
  - 疾走感: 高速ドリフト、雪煙が舞う
  - 雪まみれ: 雪に覆われた車、吹雪の中を突き進む
  - 夜の幻想: ダイヤモンドダストが輝く幻想的な夜景
- **画像生成**: Google Gemini APIを使用してAI画像生成
- **画像保存**: 生成された画像をダウンロード

## 技術スタック

- Python 3.10+
- Flask
- Google Gemini API (gemini-2.0-flash-exp-image-generation)
- HTML/CSS/JavaScript
- Pillow

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/mazdashio/devin_test.git
cd devin_test
```

### 2. 仮想環境の作成（推奨）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成します：

```bash
cp .env.example .env
```

`.env`ファイルを編集して、必要な値を設定します：

```
GEMINI_API_KEY=your_api_key_here
DRY_RUN=true
```

- `GEMINI_API_KEY`: Google Gemini APIキー
- `DRY_RUN`: `true`の場合、API呼び出しをスキップしてプレースホルダー画像を返します

### 5. アプリケーションの起動

```bash
python app.py
```

ブラウザで http://localhost:5000 にアクセスしてください。

## 使い方

1. 左側のアップロードエリアに車の塗り絵画像をドラッグ＆ドロップ（またはクリックして選択）
2. 車種を選択（MAZDA3 FASTBACK、EUNOS ROADSTER、MAZDA 787B）
3. 走行モードを選択（疾走感、雪まみれ、夜の幻想）
4. 「生成する」ボタンをクリック
5. 生成された画像が右側に表示されます
6. 「保存する」ボタンで画像をダウンロード

## DRY RUNモード

`DRY_RUN=true`を設定すると、Gemini APIを呼び出さずにプレースホルダー画像を返します。これは開発・テスト時に便利です。

## ライセンス

MIT License

## 作成者

Devin AI

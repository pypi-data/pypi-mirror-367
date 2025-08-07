# SpeechFlow プロジェクト要件定義書

## プロジェクト概要
**SpeechFlow**は、複数のTTSエンジンを統一的なインターフェースで扱えるPython用音声合成ラッパーライブラリです。

### 目的
- 他アプリケーションのバックエンドとして利用可能な音声合成ライブラリの提供
- TTSエンジンの差し替えを容易にする抽象化層の実装
- シンプルで使いやすいPythonic APIの提供

## 技術要件

### 対応環境
- Python 3.12以上
- クロスプラットフォーム対応（Windows、macOS、Linux）
- CUDA対応（PyTorch使用時）

### 対応TTSエンジン
1. **OpenAI TTS** - OpenAI APIを使用したテキスト音声合成
2. **Google GenAI** - Google GenAI APIを使用したTTS（google-genai使用）
3. **FishAudio** - FishAudio APIを使用したクラウドベースTTS
4. **Kokoro** - Kokoroライブラリを使用したTTS
5. **Style-Bert-VITS2** - ローカルで動作する高品質なTTSモデル

### 主要機能
1. **テキストプロンプト入力**
   - 統一的なテキスト入力インターフェース
   - 各TTSエンジン固有のオプションを抽象化

2. **ストリーミング機能**
   - リアルタイム音声ストリーミング対応
   - バッファリング制御

3. **音声ファイル保存**
   - WAV、MP3等の一般的な音声形式での保存
   - メタデータの付与

4. **PyAudio統合**
   - 直接音声再生機能
   - 再生制御（再生、停止、一時停止）

## アーキテクチャ設計

### クラス構造
```
speechflow/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── base.py          # 抽象基底クラス
│   └── exceptions.py    # カスタム例外
├── engines/
│   ├── __init__.py
│   ├── openai.py        # OpenAI TTS実装
│   ├── gemini.py        # Google GenAI TTS実装
│   ├── fish_audio.py    # FishAudio TTS実装
│   ├── fishspeech.py    # FishSpeech TTS実装（スケルトン）
│   ├── kokoro.py        # Kokoro TTS実装
│   └── stylebert.py     # Style-Bert-VITS2実装
├── audio/
│   ├── __init__.py
│   ├── player.py        # PyAudio再生機能
│   └── writer.py        # ファイル保存機能
└── utils/
    ├── __init__.py
    └── audio_processing.py  # NumPy音声処理
```

### 主要インターフェース
```python
from speechflow import OpenAITTSEngine, AudioPlayer, AudioWriter

# コンポーネントの初期化（分離されたアーキテクチャ）
engine = OpenAITTSEngine(api_key="your-api-key")
player = AudioPlayer()
writer = AudioWriter()

# 基本的な音声合成
audio = engine.get("こんにちは、世界！")

# 音声再生
player.play(audio)

# ファイル保存
writer.save(audio, "output.wav")

# ストリーミング再生（結合されたAudioDataを返す）
combined_audio = player.play_stream(engine.stream("長いテキストをストリーミング..."))

# ストリーミング保存（結合されたAudioDataを返す）
combined_audio = writer.save_stream(engine.stream("テキスト"), "output.wav")
```

### 設定管理
現在、各TTSエンジンは独立して初期化され、APIキーは初期化時に直接渡されます。
環境変数や.envファイルからの読み込みは、アプリケーション側で実装してください。

```python
# 例：アプリケーション側での設定管理
import os
from speechflow import OpenAITTSEngine

# 環境変数から読み込み
engine = OpenAITTSEngine(api_key=os.getenv("OPENAI_API_KEY"))

# または直接指定
engine = OpenAITTSEngine(api_key="your-api-key")
```

## 実装状況（2025年1月時点）

### 完了済み
1. **コア機能**
   - TTSエンジンの抽象化インターフェース（TTSEngineBase）
   - 統一API（get/stream メソッド）
   - AudioDataクラスによる音声データ管理

2. **エンジン実装**
   - OpenAI TTS（PCMフォーマット、真のストリーミング対応）
   - Gemini TTS（単一チャンクストリーミング、speed パラメータ対応）
   - FishAudio TTS（ストリーミング対応）
   - Kokoro TTS（多言語対応、ローカル実行）
   - Style-Bert-VITS2（日本語特化、感情表現対応）

3. **音声処理機能**
   - AudioPlayer（同期的再生、ストリーミング対応）
   - AudioWriter（ファイル保存、ストリーミング保存）
   - 分離されたアーキテクチャ（エンジン/プレイヤー/ライター独立）

### 未実装
1. **エンジン**
   - FishSpeech TTS（スケルトンのみ）

2. **追加機能**
   - 非同期処理（asyncio対応）
   - キャッシング機能
   - 音声パラメータの統一的な制御
   - 統一的な設定管理システム

## 依存関係

### コア依存関係（pyproject.tomlに定義済み）
- `numpy>=1.26.4` - 音声データ処理
- `pyaudio>=0.2.14` - 音声再生
- `pydantic>=2.0` - データ検証

### TTSエンジン依存関係
- `openai>=1.84.0` - OpenAI TTS
- `google-genai>=1.18.0` - Google GenAI TTS
- `fish-audio-sdk>=2025.6.3` - FishAudio TTS
- `kokoro>=0.9.4` - Kokoro TTS
- `style-bert-vits2>=2.5.0` - Style-Bert-VITS2
- `pyopenjtalk>=0.4.1` - 日本語音声処理（Style-Bert-VITS2用）
- `misaki[ja]>=0.9.4` - 日本語辞書（Kokoro日本語用）

### PyTorch依存関係（CUDA対応）
- `torch` - Style-Bert-VITS2で使用
- `torchvision` - 画像処理（何かのライブラリが使うかもしれないという念のためのimport）
- `torchaudio` - 音声処理（何かのライブラリが使うかもしれないという念のためのimport）
- CUDA 12.6対応のPyTorchインデックスを使用

## 実装上の重要な注意事項

### ストリーミング仕様（2025年8月時点）

#### OpenAI TTS
- **真のストリーミング対応**: 複数の小さなチャンクを順次返す
- **コールドスタート問題**: 最初のAPI呼び出しは10-20秒の遅延が発生
- **Warmup推奨**: 初期化時にwarmup呼び出しを行うことで、以降の低レイテンシを実現
- **使用フォーマット**: PCM（シンプルな実装のため）

#### Gemini TTS
- **単一チャンク仕様**: ドキュメント上はストリーミング対応だが、実際は全音声を1チャンクで返す
- **既知の制限**: Google AI Developers Forumで確認済みの仕様
- **遅延**: 全音声生成完了まで待機（6-57秒、テキスト長に依存）
- **speed パラメータ**: 音声速度調整対応（API一貫性のため追加）

#### FishAudio TTS
- **真のストリーミング対応**: リアルタイムでチャンクを返す
- **モデル選択**: s1, s1-mini, speech-1.6, speech-1.5, agent-x0
- **カスタムボイス**: ユーザー定義のボイスIDを使用可能

#### Kokoro TTS
- **ローカル実行**: GPU/CPU上で動作
- **多言語対応**: 9言語（英語、スペイン語、フランス語、日本語など）
- **ストリーミング**: 文単位での生成（真のストリーミングではない）

#### Style-Bert-VITS2
- **日本語特化**: 日本語テキストに最適化
- **感情表現**: 7つの感情スタイル対応
- **ストリーミング**: 文単位での生成（真のストリーミングではない）
- **GPU推奨**: 高速な音声生成にはGPUが必要

## 今後の検討事項
- 音声パラメータ（速度、ピッチ、音量）の統一的な制御
- キャッシング機能
- 非同期処理のサポート（asyncio対応）
- より多くのTTSエンジンへの対応
- 音声品質評価メトリクスの実装
- マルチ言語対応の強化

## 参考資料
### Gemini TTS
https://zenn.dev/sonicmoov/articles/bd862039bcba46

### OpenAI
https://qiita.com/syukan3/items/59212050a470408ecc2b

### Kokoro
https://qiita.com/syun88/items/1c33c967e06c57fb938f

## Style-Bert-VITS2
https://zenn.dev/asap/articles/f8c0621cdd74cc
https://note.com/sirodon_256/n/n40b2b1bd5aca

## FishAudio
https://docs.fish.audio/text-to-speech/text-to-speech
https://docs.fish.audio/text-to-speech/fine-grained-control
https://docs.fish.audio/emotion-control/tts-emotion-and-control-tags-user-guide

## 実装ガイドライン

### コード規約
- すべてのTTSエンジンクラスは `TTSEngine` サフィックスを使用
- 統一API: `get()` メソッド（同期的な音声合成）、`stream()` メソッド（ストリーミング）
- `synthesize()` メソッドは廃止（`get()` を使用）
- ファイル名はsnake_case（例: `fish_audio.py`、`fishspeech.py` ではなく `fish_speech.py` が望ましいが現状維持）

## PyPIパッケージング・公開ガイド

### 前提条件
- uvがインストールされていること
- PyPIアカウントを作成済みであること
- PyPI APIトークンを取得済みであること（推奨）

### 1. パッケージのビルド

```bash
# uvを使ってビルドツールを実行
uv run python -m build
```

これにより、`dist/` ディレクトリに以下のファイルが生成されます：
- `speechflow-0.1.0.tar.gz` - ソース配布物
- `speechflow-0.1.0-py3-none-any.whl` - Wheel配布物

### 2. ビルド結果の確認

```bash
# 生成されたファイルの確認
ls dist/

# パッケージの内容確認
uv run twine check dist/*
```

### 3. TestPyPIへのアップロード（推奨）

本番環境にアップロードする前に、TestPyPIでテストすることを推奨します。

```bash
# TestPyPIにアップロード
uv run twine upload --repository testpypi dist/*
```

TestPyPIからのインストールテスト：
```bash
# 新しい仮想環境でテスト
uv venv test-env
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ speechflow
```

### 4. 本番PyPIへのアップロード

```bash
# PyPIにアップロード
uv run twine upload dist/*
```

### 5. 認証設定（オプション）

毎回認証情報を入力する代わりに、`.pypirc` ファイルを設定できます：

```ini
# ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # あなたのAPIトークン

[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # TestPyPI用のAPIトークン
```

### 6. バージョン更新時の手順

1. `pyproject.toml` の `version` を更新
2. 変更をコミット
3. Gitタグを作成: `git tag v0.1.1`
4. `dist/` ディレクトリをクリーン: `rm -rf dist/`
5. 新しいバージョンをビルド: `uv run python -m build`
6. PyPIにアップロード: `uv run twine upload dist/*`

### トラブルシューティング

- **パッケージ名の重複**: PyPIで既に使用されている名前は使えません
- **認証エラー**: APIトークンが正しく設定されているか確認
- **メタデータエラー**: `pyproject.toml` の必須フィールドを確認
  - name, version, description, authors, license など

### 必要なメタデータの確認

PyPIに公開する前に、以下のメタデータが `pyproject.toml` に含まれていることを確認：

- [x] name
- [x] version
- [x] description
- [x] readme
- [x] authors
- [x] license
- [x] requires-python
- [ ] keywords（オプション）
- [ ] classifiers（オプション）
- [ ] homepage/repository（オプション）

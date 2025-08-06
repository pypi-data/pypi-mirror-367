# ErrorForecaster

[![PyPI version](https://badge.fury.io/py/errorforecaster.svg)](https://badge.fury.io/py/errorforecaster)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ErrorForecasterは、Pythonコード内の潜在的なバグ発生確率を予測する静的解析ツールです。AST（Abstract Syntax Tree）解析と統計的/ヒューリスティックモデルを使用して、コードの問題箇所を特定し、改善提案を提供します。

## 🚀 特徴

- **7種類のバグパターン検出**: 可変デフォルト引数、bare except句、未使用インポート、変数シャドウイング、大きな関数、深い再帰、非効率なループ
- **確率ベースの分析**: 各問題に対してバグ発生確率を計算
- **多様な出力形式**: テキスト、JSON、HTML、Markdownレポート
- **CLI & API**: コマンドラインとプログラムの両方から使用可能
- **カスタム例外処理**: 適切なエラーハンドリング

## 📦 インストール

### PyPIからインストール

```bash
pip install errorforecaster
```

### 開発版をインストール

```bash
pip install git+https://github.com/yourusername/errorforecaster.git
```

## 🛠️ 使用方法

### コマンドライン（CLI）

#### 基本的な使用法

```bash
# 単一ファイルをスキャン
errorforecaster scan myfile.py

# ディレクトリ全体をスキャン
errorforecaster scan ./src/

# JSON形式で出力
errorforecaster scan myfile.py --json

# HTMLレポートを生成
errorforecaster scan myfile.py --html report.html

# Markdownレポートを生成
errorforecaster scan myfile.py --markdown report.md

# 確率70%以上の問題のみ表示
errorforecaster scan myfile.py --threshold 70
```

#### ヘルプの表示

```bash
errorforecaster --help
errorforecaster scan --help
```

### Python API

```python
from errorforecaster import Forecaster

# 単一ファイルをスキャン
results = Forecaster.scan("myfile.py")
for issue in results:
    print(f"Line {issue['line']}: {issue['pattern']} ({issue['probability']:.1f}%)")

# ディレクトリ全体をスキャン
results = Forecaster.scan_dir("./src/")
for file_path, issues in results.items():
    print(f"File: {file_path}")
    for issue in issues:
        print(f"  Line {issue['line']}: {issue['pattern']}")

# JSON形式で出力
json_data = Forecaster.to_json(results)
print(json_data)

# HTMLレポートを生成
Forecaster.export_report(results, "report.html", "html")

# Markdownレポートを生成
Forecaster.export_report(results, "report.md", "markdown")
```

## 🔍 検出されるバグパターン

### 1. 可変デフォルト引数 (HIGH - 93.5%)
```python
def bad_function(items=[]):  # ❌ 危険
    items.append("new item")
    return items
```

**改善案:**
```python
def good_function(items=None):  # ✅ 安全
    if items is None:
        items = []
    items.append("new item")
    return items
```

### 2. Bare Except句 (MEDIUM - 80.2%)
```python
try:
    result = 10 / 0
except:  # ❌ 危険
    print("エラーが発生しました")
```

**改善案:**
```python
try:
    result = 10 / 0
except ZeroDivisionError:  # ✅ 安全
    print("ゼロ除算エラーが発生しました")
```

### 3. 未使用インポート (MEDIUM - 70.3%)
```python
import os   # ❌ 未使用
import sys  # ❌ 未使用
import json # ❌ 未使用

def my_function():
    return "Hello"
```

### 4. 変数シャドウイング (LOW - 60.8%)
```python
x = 10
def my_function():
    x = 20  # ❌ 外側のxをシャドウ
    return x
```

### 5. 大きな関数 (MEDIUM - 75.0%)
```python
def large_function():  # ❌ 行数が多すぎる
    # 50行以上のコード...
    pass
```

### 6. 深い再帰 (HIGH - 85.0%)
```python
def recursive_function(n):  # ❌ スタックオーバーフローの危険
    if n <= 0:
        return 1
    return n * recursive_function(n - 1)
```

### 7. 非効率なループ (MEDIUM - 65.0%)
```python
for i in range(100):  # ❌ 非効率
    for j in range(100):
        # 処理...
        pass
```

## 📊 出力例

### テキスト出力
```
21個の問題が見つかりました:

📁 tests/test_sample.py
  🔴 [HIGH] line 13: Mutable default argument
     → Probability: 93.5%
     → Suggestion: Use None as default and initialize inside function
     → Code: def bad_function(items=[]):

  🟡 [MEDIUM] line 85: Bare except clause
     → Probability: 80.2%
     → Suggestion: Specify exception type or use Exception
     → Code: except:  # bare except
```

### JSON出力
```json
{
  "tests/test_sample.py": [
    {
      "line": 13,
      "probability": 93.5,
      "pattern": "Mutable default argument",
      "suggestion": "Use None as default and initialize inside function",
      "snippet": "def bad_function(items=[]):",
      "severity": "HIGH"
    }
  ]
}
```

### HTMLレポート
美しいスタイリング付きのHTMLレポートが生成されます。ブラウザで開いて確認できます。

## 🏗️ プロジェクト構造

```
errorforecaster/
├── core/
│   ├── patterns.py      # パターン検出ロジック
│   ├── model.py         # 統計モデル
│   └── scanner.py       # メインスキャナー
├── report/              # レポート生成モジュール
├── tests/               # テストファイル
├── cli.py              # コマンドラインインターフェース
└── setup.py            # パッケージ設定
```

## 🧪 テスト

```bash
# テストを実行
python -m pytest tests/

# 特定のテストファイルを実行
python tests/test_forecaster.py
```

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## ⭐ スター

このプロジェクトが役立った場合は、⭐を付けてください！

---

**tikisan** - より良いコードを書くための静的解析ツール
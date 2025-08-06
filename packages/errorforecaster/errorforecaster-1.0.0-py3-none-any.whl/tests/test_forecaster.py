"""
Forecasterクラスのテスト
"""

import unittest
import tempfile
import os
from pathlib import Path

try:
    from errorforecaster import Forecaster
except ImportError:
    from core.scanner import Forecaster


class TestForecaster(unittest.TestCase):
    """Forecasterクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_file_content = '''
import os
import sys

def bad_function(items=[]):
    """可変デフォルト引数を使用した悪い例"""
    items.append("new item")
    return items

def good_function(items=None):
    """正しい実装例"""
    if items is None:
        items = []
    items.append("new item")
    return items

def large_function():
    """巨大関数"""
    result = []
    for i in range(100):
        if i % 2 == 0:
            result.append(i)
        else:
            result.append(i * 2)
    return result

def recursive_function(n):
    """再帰関数"""
    if n <= 0:
        return 1
    return n * recursive_function(n - 1)

try:
    result = 10 / 0
except:
    print("エラーが発生しました")
'''
        
        # 一時ファイルを作成
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test_file.py")
        
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(self.test_file_content)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_scan_file(self):
        """ファイルスキャンのテスト"""
        results = Forecaster.scan(self.test_file_path)
        
        # 結果がリストであることを確認
        self.assertIsInstance(results, list)
        
        # 少なくとも1つの問題が見つかることを確認
        self.assertGreater(len(results), 0)
        
        # 結果の構造を確認
        for result in results:
            self.assertIn('line', result)
            self.assertIn('probability', result)
            self.assertIn('pattern', result)
            self.assertIn('suggestion', result)
            self.assertIn('snippet', result)
            self.assertIn('severity', result)
    
    def test_scan_directory(self):
        """ディレクトリスキャンのテスト"""
        results = Forecaster.scan_dir(self.temp_dir)
        
        # 結果が辞書であることを確認
        self.assertIsInstance(results, dict)
        
        # テストファイルが含まれていることを確認
        self.assertIn(self.test_file_path, results)
        
        # ファイルの結果がリストであることを確認
        self.assertIsInstance(results[self.test_file_path], list)
    
    def test_to_json(self):
        """JSON変換のテスト"""
        results = Forecaster.scan(self.test_file_path)
        json_data = Forecaster.to_json({self.test_file_path: results})
        
        # JSON文字列であることを確認
        self.assertIsInstance(json_data, str)
        
        # JSONとして解析可能であることを確認
        import json
        parsed = json.loads(json_data)
        self.assertIsInstance(parsed, dict)
    
    def test_export_report_html(self):
        """HTMLレポート出力のテスト"""
        results = Forecaster.scan(self.test_file_path)
        report_file = os.path.join(self.temp_dir, "report.html")
        
        Forecaster.export_report({self.test_file_path: results}, report_file, "html")
        
        # ファイルが作成されていることを確認
        self.assertTrue(os.path.exists(report_file))
        
        # ファイルサイズが0より大きいことを確認
        self.assertGreater(os.path.getsize(report_file), 0)
    
    def test_export_report_markdown(self):
        """Markdownレポート出力のテスト"""
        results = Forecaster.scan(self.test_file_path)
        report_file = os.path.join(self.temp_dir, "report.md")
        
        Forecaster.export_report({self.test_file_path: results}, report_file, "markdown")
        
        # ファイルが作成されていることを確認
        self.assertTrue(os.path.exists(report_file))
        
        # ファイルサイズが0より大きいことを確認
        self.assertGreater(os.path.getsize(report_file), 0)
    
    def test_file_not_found(self):
        """存在しないファイルのテスト"""
        from core.scanner import FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            Forecaster.scan("nonexistent_file.py")
    
    def test_unsupported_file_type(self):
        """サポートされていないファイルタイプのテスト"""
        from core.scanner import UnsupportedFileTypeError
        unsupported_file = os.path.join(self.temp_dir, "test.txt")
        with open(unsupported_file, 'w') as f:
            f.write("This is not a Python file")
        
        with self.assertRaises(UnsupportedFileTypeError):
            Forecaster.scan(unsupported_file)


if __name__ == '__main__':
    unittest.main() 
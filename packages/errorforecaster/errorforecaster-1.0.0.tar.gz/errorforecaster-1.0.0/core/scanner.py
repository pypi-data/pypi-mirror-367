"""
メインのスキャナー機能
"""

import ast
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from .patterns import PatternDetector
from .model import StatisticalModel


class Forecaster:
    """バグ発生確率解析を行うメインクラス"""
    
    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.statistical_model = StatisticalModel()
    
    @classmethod
    def scan(cls, path: str) -> List[Dict[str, Any]]:
        """単一ファイルを解析し、脆弱ポイント情報を返す"""
        instance = cls()
        return instance._scan_file(path)
    
    @classmethod
    def scan_dir(cls, path: str) -> Dict[str, List[Dict[str, Any]]]:
        """ディレクトリ内のすべてのコードファイルを解析"""
        instance = cls()
        return instance._scan_directory(path)
    
    @classmethod
    def to_json(cls, data: Dict[str, List[Dict[str, Any]]]) -> str:
        """解析結果をJSON形式に変換"""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @classmethod
    def export_report(cls, data: Dict[str, List[Dict[str, Any]]], 
                     file: str, format: str = "html") -> None:
        """解析結果をレポート出力"""
        if format == "html":
            cls._export_html_report(data, file)
        elif format == "markdown":
            cls._export_markdown_report(data, file)
        elif format == "json":
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """単一ファイルをスキャン"""
        try:
            # ファイルの存在確認
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # ファイル拡張子の確認
            if not self._is_supported_file(file_path):
                raise UnsupportedFileTypeError(f"Unsupported file type: {file_path}")
            
            # ファイル読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                source_lines = source_code.splitlines()
            
            # AST解析
            try:
                tree = ast.parse(source_code)
            except SyntaxError as e:
                raise ParseError(f"Syntax error in {file_path}: {e}")
            
            # ファイルコンテキストの分析
            file_context = self.statistical_model.analyze_file_context(source_lines)
            complexity = self.statistical_model.analyze_complexity(tree)
            file_context["complexity"] = complexity
            
            # パターン検出
            results = self.pattern_detector.detect_patterns(tree, source_lines)
            
            # 確率の調整
            for result in results:
                context = file_context.copy()
                context["line_number"] = result["line"]
                
                # パターンタイプを推測（簡易版）
                pattern_type = self._guess_pattern_type(result["pattern"])
                adjusted_prob = self.statistical_model.predict(pattern_type, context)
                result["probability"] = adjusted_prob
            
            return results
            
        except Exception as e:
            raise e
    
    def _scan_directory(self, dir_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """ディレクトリ内のファイルをスキャン"""
        results = {}
        
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        if not os.path.isdir(dir_path):
            raise ValueError(f"Path is not a directory: {dir_path}")
        
        # Pythonファイルを再帰的に検索
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if self._is_supported_file(file):
                    file_path = os.path.join(root, file)
                    try:
                        file_results = self._scan_file(file_path)
                        if file_results:  # 結果がある場合のみ追加
                            results[file_path] = file_results
                    except Exception as e:
                        # エラーが発生しても他のファイルの処理を継続
                        print(f"Error scanning {file_path}: {e}")
        
        return results
    
    def _is_supported_file(self, file_path: str) -> bool:
        """サポートされているファイルかチェック"""
        supported_extensions = {'.py'}
        return Path(file_path).suffix.lower() in supported_extensions
    
    def _guess_pattern_type(self, pattern_name: str) -> str:
        """パターン名からパターンタイプを推測"""
        pattern_mapping = {
            "Mutable default argument": "mutable_default",
            "Bare except clause": "bare_except",
            "Unused import": "unused_import",
            "Variable shadowing": "shadowing",
            "Large function": "large_function",
            "Deep recursion": "deep_recursion",
            "Inefficient loop": "inefficient_loop"
        }
        return pattern_mapping.get(pattern_name, "unknown")
    
    @classmethod
    def _export_html_report(cls, data: Dict[str, List[Dict[str, Any]]], file: str) -> None:
        """HTMLレポートを出力"""
        html_content = cls._generate_html_report(data)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    @classmethod
    def _export_markdown_report(cls, data: Dict[str, List[Dict[str, Any]]], file: str) -> None:
        """Markdownレポートを出力"""
        md_content = cls._generate_markdown_report(data)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    @classmethod
    def _generate_html_report(cls, data: Dict[str, List[Dict[str, Any]]]) -> str:
        """HTMLレポートを生成"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>ErrorForecaster Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .file { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; }
        .file h2 { color: #333; border-bottom: 2px solid #007acc; }
        .issue { margin: 10px 0; padding: 10px; border-left: 4px solid #ff6b6b; background: #f8f9fa; }
        .high { border-left-color: #ff6b6b; }
        .medium { border-left-color: #ffd93d; }
        .low { border-left-color: #6bcf7f; }
        .probability { font-weight: bold; color: #007acc; }
        .suggestion { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <h1>ErrorForecaster Analysis Report</h1>
"""
        
        for file_path, issues in data.items():
            html += f'<div class="file">\n'
            html += f'<h2>{file_path}</h2>\n'
            
            if not issues:
                html += '<p>No issues found.</p>\n'
            else:
                for issue in issues:
                    severity_class = issue.get("severity", "medium").lower()
                    html += f'<div class="issue {severity_class}">\n'
                    html += f'<strong>Line {issue["line"]}: {issue["pattern"]}</strong><br>\n'
                    html += f'<span class="probability">Probability: {issue["probability"]:.1f}%</span><br>\n'
                    html += f'<span class="suggestion">Suggestion: {issue["suggestion"]}</span><br>\n'
                    html += f'<code>{issue["snippet"]}</code>\n'
                    html += '</div>\n'
            
            html += '</div>\n'
        
        html += """
</body>
</html>
"""
        return html
    
    @classmethod
    def _generate_markdown_report(cls, data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Markdownレポートを生成"""
        md = "# ErrorForecaster Analysis Report\n\n"
        
        for file_path, issues in data.items():
            md += f"## {file_path}\n\n"
            
            if not issues:
                md += "No issues found.\n\n"
            else:
                for issue in issues:
                    severity = issue.get("severity", "MEDIUM")
                    md += f"### [{severity}] Line {issue['line']}: {issue['pattern']}\n\n"
                    md += f"- **Probability:** {issue['probability']:.1f}%\n"
                    md += f"- **Suggestion:** {issue['suggestion']}\n"
                    md += f"- **Code:** `{issue['snippet']}`\n\n"
        
        return md


class FileNotFoundError(Exception):
    """ファイルが見つからない場合の例外"""
    pass


class UnsupportedFileTypeError(Exception):
    """サポートされていないファイルタイプの場合の例外"""
    pass


class ParseError(Exception):
    """構文解析エラーの場合の例外"""
    pass 
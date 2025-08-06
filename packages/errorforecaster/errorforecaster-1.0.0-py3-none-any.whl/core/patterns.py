"""
バグパターンの定義と検出ロジック
"""

import ast
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class BugPattern:
    """バグパターンの定義"""
    name: str
    description: str
    probability: float
    suggestion: str
    severity: str  # "LOW", "MEDIUM", "HIGH"


class PatternDetector:
    """バグパターンの検出器"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, BugPattern]:
        """バグパターンの初期化"""
        return {
            "mutable_default": BugPattern(
                name="Mutable default argument",
                description="可変オブジェクトをデフォルト引数として使用",
                probability=78.5,
                suggestion="Use None as default and initialize inside function",
                severity="HIGH"
            ),
            "bare_except": BugPattern(
                name="Bare except clause",
                description="例外の種類を指定しないexcept文",
                probability=65.2,
                suggestion="Specify exception type or use Exception",
                severity="MEDIUM"
            ),
            "unused_import": BugPattern(
                name="Unused import",
                description="使用されていないインポート",
                probability=55.3,
                suggestion="Remove unused imports",
                severity="MEDIUM"
            ),
            "shadowing": BugPattern(
                name="Variable shadowing",
                description="変数のシャドーイング",
                probability=45.8,
                suggestion="Use different variable names",
                severity="LOW"
            ),
            "large_function": BugPattern(
                name="Large function",
                description="行数が多すぎる関数",
                probability=60.0,
                suggestion="Break down into smaller functions",
                severity="MEDIUM"
            ),
            "deep_recursion": BugPattern(
                name="Deep recursion",
                description="深い再帰呼び出し",
                probability=70.0,
                suggestion="Consider iterative approach",
                severity="HIGH"
            ),
            "inefficient_loop": BugPattern(
                name="Inefficient loop",
                description="非効率なループ構造",
                probability=50.0,
                suggestion="Consider using list comprehension or generator",
                severity="MEDIUM"
            )
        }
    
    def detect_patterns(self, tree: ast.AST, source_lines: List[str]) -> List[Dict[str, Any]]:
        """ASTからバグパターンを検出"""
        results = []
        
        # 各パターンの検出を実行
        results.extend(self._detect_mutable_defaults(tree, source_lines))
        results.extend(self._detect_bare_excepts(tree, source_lines))
        results.extend(self._detect_unused_imports(tree, source_lines))
        results.extend(self._detect_variable_shadowing(tree, source_lines))
        results.extend(self._detect_large_functions(tree, source_lines))
        results.extend(self._detect_deep_recursion(tree, source_lines))
        results.extend(self._detect_inefficient_loops(tree, source_lines))
        
        return results
    
    def _detect_mutable_defaults(self, tree: ast.AST, source_lines: List[str]) -> List[Dict[str, Any]]:
        """可変デフォルト引数の検出"""
        results = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for arg in node.args.defaults:
                    if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                        line_num = node.lineno
                        pattern = self.patterns["mutable_default"]
                        
                        # 関数定義行のスニペットを取得
                        snippet = source_lines[line_num - 1].strip()
                        
                        results.append({
                            "line": line_num,
                            "probability": pattern.probability,
                            "pattern": pattern.name,
                            "suggestion": pattern.suggestion,
                            "snippet": snippet,
                            "severity": pattern.severity
                        })
        
        return results
    
    def _detect_bare_excepts(self, tree: ast.AST, source_lines: List[str]) -> List[Dict[str, Any]]:
        """bare except文の検出"""
        results = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    if handler.type is None:  # bare except
                        line_num = handler.lineno
                        pattern = self.patterns["bare_except"]
                        
                        snippet = source_lines[line_num - 1].strip()
                        
                        results.append({
                            "line": line_num,
                            "probability": pattern.probability,
                            "pattern": pattern.name,
                            "suggestion": pattern.suggestion,
                            "snippet": snippet,
                            "severity": pattern.severity
                        })
        
        return results
    
    def _detect_unused_imports(self, tree: ast.AST, source_lines: List[str]) -> List[Dict[str, Any]]:
        """未使用インポートの検出（簡易版）"""
        results = []
        
        # 実際の実装では、より複雑な解析が必要
        # ここでは簡易的にimport文を検出
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    line_num = node.lineno
                    pattern = self.patterns["unused_import"]
                    
                    snippet = source_lines[line_num - 1].strip()
                    
                    results.append({
                        "line": line_num,
                        "probability": pattern.probability,
                        "pattern": pattern.name,
                        "suggestion": pattern.suggestion,
                        "snippet": snippet,
                        "severity": pattern.severity
                    })
        
        return results
    
    def _detect_variable_shadowing(self, tree: ast.AST, source_lines: List[str]) -> List[Dict[str, Any]]:
        """変数シャドーイングの検出（簡易版）"""
        results = []
        
        # 実際の実装では、スコープ解析が必要
        # ここでは簡易的に変数代入を検出
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                line_num = node.lineno
                pattern = self.patterns["shadowing"]
                
                snippet = source_lines[line_num - 1].strip()
                
                results.append({
                    "line": line_num,
                    "probability": pattern.probability,
                    "pattern": pattern.name,
                    "suggestion": pattern.suggestion,
                    "snippet": snippet,
                    "severity": pattern.severity
                })
        
        return results
    
    def _detect_large_functions(self, tree: ast.AST, source_lines: List[str]) -> List[Dict[str, Any]]:
        """巨大関数の検出"""
        results = []
        threshold = 50  # 50行以上の関数を巨大とみなす
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 関数の行数を計算
                start_line = node.lineno
                end_line = self._get_node_end_line(node, source_lines)
                function_lines = end_line - start_line + 1
                
                if function_lines > threshold:
                    pattern = self.patterns["large_function"]
                    
                    snippet = source_lines[start_line - 1].strip()
                    
                    results.append({
                        "line": start_line,
                        "probability": pattern.probability,
                        "pattern": pattern.name,
                        "suggestion": pattern.suggestion,
                        "snippet": snippet,
                        "severity": pattern.severity
                    })
        
        return results
    
    def _detect_deep_recursion(self, tree: ast.AST, source_lines: List[str]) -> List[Dict[str, Any]]:
        """深い再帰の検出（簡易版）"""
        results = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 関数内で自分自身を呼び出しているかチェック
                if self._has_self_call(node, node.name):
                    line_num = node.lineno
                    pattern = self.patterns["deep_recursion"]
                    
                    snippet = source_lines[line_num - 1].strip()
                    
                    results.append({
                        "line": line_num,
                        "probability": pattern.probability,
                        "pattern": pattern.name,
                        "suggestion": pattern.suggestion,
                        "snippet": snippet,
                        "severity": pattern.severity
                    })
        
        return results
    
    def _detect_inefficient_loops(self, tree: ast.AST, source_lines: List[str]) -> List[Dict[str, Any]]:
        """非効率なループの検出（簡易版）"""
        results = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # ネストしたループを検出
                if self._has_nested_loop(node):
                    line_num = node.lineno
                    pattern = self.patterns["inefficient_loop"]
                    
                    snippet = source_lines[line_num - 1].strip()
                    
                    results.append({
                        "line": line_num,
                        "probability": pattern.probability,
                        "pattern": pattern.name,
                        "suggestion": pattern.suggestion,
                        "snippet": snippet,
                        "severity": pattern.severity
                    })
        
        return results
    
    def _get_node_end_line(self, node: ast.AST, source_lines: List[str]) -> int:
        """ノードの終了行を取得"""
        # 簡易実装：実際はより正確な計算が必要
        return node.lineno + 10  # 仮の実装
    
    def _has_self_call(self, node: ast.FunctionDef, func_name: str) -> bool:
        """関数内で自分自身を呼び出しているかチェック"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id == func_name:
                    return True
        return False
    
    def _has_nested_loop(self, node: ast.For) -> bool:
        """ネストしたループがあるかチェック"""
        for child in ast.walk(node):
            if isinstance(child, ast.For) and child != node:
                return True
        return False 
"""
統計モデルとヒューリスティックルール
"""

from typing import List, Dict, Any
import ast


class HeuristicModel:
    """ヒューリスティックベースの統計モデル"""
    
    def __init__(self):
        self.base_probabilities = {
            "mutable_default": 78.5,
            "bare_except": 65.2,
            "unused_import": 55.3,
            "shadowing": 45.8,
            "large_function": 60.0,
            "deep_recursion": 70.0,
            "inefficient_loop": 50.0
        }
    
    def calculate_probability(self, pattern_type: str, context: Dict[str, Any]) -> float:
        """パターンタイプとコンテキストに基づいて確率を計算"""
        base_prob = self.base_probabilities.get(pattern_type, 50.0)
        
        # コンテキストに基づく調整
        adjusted_prob = self._adjust_probability(base_prob, context)
        
        # 0-100の範囲に制限
        return max(0.0, min(100.0, adjusted_prob))
    
    def _adjust_probability(self, base_prob: float, context: Dict[str, Any]) -> float:
        """コンテキストに基づいて確率を調整"""
        adjusted = base_prob
        
        # 関数の複雑度による調整
        if "complexity" in context:
            complexity = context["complexity"]
            if complexity > 10:
                adjusted += 10
            elif complexity < 3:
                adjusted -= 10
        
        # ファイルサイズによる調整
        if "file_size" in context:
            file_size = context["file_size"]
            if file_size > 1000:
                adjusted += 5
            elif file_size < 100:
                adjusted -= 5
        
        # 行番号による調整（ファイルの後半ほど確率が高くなる）
        if "line_number" in context and "total_lines" in context:
            line_ratio = context["line_number"] / context["total_lines"]
            if line_ratio > 0.8:
                adjusted += 5
        
        return adjusted


class StatisticalModel:
    """統計モデル（将来的な拡張用）"""
    
    def __init__(self):
        self.heuristic_model = HeuristicModel()
        # 将来的にscikit-learnモデルを追加予定
    
    def predict(self, pattern_type: str, context: Dict[str, Any]) -> float:
        """パターンの確率を予測"""
        # 現在はヒューリスティックモデルを使用
        return self.heuristic_model.calculate_probability(pattern_type, context)
    
    def analyze_complexity(self, tree: ast.AST) -> int:
        """ASTの複雑度を分析"""
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 2
            elif isinstance(node, ast.ClassDef):
                complexity += 3
        
        return complexity
    
    def analyze_file_context(self, source_lines: List[str]) -> Dict[str, Any]:
        """ファイルのコンテキスト情報を分析"""
        return {
            "total_lines": len(source_lines),
            "file_size": len("".join(source_lines)),
            "has_docstring": any(line.strip().startswith('"""') for line in source_lines[:10]),
            "has_comments": any(line.strip().startswith('#') for line in source_lines)
        } 
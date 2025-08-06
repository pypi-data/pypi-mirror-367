"""
テスト用のサンプルファイル - 様々なバグパターンを含む
"""

import os
import sys

# 未使用インポート
import json
import time

# 可変デフォルト引数の例
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

# 巨大関数の例
def large_function():
    """50行を超える巨大関数"""
    result = []
    for i in range(100):
        if i % 2 == 0:
            result.append(i)
        else:
            result.append(i * 2)
    
    # さらに多くの処理を追加
    for i in range(50):
        if i % 3 == 0:
            result.append(i * 3)
        elif i % 5 == 0:
            result.append(i * 5)
        else:
            result.append(i)
    
    # さらに処理を追加
    for i in range(25):
        if i % 7 == 0:
            result.append(i * 7)
        elif i % 11 == 0:
            result.append(i * 11)
        else:
            result.append(i)
    
    return result

# 深い再帰の例
def recursive_function(n):
    """深い再帰呼び出し"""
    if n <= 0:
        return 1
    return n * recursive_function(n - 1)

# 非効率なループの例
def inefficient_loop():
    """ネストしたループ"""
    result = []
    for i in range(100):
        for j in range(100):
            for k in range(10):
                result.append(i + j + k)
    return result

# シャドーイングの例
def shadowing_example():
    """変数シャドーイング"""
    x = 10
    for x in range(5):  # 外側のxをシャドー
        print(x)
    return x

# bare exceptの例
def bad_exception_handling():
    """例外の種類を指定しないexcept"""
    try:
        result = 10 / 0
    except:  # bare except
        print("エラーが発生しました")

def good_exception_handling():
    """正しい例外処理"""
    try:
        result = 10 / 0
    except ZeroDivisionError:
        print("ゼロ除算エラーが発生しました")
    except Exception as e:
        print(f"その他のエラー: {e}")

# メイン処理
if __name__ == "__main__":
    # テスト実行
    print("テスト実行中...")
    
    # 可変デフォルト引数のテスト
    result1 = bad_function()
    result2 = bad_function()
    print(f"可変デフォルト引数の結果: {result1}, {result2}")
    
    # 巨大関数のテスト
    large_result = large_function()
    print(f"巨大関数の結果: {len(large_result)}個の要素")
    
    # 再帰関数のテスト
    try:
        recursive_result = recursive_function(5)
        print(f"再帰関数の結果: {recursive_result}")
    except RecursionError:
        print("再帰深度エラーが発生しました")
    
    # 非効率ループのテスト
    inefficient_result = inefficient_loop()
    print(f"非効率ループの結果: {len(inefficient_result)}個の要素")
    
    # シャドーイングのテスト
    shadowing_result = shadowing_example()
    print(f"シャドーイングの結果: {shadowing_result}")
    
    # 例外処理のテスト
    bad_exception_handling()
    good_exception_handling()
    
    print("テスト完了") 
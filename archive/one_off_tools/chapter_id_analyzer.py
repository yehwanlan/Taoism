#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章節ID分析器 - 智能識別章節ID模式並採用對應策略

根據章節ID的特徵（數字序列 vs 隨機字符串）來決定最佳的子章節發現策略
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

sys.path.append(str(Path(__file__).parent.parent))
from core.unicode_handler import safe_print

@dataclass
class ChapterIdPattern:
    """章節ID模式分析結果"""
    pattern_type: str  # 'sequential', 'random', 'mixed', 'unknown'
    confidence: float  # 0.0 - 1.0
    characteristics: Dict
    recommended_strategy: str

class ChapterIdAnalyzer:
    """章節ID分析器"""
    
    def __init__(self):
        self.patterns = {
            'sequential_numeric': r'^\d+$',  # 純數字
            'sequential_prefixed': r'^[a-zA-Z]+\d+$',  # 字母+數字
            'sequential_suffixed': r'^\d+[a-zA-Z]+$',  # 數字+字母
            'random_string': r'^[a-zA-Z0-9]{8,}$',  # 長隨機字符串
            'uuid_like': r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',  # UUID格式
            'hash_like': r'^[a-f0-9]{32,}$',  # Hash格式
            'mixed_pattern': r'^[a-zA-Z0-9]+$'  # 混合模式
        }
    
    def analyze_chapter_ids(self, chapters: List[Dict]) -> ChapterIdPattern:
        """分析章節ID列表，識別模式"""
        safe_print("🔍 分析章節ID模式...")
        
        if not chapters:
            return ChapterIdPattern('unknown', 0.0, {}, 'default')
        
        chapter_ids = [ch.get('chapter_id', '') for ch in chapters if ch.get('chapter_id')]
        
        if not chapter_ids:
            return ChapterIdPattern('unknown', 0.0, {}, 'default')
        
        safe_print(f"📊 分析 {len(chapter_ids)} 個章節ID")
        
        # 分析每個ID的特徵
        analysis_results = []
        for chapter_id in chapter_ids:
            result = self._analyze_single_id(chapter_id)
            analysis_results.append(result)
        
        # 統計模式分布
        pattern_counts = {}
        for result in analysis_results:
            pattern = result['primary_pattern']
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # 確定主要模式
        total_ids = len(chapter_ids)
        dominant_pattern = max(pattern_counts.items(), key=lambda x: x[1])
        confidence = dominant_pattern[1] / total_ids
        
        safe_print(f"📋 模式分析結果:")
        for pattern, count in pattern_counts.items():
            percentage = (count / total_ids) * 100
            safe_print(f"   {pattern}: {count} 個 ({percentage:.1f}%)")
        
        safe_print(f"🎯 主要模式: {dominant_pattern[0]} (信心度: {confidence:.2f})")
        
        # 生成特徵分析
        characteristics = self._generate_characteristics(chapter_ids, analysis_results)
        
        # 推薦策略
        strategy = self._recommend_strategy(dominant_pattern[0], confidence, characteristics)
        
        return ChapterIdPattern(
            pattern_type=dominant_pattern[0],
            confidence=confidence,
            characteristics=characteristics,
            recommended_strategy=strategy
        )
    
    def _analyze_single_id(self, chapter_id: str) -> Dict:
        """分析單個章節ID"""
        result = {
            'id': chapter_id,
            'length': len(chapter_id),
            'has_numbers': bool(re.search(r'\d', chapter_id)),
            'has_letters': bool(re.search(r'[a-zA-Z]', chapter_id)),
            'has_special': bool(re.search(r'[^a-zA-Z0-9]', chapter_id)),
            'numeric_ratio': len(re.findall(r'\d', chapter_id)) / len(chapter_id),
            'letter_ratio': len(re.findall(r'[a-zA-Z]', chapter_id)) / len(chapter_id),
            'patterns_matched': []
        }
        
        # 檢查匹配的模式
        for pattern_name, pattern_regex in self.patterns.items():
            if re.match(pattern_regex, chapter_id):
                result['patterns_matched'].append(pattern_name)
        
        # 確定主要模式
        if result['patterns_matched']:
            # 優先級排序
            priority_order = [
                'sequential_numeric', 'sequential_prefixed', 'sequential_suffixed',
                'uuid_like', 'hash_like', 'random_string', 'mixed_pattern'
            ]
            
            for pattern in priority_order:
                if pattern in result['patterns_matched']:
                    result['primary_pattern'] = pattern
                    break
        else:
            result['primary_pattern'] = 'unknown'
        
        return result
    
    def _generate_characteristics(self, chapter_ids: List[str], analysis_results: List[Dict]) -> Dict:
        """生成整體特徵分析"""
        characteristics = {
            'total_count': len(chapter_ids),
            'avg_length': sum(len(id) for id in chapter_ids) / len(chapter_ids),
            'min_length': min(len(id) for id in chapter_ids),
            'max_length': max(len(id) for id in chapter_ids),
            'has_consistent_length': len(set(len(id) for id in chapter_ids)) == 1,
            'all_numeric': all(result['primary_pattern'] == 'sequential_numeric' for result in analysis_results),
            'all_random': all(result['primary_pattern'] == 'random_string' for result in analysis_results),
            'mixed_types': len(set(result['primary_pattern'] for result in analysis_results)) > 1
        }
        
        # 檢查序列性
        if characteristics['all_numeric']:
            numeric_ids = [int(id) for id in chapter_ids if id.isdigit()]
            if numeric_ids:
                numeric_ids.sort()
                is_sequential = all(numeric_ids[i] == numeric_ids[i-1] + 1 for i in range(1, len(numeric_ids)))
                characteristics['is_sequential'] = is_sequential
                characteristics['sequence_gaps'] = not is_sequential
        
        return characteristics
    
    def _recommend_strategy(self, pattern_type: str, confidence: float, characteristics: Dict) -> str:
        """根據分析結果推薦發現策略"""
        
        if confidence < 0.5:
            return 'hybrid_strategy'  # 混合策略
        
        strategy_map = {
            'sequential_numeric': 'numeric_sequence_strategy',
            'sequential_prefixed': 'prefixed_sequence_strategy', 
            'sequential_suffixed': 'suffixed_sequence_strategy',
            'random_string': 'structure_based_strategy',
            'uuid_like': 'structure_based_strategy',
            'hash_like': 'structure_based_strategy',
            'mixed_pattern': 'adaptive_strategy',
            'unknown': 'default_strategy'
        }
        
        base_strategy = strategy_map.get(pattern_type, 'default_strategy')
        
        # 根據特徵調整策略
        if characteristics.get('mixed_types', False):
            return 'hybrid_strategy'
        
        if pattern_type in ['random_string', 'uuid_like', 'hash_like']:
            return 'structure_based_strategy'  # 使用我們現有的智能結構分析
        
        return base_strategy
    
    def get_discovery_recommendations(self, pattern: ChapterIdPattern) -> Dict:
        """獲取發現策略的具體建議"""
        recommendations = {
            'strategy': pattern.recommended_strategy,
            'confidence': pattern.confidence,
            'methods': [],
            'fallback_methods': [],
            'special_considerations': []
        }
        
        if pattern.pattern_type == 'sequential_numeric':
            recommendations['methods'] = [
                'numeric_increment_probing',
                'range_scanning',
                'gap_detection'
            ]
            recommendations['fallback_methods'] = ['structure_based_discovery']
            recommendations['special_considerations'] = [
                '可以嘗試數字遞增探測',
                '注意可能的序列間隙',
                '檢查是否有跳號'
            ]
        
        elif pattern.pattern_type in ['random_string', 'uuid_like', 'hash_like']:
            recommendations['methods'] = [
                'structure_based_discovery',
                'catalog_tree_analysis',
                'level_hierarchy_detection'
            ]
            recommendations['fallback_methods'] = ['content_pattern_matching']
            recommendations['special_considerations'] = [
                '依賴頁面結構分析',
                '使用目錄樹層級關係',
                '無法進行ID模式預測'
            ]
        
        elif pattern.pattern_type in ['sequential_prefixed', 'sequential_suffixed']:
            recommendations['methods'] = [
                'pattern_based_increment',
                'prefix_suffix_analysis',
                'structure_based_discovery'
            ]
            recommendations['fallback_methods'] = ['hybrid_approach']
            recommendations['special_considerations'] = [
                '分析前綴/後綴模式',
                '結合結構分析',
                '可能需要混合策略'
            ]
        
        else:  # mixed_pattern, unknown
            recommendations['methods'] = [
                'adaptive_discovery',
                'multiple_strategy_testing',
                'structure_based_discovery'
            ]
            recommendations['fallback_methods'] = ['manual_inspection']
            recommendations['special_considerations'] = [
                '需要自適應策略',
                '測試多種方法',
                '可能需要人工檢查'
            ]
        
        return recommendations

def test_chapter_id_analyzer():
    """測試章節ID分析器"""
    safe_print("🧪 測試章節ID分析器")
    safe_print("=" * 50)
    
    analyzer = ChapterIdAnalyzer()
    
    # 測試案例1: 數字序列
    safe_print("\n📋 測試案例1: 數字序列")
    numeric_chapters = [
        {'chapter_id': '1', 'title': '第一章'},
        {'chapter_id': '2', 'title': '第二章'},
        {'chapter_id': '3', 'title': '第三章'},
        {'chapter_id': '5', 'title': '第五章'},  # 有間隙
    ]
    
    pattern1 = analyzer.analyze_chapter_ids(numeric_chapters)
    recommendations1 = analyzer.get_discovery_recommendations(pattern1)
    
    safe_print(f"模式類型: {pattern1.pattern_type}")
    safe_print(f"推薦策略: {pattern1.recommended_strategy}")
    safe_print(f"建議方法: {', '.join(recommendations1['methods'])}")
    
    # 測試案例2: 隨機字符串（如DZ0735的情況）
    safe_print("\n📋 測試案例2: 隨機字符串")
    random_chapters = [
        {'chapter_id': '1k1r7oqmxh8uz', 'title': '庄子口义发题'},
        {'chapter_id': '1k1r7pcj7a2wi', 'title': '南华真经口义卷之一'},
        {'chapter_id': '1k1r7pdhjf8kb', 'title': '南华真经口义卷之二'},
        {'chapter_id': '1k1ro1wu1qwiu', 'title': '南华真经口义卷之三十一'},
    ]
    
    pattern2 = analyzer.analyze_chapter_ids(random_chapters)
    recommendations2 = analyzer.get_discovery_recommendations(pattern2)
    
    safe_print(f"模式類型: {pattern2.pattern_type}")
    safe_print(f"推薦策略: {pattern2.recommended_strategy}")
    safe_print(f"建議方法: {', '.join(recommendations2['methods'])}")
    safe_print(f"特殊考慮: {recommendations2['special_considerations']}")
    
    # 測試案例3: 混合模式
    safe_print("\n📋 測試案例3: 混合模式")
    mixed_chapters = [
        {'chapter_id': '1', 'title': '序言'},
        {'chapter_id': 'ch001', 'title': '第一章'},
        {'chapter_id': '1k1r7oqmxh8uz', 'title': '特殊章節'},
        {'chapter_id': 'appendix', 'title': '附錄'},
    ]
    
    pattern3 = analyzer.analyze_chapter_ids(mixed_chapters)
    recommendations3 = analyzer.get_discovery_recommendations(pattern3)
    
    safe_print(f"模式類型: {pattern3.pattern_type}")
    safe_print(f"推薦策略: {pattern3.recommended_strategy}")
    safe_print(f"建議方法: {', '.join(recommendations3['methods'])}")

if __name__ == "__main__":
    test_chapter_id_analyzer()
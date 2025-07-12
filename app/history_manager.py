# -*- coding: utf-8 -*-

# @autor: History Feature Extension
# 历史记录管理器

import json
import os
from datetime import datetime
from typing import List, Dict, Any

class HistoryManager:
    """历史记录管理器类，负责计算历史的存储、读取和管理"""
    
    def __init__(self, history_file: str = './app/settings/history.json'):
        self.history_file = history_file
        self.max_history = 100  # 最大历史记录数
        self.history_data = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('calculations', [])
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_history(self) -> None:
        """保存历史记录到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            history_json = {
                'calculations': self.history_data,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_json, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def add_calculation(self, expression: str, result: str) -> None:
        """添加新的计算记录"""
        if expression and result and result != 'Erro':
            calculation = {
                'id': len(self.history_data) + 1,
                'expression': expression,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'date_formatted': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 添加到历史记录开头
            self.history_data.insert(0, calculation)
            
            # 限制历史记录数量
            if len(self.history_data) > self.max_history:
                self.history_data = self.history_data[:self.max_history]
            
            self._save_history()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取历史记录列表"""
        return self.history_data.copy()
    
    def get_recent_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取最近的历史记录"""
        return self.history_data[:count]
    
    def clear_history(self) -> None:
        """清空历史记录"""
        self.history_data.clear()
        self._save_history()
    
    def delete_calculation(self, calc_id: int) -> bool:
        """删除指定的计算记录"""
        original_length = len(self.history_data)
        self.history_data = [calc for calc in self.history_data if calc.get('id') != calc_id]
        
        if len(self.history_data) < original_length:
            self._save_history()
            return True
        return False
    
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """搜索历史记录"""
        if not query:
            return self.history_data
        
        query = query.lower()
        filtered_history = []
        
        for calc in self.history_data:
            if (query in calc['expression'].lower() or 
                query in str(calc['result']).lower() or
                query in calc['date_formatted'].lower()):
                filtered_history.append(calc)
        
        return filtered_history
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取历史记录统计信息"""
        total_calculations = len(self.history_data)
        
        if total_calculations == 0:
            return {
                'total_calculations': 0,
                'most_recent': None,
                'oldest': None
            }
        
        return {
            'total_calculations': total_calculations,
            'most_recent': self.history_data[0]['date_formatted'] if self.history_data else None,
            'oldest': self.history_data[-1]['date_formatted'] if self.history_data else None
        }
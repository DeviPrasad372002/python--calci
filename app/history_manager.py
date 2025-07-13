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
        try:
            self.history_data = self._load_history()
        except Exception as e:
            print(f"历史记录初始化失败: {e}")
            self.history_data = []
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 验证数据格式
                    calculations = data.get('calculations', [])
                    if isinstance(calculations, list):
                        # 验证每个计算记录的格式
                        valid_calculations = []
                        for calc in calculations:
                            if (isinstance(calc, dict) and 
                                'expression' in calc and 
                                'result' in calc and
                                'timestamp' in calc):
                                valid_calculations.append(calc)
                        return valid_calculations
            return []
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"加载历史记录失败: {e}")
            return []
    
    def _save_history(self) -> None:
        """保存历史记录到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            history_json = {
                'calculations': self.history_data,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'  # 添加版本信息
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_json, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def add_calculation(self, expression: str, result: str) -> None:
        """添加新的计算记录"""
        # 验证输入参数
        if not expression or not result or result == 'Erro':
            return
            
        # 避免重复记录相同的计算
        if (self.history_data and 
            len(self.history_data) > 0 and
            self.history_data[0].get('expression') == expression and
            self.history_data[0].get('result') == result):
            return
            
        try:
            # 生成唯一ID
            new_id = max([calc.get('id', 0) for calc in self.history_data], default=0) + 1
            
            calculation = {
                'id': new_id,
                'expression': str(expression).strip(),
                'result': str(result).strip(),
                'timestamp': datetime.now().isoformat(),
                'date_formatted': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 添加到历史记录开头
            self.history_data.insert(0, calculation)
            
            # 限制历史记录数量
            if len(self.history_data) > self.max_history:
                self.history_data = self.history_data[:self.max_history]
            
            self._save_history()
        except Exception as e:
            print(f"添加计算记录失败: {e}")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取历史记录列表"""
        try:
            return self.history_data.copy()
        except Exception as e:
            print(f"获取历史记录失败: {e}")
            return []
    
    def get_recent_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取最近的历史记录"""
        try:
            count = max(1, min(count, len(self.history_data)))  # 确保count在有效范围内
            return self.history_data[:count]
        except Exception as e:
            print(f"获取最近历史记录失败: {e}")
            return []
    
    def clear_history(self) -> None:
        """清空历史记录"""
        try:
            self.history_data.clear()
            self._save_history()
        except Exception as e:
            print(f"清空历史记录失败: {e}")
    
    def delete_calculation(self, calc_id: int) -> bool:
        """删除指定的计算记录"""
        try:
            original_length = len(self.history_data)
            self.history_data = [calc for calc in self.history_data 
                               if calc.get('id') != calc_id]
            
            if len(self.history_data) < original_length:
                self._save_history()
                return True
            return False
        except Exception as e:
            print(f"删除计算记录失败: {e}")
            return False
    
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """搜索历史记录"""
        try:
            if not query or not isinstance(query, str):
                return self.history_data
            
            query = query.lower().strip()
            if not query:
                return self.history_data
            
            filtered_history = []
            
            for calc in self.history_data:
                try:
                    if (query in str(calc.get('expression', '')).lower() or 
                        query in str(calc.get('result', '')).lower() or
                        query in str(calc.get('date_formatted', '')).lower()):
                        filtered_history.append(calc)
                except (TypeError, AttributeError):
                    continue  # 跳过格式错误的记录
            
            return filtered_history
        except Exception as e:
            print(f"搜索历史记录失败: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取历史记录统计信息"""
        try:
            total_calculations = len(self.history_data)
            
            if total_calculations == 0:
                return {
                    'total_calculations': 0,
                    'most_recent': None,
                    'oldest': None
                }
            
            return {
                'total_calculations': total_calculations,
                'most_recent': self.history_data[0].get('date_formatted') if self.history_data else None,
                'oldest': self.history_data[-1].get('date_formatted') if self.history_data else None
            }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {
                'total_calculations': 0,
                'most_recent': None,
                'oldest': None
            }
    
    def validate_data_integrity(self) -> bool:
        """验证数据完整性"""
        try:
            if not isinstance(self.history_data, list):
                return False
                
            for calc in self.history_data:
                if not isinstance(calc, dict):
                    return False
                if not all(key in calc for key in ['id', 'expression', 'result', 'timestamp']):
                    return False
                    
            return True
        except Exception:
            return False
    
    def repair_data(self) -> bool:
        """修复损坏的数据"""
        try:
            if not self.validate_data_integrity():
                # 尝试重新加载数据
                self.history_data = self._load_history()
                
                # 如果仍然无效，创建新的空数据
                if not self.validate_data_integrity():
                    self.history_data = []
                    self._save_history()
                    return True
                    
            return True
        except Exception as e:
            print(f"修复数据失败: {e}")
            self.history_data = []
            return False
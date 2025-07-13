# -*- coding: utf-8 -*-

# @author: History Feature Extension
# History record manager

import json
import os
from datetime import datetime
from typing import List, Dict, Any

class HistoryManager:
    """History manager class, responsible for storing, reading and managing calculation history"""
    
    def __init__(self, history_file: str = './app/settings/history.json'):
        self.history_file = history_file
        self.max_history = 100  # Maximum history records
        try:
            self.history_data = self._load_history()
        except Exception as e:
            print(f"History initialization failed: {e}")
            self.history_data = []
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load history records"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validate data format
                    calculations = data.get('calculations', [])
                    if isinstance(calculations, list):
                        # Validate each calculation record format
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
            print(f"Failed to load history: {e}")
            return []
    
    def _save_history(self) -> None:
        """Save history to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            history_json = {
                'calculations': self.history_data,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'  # Add version information
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_json, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save history: {e}")
    
    def add_calculation(self, expression: str, result: str) -> None:
        """Add new calculation record"""
        # Validate input parameters
        if not expression or not result or result == 'Error':
            return
            
        # Avoid duplicate records of same calculation
        if (self.history_data and 
            len(self.history_data) > 0 and
            self.history_data[0].get('expression') == expression and
            self.history_data[0].get('result') == result):
            return
            
        try:
            # Generate unique ID
            new_id = max([calc.get('id', 0) for calc in self.history_data], default=0) + 1
            
            calculation = {
                'id': new_id,
                'expression': str(expression).strip(),
                'result': str(result).strip(),
                'timestamp': datetime.now().isoformat(),
                'date_formatted': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add to beginning of history
            self.history_data.insert(0, calculation)
            
            # Limit history count
            if len(self.history_data) > self.max_history:
                self.history_data = self.history_data[:self.max_history]
            
            self._save_history()
        except Exception as e:
            print(f"Failed to add calculation record: {e}")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get history list"""
        try:
            return self.history_data.copy()
        except Exception as e:
            print(f"Failed to get history: {e}")
            return []
    
    def get_recent_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent history records"""
        try:
            count = max(1, min(count, len(self.history_data)))  # Ensure count is in valid range
            return self.history_data[:count]
        except Exception as e:
            print(f"Failed to get recent history: {e}")
            return []
    
    def clear_history(self) -> None:
        """Clear all history"""
        try:
            self.history_data.clear()
            self._save_history()
        except Exception as e:
            print(f"Failed to clear history: {e}")
    
    def delete_calculation(self, calc_id: int) -> bool:
        """Delete specified calculation record"""
        try:
            original_length = len(self.history_data)
            self.history_data = [calc for calc in self.history_data 
                               if calc.get('id') != calc_id]
            
            if len(self.history_data) < original_length:
                self._save_history()
                return True
            return False
        except Exception as e:
            print(f"Failed to delete calculation record: {e}")
            return False
    
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """Search history records"""
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
                    continue  # Skip records with format errors
            
            return filtered_history
        except Exception as e:
            print(f"Failed to search history: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics"""
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
            print(f"Failed to get statistics: {e}")
            return {
                'total_calculations': 0,
                'most_recent': None,
                'oldest': None
            }
    
    def validate_data_integrity(self) -> bool:
        """Validate data integrity"""
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
        """Repair corrupted data"""
        try:
            if not self.validate_data_integrity():
                # Try to reload data
                self.history_data = self._load_history()
                
                # If still invalid, create new empty data
                if not self.validate_data_integrity():
                    self.history_data = []
                    self._save_history()
                    return True
                    
            return True
        except Exception as e:
            print(f"Failed to repair data: {e}")
            self.history_data = []
            return False
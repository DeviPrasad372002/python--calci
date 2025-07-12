# -*- coding: utf-8 -*-

# @autor: History Feature Extension
# 历史记录窗口界面

import tkinter as tk
from tkinter import ttk, messagebox, StringVar
from functools import partial
from typing import Callable, List, Dict, Any

class HistoryWindow:
    """历史记录窗口类，提供历史记录的GUI界面"""
    
    def __init__(self, parent, history_manager, theme: Dict, on_use_calculation: Callable):
        self.parent = parent
        self.history_manager = history_manager
        self.theme = theme
        self.on_use_calculation = on_use_calculation
        
        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.setup_window()
        
        # 搜索变量
        self.search_var = StringVar()
        self.search_var.trace('w', self._on_search_change)
        
        # 当前显示的历史记录
        self.current_history = []
        
        self._create_interface()
        self._load_history()
    
    def setup_window(self):
        """设置窗口属性"""
        self.window.title('计算历史记录')
        self.window.geometry('600x500')
        self.window.minsize(500, 400)
        self.window.configure(bg=self.theme.get('master_bg', '#252729'))
        
        # 设置窗口图标和属性
        self.window.transient(self.parent)
        self.window.grab_set()  # 模态窗口
        
        # 居中显示
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f'600x500+{x}+{y}')
    
    def _create_interface(self):
        """创建界面元素"""
        # 主框架
        main_frame = tk.Frame(self.window, bg=self.theme.get('frame_bg', '#252729'))
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 顶部框架 - 标题和搜索
        top_frame = tk.Frame(main_frame, bg=self.theme.get('frame_bg', '#252729'))
        top_frame.pack(fill='x', pady=(0, 10))
        
        # 标题
        title_label = tk.Label(
            top_frame,
            text='计算历史记录',
            font=('Arial', 16, 'bold'),
            bg=self.theme.get('frame_bg', '#252729'),
            fg=self.theme.get('INPUT', {}).get('fg', '#ffffff')
        )
        title_label.pack(side='left')
        
        # 搜索框架
        search_frame = tk.Frame(top_frame, bg=self.theme.get('frame_bg', '#252729'))
        search_frame.pack(side='right')
        
        tk.Label(
            search_frame,
            text='搜索:',
            bg=self.theme.get('frame_bg', '#252729'),
            fg=self.theme.get('INPUT', {}).get('fg', '#ffffff')
        ).pack(side='left', padx=(0, 5))
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=20,
            bg=self.theme.get('INPUT', {}).get('bg', '#252729'),
            fg=self.theme.get('INPUT', {}).get('fg', '#ffffff'),
            insertbackground=self.theme.get('INPUT', {}).get('fg', '#ffffff')
        )
        self.search_entry.pack(side='left')
        
        # 中间框架 - 历史记录列表
        middle_frame = tk.Frame(main_frame, bg=self.theme.get('frame_bg', '#252729'))
        middle_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 创建Treeview来显示历史记录
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置Treeview样式
        style.configure(
            'History.Treeview',
            background=self.theme.get('BTN_NUMERICO', {}).get('bg', '#050505'),
            foreground=self.theme.get('BTN_NUMERICO', {}).get('fg', '#f5f6fa'),
            fieldbackground=self.theme.get('BTN_NUMERICO', {}).get('bg', '#050505'),
            borderwidth=0
        )
        
        style.configure(
            'History.Treeview.Heading',
            background=self.theme.get('BTN_OPERADOR', {}).get('bg', '#0e0f0f'),
            foreground=self.theme.get('BTN_OPERADOR', {}).get('fg', '#f5f6fa'),
            relief='flat'
        )
        
        # 创建Treeview
        columns = ('expression', 'result', 'time')
        self.tree = ttk.Treeview(
            middle_frame,
            columns=columns,
            show='headings',
            style='History.Treeview'
        )
        
        # 定义列
        self.tree.heading('expression', text='表达式')
        self.tree.heading('result', text='结果')
        self.tree.heading('time', text='时间')
        
        self.tree.column('expression', width=200, anchor='w')
        self.tree.column('result', width=150, anchor='e')
        self.tree.column('time', width=180, anchor='center')
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(middle_frame, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(middle_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        middle_frame.grid_rowconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', self._on_item_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)  # 右键菜单
        
        # 底部框架 - 按钮
        bottom_frame = tk.Frame(main_frame, bg=self.theme.get('frame_bg', '#252729'))
        bottom_frame.pack(fill='x')
        
        # 统计信息
        self.stats_label = tk.Label(
            bottom_frame,
            text='',
            bg=self.theme.get('frame_bg', '#252729'),
            fg=self.theme.get('INPUT', {}).get('fg', '#ffffff'),
            font=('Arial', 9)
        )
        self.stats_label.pack(side='left')
        
        # 按钮框架
        button_frame = tk.Frame(bottom_frame, bg=self.theme.get('frame_bg', '#252729'))
        button_frame.pack(side='right')
        
        # 按钮配置
        btn_config = {
            'width': 10,
            'height': 1,
            'font': ('Arial', 10),
            'bg': self.theme.get('BTN_DEFAULT', {}).get('bg', '#0e0f0f'),
            'fg': self.theme.get('BTN_DEFAULT', {}).get('fg', '#f5f6fa'),
            'activebackground': self.theme.get('BTN_DEFAULT', {}).get('activebackground', '#635f5f'),
            'activeforeground': self.theme.get('BTN_DEFAULT', {}).get('activeforeground', '#000000'),
            'border': 0
        }
        
        # 使用按钮
        self.use_btn = tk.Button(
            button_frame,
            text='使用',
            command=self._use_selected,
            **btn_config
        )
        self.use_btn.pack(side='left', padx=(0, 5))
        
        # 删除按钮
        self.delete_btn = tk.Button(
            button_frame,
            text='删除',
            command=self._delete_selected,
            **btn_config
        )
        self.delete_btn.pack(side='left', padx=(0, 5))
        
        # 清空按钮
        self.clear_btn = tk.Button(
            button_frame,
            text='清空全部',
            command=self._clear_all,
            **btn_config
        )
        self.clear_btn.pack(side='left', padx=(0, 5))
        
        # 关闭按钮
        self.close_btn = tk.Button(
            button_frame,
            text='关闭',
            command=self.window.destroy,
            **btn_config
        )
        self.close_btn.pack(side='left')
        
        # 创建右键菜单
        self._create_context_menu()
    
    def _create_context_menu(self):
        """创建右键上下文菜单"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="使用此计算", command=self._use_selected)
        self.context_menu.add_command(label="复制表达式", command=self._copy_expression)
        self.context_menu.add_command(label="复制结果", command=self._copy_result)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="删除", command=self._delete_selected)
    
    def _load_history(self):
        """加载并显示历史记录"""
        history = self.history_manager.get_history()
        self.current_history = history
        self._update_tree_view(history)
        self._update_statistics()
    
    def _update_tree_view(self, history_list: List[Dict]):
        """更新树形视图"""
        # 清空现有项目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加历史记录
        for calc in history_list:
            self.tree.insert('', 'end', values=(
                calc['expression'],
                calc['result'],
                calc['date_formatted']
            ), tags=(str(calc['id']),))
    
    def _update_statistics(self):
        """更新统计信息"""
        stats = self.history_manager.get_statistics()
        if stats['total_calculations'] > 0:
            text = f"总计算数: {stats['total_calculations']}"
            if len(self.current_history) != stats['total_calculations']:
                text += f" (显示: {len(self.current_history)})"
        else:
            text = "暂无计算记录"
        
        self.stats_label.config(text=text)
    
    def _on_search_change(self, *args):
        """搜索框内容变化时的回调"""
        query = self.search_var.get()
        filtered_history = self.history_manager.search_history(query)
        self.current_history = filtered_history
        self._update_tree_view(filtered_history)
        self._update_statistics()
    
    def _on_item_double_click(self, event):
        """双击项目时使用该计算"""
        self._use_selected()
    
    def _on_right_click(self, event):
        """右键点击显示上下文菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _get_selected_calculation(self) -> Dict:
        """获取选中的计算记录"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        values = self.tree.item(item)['values']
        tags = self.tree.item(item)['tags']
        
        if values and tags:
            calc_id = int(tags[0])
            for calc in self.current_history:
                if calc['id'] == calc_id:
                    return calc
        return None
    
    def _use_selected(self):
        """使用选中的计算"""
        calc = self._get_selected_calculation()
        if calc:
            self.on_use_calculation(calc['expression'], calc['result'])
            self.window.destroy()
        else:
            messagebox.showwarning("警告", "请先选择一个计算记录")
    
    def _delete_selected(self):
        """删除选中的计算"""
        calc = self._get_selected_calculation()
        if calc:
            if messagebox.askyesno("确认删除", f"确定要删除计算 '{calc['expression']} = {calc['result']}' 吗？"):
                if self.history_manager.delete_calculation(calc['id']):
                    self._load_history()
                    messagebox.showinfo("成功", "计算记录已删除")
                else:
                    messagebox.showerror("错误", "删除失败")
        else:
            messagebox.showwarning("警告", "请先选择一个计算记录")
    
    def _clear_all(self):
        """清空所有历史记录"""
        if messagebox.askyesno("确认清空", "确定要清空所有历史记录吗？此操作不可撤销！"):
            self.history_manager.clear_history()
            self._load_history()
            messagebox.showinfo("成功", "所有历史记录已清空")
    
    def _copy_expression(self):
        """复制表达式到剪贴板"""
        calc = self._get_selected_calculation()
        if calc:
            self.window.clipboard_clear()
            self.window.clipboard_append(calc['expression'])
            messagebox.showinfo("成功", "表达式已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "请先选择一个计算记录")
    
    def _copy_result(self):
        """复制结果到剪贴板"""
        calc = self._get_selected_calculation()
        if calc:
            self.window.clipboard_clear()
            self.window.clipboard_append(calc['result'])
            messagebox.showinfo("成功", "结果已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "请先选择一个计算记录")
# -*- coding: utf-8 -*-

# @autor: Matheus Felipe (Original) + History Feature Extension
# @github: github.com/matheusfelipeog

# Builtins
import sys 
import os
import platform

import tkinter as tk
from tkinter import Menu, FALSE, messagebox

from functools import partial
from json import load as json_load
from json import dump as json_dump

from copy import deepcopy

# Módulos próprios
from .calculador import Calculador
from .history_manager import HistoryManager
from .history_window import HistoryWindow


class Calculadora(object):
    """Classe para criação do layout da calculadora, distribuição dos botões
    e a adição de suas funcionalidades.

    Os botões distríbuidos no layout estão conforme o exemplo abaixo:

        C | ( | ) | <
        7 | 8 | 9 | x
        4 | 5 | 6 | -
        1 | 2 | 3 | +
        . | 0 | = | /
        H |   | ^ | √

        OBS: É necessário importar o modulo style contido na pacote view,
             e selecionar uma de suas classes de estilo.
             
        Nova funcionalidade: Histórico de cálculos com interface gráfica.
        Melhorias: Cursor visível e suporte ao Enter para calcular.
    """

    def __init__(self, master):
        self.master = master
        self.calc = Calculador()
        
        # 初始化历史记录管理器，添加错误处理
        try:
            self.history_manager = HistoryManager()
        except Exception as e:
            print(f"历史记录初始化失败: {e}")
            self.history_manager = None

        self.settings = self._load_settings()
        
        # Define estilo padrão para macOS, caso seja o sistema operacional utilizado
        if platform.system() == 'Darwin':
            self.theme = self._get_theme('Default Theme For MacOS')
        else:
            self.theme = self._get_theme(self.settings['current_theme'])

        # Edição da Top-Level
        self.master.title('Calculadora Tk')
        self.master.maxsize(width=335, height=415)
        self.master.minsize(width=335, height=415)
        self.master.geometry('-150+100')
        self.master['bg'] = self.theme['master_bg']

        # Área do input
        self._frame_input = tk.Frame(self.master, bg=self.theme['frame_bg'], pady=4)
        self._frame_input.pack()

        # Área dos botões
        self._frame_buttons = tk.Frame(self.master, bg=self.theme['frame_bg'], padx=2)
        self._frame_buttons.pack()

        # Funções de inicialização 
        self._create_input(self._frame_input)
        self._create_buttons(self._frame_buttons)
        self._create_menu(self.master)
        
        # 绑定键盘事件
        self._bind_keyboard_events()
        
        # 存储上一次的计算表达式，用于历史记录
        self._last_expression = ""

    @staticmethod
    def _load_settings():
        """Utilitário para carregar o arquivo de confirgurações da calculadora."""
        try:
            with open('./app/settings/settings.json', mode='r', encoding='utf-8') as f:
                settings = json_load(f)
            return settings
        except (FileNotFoundError, ValueError) as e:
            print(f"配置文件加载失败: {e}")
            # 返回默认配置
            return {
                "current_theme": "Dark",
                "global": {
                    "borderwidth": 0,
                    "highlightthickness": 0,
                    "width": 6,
                    "height": 2,
                    "font": "Arial 14 bold"
                },
                "themes": []
            }

    def _get_theme(self, name='Dark'):
        """Retorna as configurações de estilo para o theme especificado."""
        list_of_themes = self.settings.get('themes', [])

        found_theme = None
        for t in list_of_themes:
            if name == t['name']:
                found_theme = deepcopy(t)
                break
        
        # 如果没有找到主题，返回默认主题
        if not found_theme:
            found_theme = {
                "name": "Dark",
                "master_bg": "#252729",
                "frame_bg": "#252729",
                "INPUT": {
                    "bg": "#252729",
                    "fg": "#ffffff",
                    "borderwidth": 0,
                    "highlightthickness": 0,
                    "width": 15,
                    "font": "Arial 28 bold",
                    "justify": "right"
                },
                "BTN_DEFAULT": {
                    "bg": "#0e0f0f",
                    "fg": "#f5f6fa",
                    "activebackground": "#635f5f",
                    "activeforeground": "#000000"
                },
                "BTN_NUMERICO": {
                    "bg": "#050505",
                    "fg": "#f5f6fa",
                    "activebackground": "#635f5f",
                    "activeforeground": "#000000"
                },
                "BTN_OPERADOR": {
                    "bg": "#0e0f0f",
                    "fg": "#f5f6fa",
                    "activebackground": "#0097e6",
                    "activeforeground": "#000000"
                },
                "BTN_CLEAR": {
                    "bg": "#0e0f0f",
                    "fg": "#f5f6fa",
                    "activebackground": "#d63031",
                    "activeforeground": "#000000"
                }
            }
        
        return found_theme
        
    def _create_input(self, master):
        """创建输入框并配置光标显示"""
        # 创建输入框配置，确保光标可见
        input_config = deepcopy(self.theme['INPUT'])
        
        # 设置光标相关配置
        input_config['insertbackground'] = input_config.get('fg', '#ffffff')  # 光标颜色与文字颜色一致
        input_config['insertwidth'] = 2  # 光标宽度
        input_config['insertborderwidth'] = 0  # 光标边框宽度
        input_config['insertontime'] = 600  # 光标显示时间(毫秒)
        input_config['insertofftime'] = 300  # 光标隐藏时间(毫秒)
        
        self._entrada = tk.Entry(master, cnf=input_config)
        self._entrada.insert(0, 0)
        self._entrada.pack()
        
        # 确保输入框获得焦点以显示光标
        self._entrada.focus_set()
    
    def _bind_keyboard_events(self):
        """绑定键盘事件"""
        # 只绑定到输入框，避免重复触发
        self._entrada.bind('<KeyPress>', self._on_key_press)
        self._entrada.bind('<Return>', self._on_enter_press)
        self._entrada.bind('<KP_Enter>', self._on_enter_press)  # 数字键盘的Enter
        
        # 确保输入框获得焦点
        self._entrada.focus_set()
    
    def _on_key_press(self, event):
        """处理键盘按键事件"""
        key = event.keysym
        char = event.char
        
        # 处理数字键
        if char.isdigit():
            self._set_values_in_input(int(char))
            return 'break'  # 阻止默认行为
        
        # 处理运算符
        elif char in ['+', '-', '*', '/']:
            if char == '*':
                self._set_operator_in_input('*')
            else:
                self._set_operator_in_input(char)
            return 'break'
        
        # 处理小数点
        elif char == '.':
            self._set_dot_in_input('.')
            return 'break'
        
        # 处理括号
        elif char == '(':
            self._set_open_parent()
            return 'break'
        elif char == ')':
            self._set_close_parent()
            return 'break'
        
        # 处理特殊键
        elif key == 'BackSpace':
            self._del_last_value_in_input()
            return 'break'
        elif key in ['Delete', 'c', 'C']:
            self._clear_input()
            return 'break'
        elif key == 'Escape':
            self._clear_input()
            return 'break'
        
        # 处理Power运算符 (^)
        elif char == '^':
            self._set_operator_in_input('**')
            return 'break'
        
        # 处理等号
        elif char == '=':
            self._get_data_in_input()
            return 'break'
        
        # 处理历史记录快捷键
        elif key.lower() == 'h' and event.state & 0x4:  # Ctrl+H
            if self.history_manager:
                self._show_history_window()
            return 'break'
        
        # 对于其他键，允许默认行为但限制只能输入我们支持的字符
        elif char and not char.isalnum() and char not in '+-*/().^=':
            return 'break'  # 阻止不支持的字符
        
        # 允许导航键（左右箭头等）
        elif key in ['Left', 'Right', 'Home', 'End']:
            return  # 允许默认行为
        
        # 其他情况阻止输入
        else:
            return 'break'
    
    def _on_enter_press(self, event):
        """处理Enter键按下事件"""
        self._get_data_in_input()
        return 'break'  # 阻止默认行为

    def _create_menu(self, master):
        self.master.option_add('*tearOff', FALSE)
        calc_menu = Menu(self.master)
        self.master.config(menu=calc_menu)

        #Configuração
        config = Menu(calc_menu)
        theme = Menu(config)
        #Menu tema
        theme_incompatible = ['Default Theme For MacOS']
        for t in self.settings.get('themes', []):
            name = t.get('name', '')
            if name in theme_incompatible:  # Ignora os temas não compatíveis.
                continue
            else:
                theme.add_command(label=name, command=partial(self._change_theme_to, name))
        
        # 添加历史记录菜单 - 只有在历史管理器可用时才添加
        if self.history_manager:
            history_menu = Menu(calc_menu)
            calc_menu.add_cascade(label='历史记录', menu=history_menu)
            history_menu.add_command(label='查看历史记录 (Ctrl+H)', command=self._show_history_window)
            history_menu.add_command(label='清空历史记录', command=self._clear_history_confirm)
        
        # 添加帮助菜单
        help_menu = Menu(calc_menu)
        calc_menu.add_cascade(label='帮助', menu=help_menu)
        help_menu.add_command(label='键盘快捷键', command=self._show_keyboard_shortcuts)
        
        #Configuração
        calc_menu.add_cascade(label='Configuração', menu=config)
        config.add_cascade(label='Tema', menu=theme)

        config.add_separator()
        config.add_command(label='Sair', command=self._exit)
    
    def _show_keyboard_shortcuts(self):
        """显示键盘快捷键帮助"""
        shortcuts_text = """键盘快捷键:

数字键 (0-9): 输入数字
运算符 (+, -, *, /): 输入运算符
小数点 (.): 输入小数点
括号 ((, )): 输入括号
^ : 乘方运算 (**)
= 或 Enter: 计算结果
Backspace: 删除最后一个字符
Delete 或 C: 清空输入
Escape: 清空输入
Ctrl+H: 打开历史记录
H: 历史记录按钮

鼠标操作:
- 点击按钮进行输入
- 双击历史记录项目使用该计算
- 右键点击历史记录查看更多选项"""
        
        messagebox.showinfo("键盘快捷键", shortcuts_text)

    def _change_theme_to(self, name='Dark'):
        """修改主题设置并重启应用"""
        try:
            self.settings['current_theme'] = name
            with open('./app/settings/settings.json', 'w', encoding='utf-8') as outfile:
                json_dump(self.settings, outfile, indent=4, ensure_ascii=False)
            self._realod_app()
        except Exception as e:
            messagebox.showerror("错误", f"主题切换失败: {e}")
    
    def _show_history_window(self):
        """显示历史记录窗口"""
        if not self.history_manager:
            messagebox.showerror("错误", "历史记录功能不可用")
            return
            
        try:
            HistoryWindow(
                parent=self.master,
                history_manager=self.history_manager,
                theme=self.theme,
                on_use_calculation=self._use_calculation_from_history
            )
        except Exception as e:
            print(f"打开历史记录窗口时出错: {e}")
            messagebox.showerror("错误", f"无法打开历史记录窗口: {e}")
    
    def _clear_history_confirm(self):
        """确认清空历史记录"""
        if not self.history_manager:
            messagebox.showerror("错误", "历史记录功能不可用")
            return
            
        try:
            if messagebox.askyesno("确认清空", "确定要清空所有历史记录吗？此操作不可撤销！"):
                self.history_manager.clear_history()
                messagebox.showinfo("成功", "历史记录已清空")
        except Exception as e:
            messagebox.showerror("错误", f"清空历史记录失败: {e}")
    
    def _use_calculation_from_history(self, expression: str, result: str):
        """从历史记录中使用计算"""
        try:
            # 清空当前输入
            self._entrada.delete(0, tk.END)
            # 插入表达式
            self._entrada.insert(0, expression)
            # 确保光标在末尾
            self._entrada.icursor(tk.END)
            # 确保输入框获得焦点以显示光标
            self._entrada.focus_set()
        except Exception as e:
            print(f"使用历史记录失败: {e}")
        
    def _create_buttons(self, master):
        """"Metódo responsável pela criação de todos os botões da calculadora,
        indo desde adição de eventos em cada botão à distribuição no layout grid.
        """

        # Seta configurações globais (width, height font etc) no botão especificado.
        btn_numerico_config = deepcopy(self.theme.get('BTN_NUMERICO', {}))
        btn_numerico_config.update(self.settings.get('global', {}))

        self._BTN_NUM_0 = tk.Button(master, text=0, cnf=btn_numerico_config)
        self._BTN_NUM_1 = tk.Button(master, text=1, cnf=btn_numerico_config)
        self._BTN_NUM_2 = tk.Button(master, text=2, cnf=btn_numerico_config)
        self._BTN_NUM_3 = tk.Button(master, text=3, cnf=btn_numerico_config)
        self._BTN_NUM_4 = tk.Button(master, text=4, cnf=btn_numerico_config)
        self._BTN_NUM_5 = tk.Button(master, text=5, cnf=btn_numerico_config)
        self._BTN_NUM_6 = tk.Button(master, text=6, cnf=btn_numerico_config)
        self._BTN_NUM_7 = tk.Button(master, text=7, cnf=btn_numerico_config)
        self._BTN_NUM_8 = tk.Button(master, text=8, cnf=btn_numerico_config)
        self._BTN_NUM_9 = tk.Button(master, text=9, cnf=btn_numerico_config)

        # Seta configurações globais (width, height font etc) no botão especificado.
        btn_operador_config = deepcopy(self.theme.get('BTN_OPERADOR', {}))
        btn_operador_config.update(self.settings.get('global', {}))

        # Instânciação dos botões dos operadores númericos
        self._BTN_SOMA = tk.Button(master, text='+', cnf=btn_operador_config)
        self._BTN_SUB = tk.Button(master, text='-', cnf=btn_operador_config)
        self._BTN_DIV = tk.Button(master, text='/', cnf=btn_operador_config)
        self._BTN_MULT = tk.Button(master, text='*', cnf=btn_operador_config)
        self._BTN_EXP = tk.Button(master, text='^', cnf=btn_operador_config)
        self._BTN_RAIZ = tk.Button(master, text='√', cnf=btn_operador_config)

        # Seta configurações globais (width, height font etc) no botão especificado.
        btn_default_config = deepcopy(self.theme.get('BTN_DEFAULT', {}))
        btn_default_config.update(self.settings.get('global', {}))
        
        btn_clear_config = deepcopy(self.theme.get('BTN_CLEAR', {}))
        btn_clear_config.update(self.settings.get('global', {}))

        # Instânciação dos botões de funcionalidades da calculadora
        self._BTN_ABRE_PARENTESE = tk.Button(master, text='(', cnf=btn_default_config)
        self._BTN_FECHA_PARENTESE = tk.Button(master, text=')', cnf=btn_default_config)
        self._BTN_CLEAR = tk.Button(master, text='C', cnf=btn_default_config)
        self._BTN_DEL = tk.Button(master, text='<', cnf=btn_clear_config)
        self._BTN_RESULT = tk.Button(master, text='=', cnf=btn_operador_config)
        self._BTN_DOT = tk.Button(master, text='.', cnf=btn_default_config)
        
        # 添加历史记录按钮 - 只有在历史管理器可用时才启用
        if self.history_manager:
            self._BTN_HISTORY = tk.Button(master, text='H', cnf=btn_default_config)
        else:
            # 如果历史功能不可用，创建一个禁用的按钮
            disabled_config = deepcopy(btn_default_config)
            disabled_config['state'] = 'disabled'
            self._BTN_HISTORY = tk.Button(master, text='H', cnf=disabled_config)

        # Instânciação dos botões vazios，为未来功能预留
        self._BTN_VAZIO2 = tk.Button(master, text='', cnf=btn_operador_config, state='disabled')

        # Distribuição dos botões em um gerenciador de layout grid
        # Linha 0
        self._BTN_CLEAR.grid(row=0, column=0, padx=1, pady=1)
        self._BTN_ABRE_PARENTESE.grid(row=0, column=1, padx=1, pady=1)
        self._BTN_FECHA_PARENTESE.grid(row=0, column=2, padx=1, pady=1)
        self._BTN_DEL.grid(row=0, column=3, padx=1, pady=1)

        # Linha 1
        self._BTN_NUM_7.grid(row=1, column=0, padx=1, pady=1)
        self._BTN_NUM_8.grid(row=1, column=1, padx=1, pady=1)
        self._BTN_NUM_9.grid(row=1, column=2, padx=1, pady=1)
        self._BTN_MULT.grid(row=1, column=3, padx=1, pady=1)

        # Linha 2
        self._BTN_NUM_4.grid(row=2, column=0, padx=1, pady=1)
        self._BTN_NUM_5.grid(row=2, column=1, padx=1, pady=1)
        self._BTN_NUM_6.grid(row=2, column=2, padx=1, pady=1)
        self._BTN_SUB.grid(row=2, column=3, padx=1, pady=1)

        # Linha 3
        self._BTN_NUM_1.grid(row=3, column=0, padx=1, pady=1)
        self._BTN_NUM_2.grid(row=3, column=1, padx=1, pady=1)
        self._BTN_NUM_3.grid(row=3, column=2, padx=1, pady=1)
        self._BTN_SOMA.grid(row=3, column=3, padx=1, pady=1)

        # Linha 4
        self._BTN_DOT.grid(row=4, column=0, padx=1, pady=1)
        self._BTN_NUM_0.grid(row=4, column=1, padx=1, pady=1)
        self._BTN_RESULT.grid(row=4, column=2, padx=1, pady=1)
        self._BTN_DIV.grid(row=4, column=3, padx=1, pady=1)

        # Linha 5 - 历史记录按钮替换第一个空按钮
        self._BTN_HISTORY.grid(row=5, column=0, padx=1, pady=1)
        self._BTN_VAZIO2.grid(row=5, column=1, padx=1, pady=1)
        self._BTN_EXP.grid(row=5, column=2, padx=1, pady=1)
        self._BTN_RAIZ.grid(row=5, column=3, padx=1, pady=1)

        # 为所有按钮绑定点击后重新聚焦到输入框的事件
        buttons = [
            self._BTN_NUM_0, self._BTN_NUM_1, self._BTN_NUM_2, self._BTN_NUM_3, self._BTN_NUM_4,
            self._BTN_NUM_5, self._BTN_NUM_6, self._BTN_NUM_7, self._BTN_NUM_8, self._BTN_NUM_9,
            self._BTN_SOMA, self._BTN_SUB, self._BTN_DIV, self._BTN_MULT, self._BTN_EXP, self._BTN_RAIZ,
            self._BTN_ABRE_PARENTESE, self._BTN_FECHA_PARENTESE, self._BTN_CLEAR, self._BTN_DEL,
            self._BTN_RESULT, self._BTN_DOT
        ]
        
        if self.history_manager:
            buttons.append(self._BTN_HISTORY)

        # Eventos dos botões númericos
        self._BTN_NUM_0['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 0))
        self._BTN_NUM_1['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 1))
        self._BTN_NUM_2['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 2))
        self._BTN_NUM_3['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 3))
        self._BTN_NUM_4['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 4))
        self._BTN_NUM_5['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 5))
        self._BTN_NUM_6['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 6))
        self._BTN_NUM_7['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 7))
        self._BTN_NUM_8['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 8))
        self._BTN_NUM_9['command'] = partial(self._button_click_wrapper, partial(self._set_values_in_input, 9))

        # Eventos dos botões de operação matemática
        self._BTN_SOMA['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '+'))
        self._BTN_SUB['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '-'))
        self._BTN_MULT['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '*'))
        self._BTN_DIV['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '/'))
        self._BTN_EXP['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '**'))
        self._BTN_RAIZ['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '**(1/2)'))

        # Eventos dos botões de funcionalidades da calculadora
        self._BTN_DOT['command'] = partial(self._button_click_wrapper, partial(self._set_dot_in_input, '.'))
        self._BTN_ABRE_PARENTESE['command'] = partial(self._button_click_wrapper, self._set_open_parent)
        self._BTN_FECHA_PARENTESE['command'] = partial(self._button_click_wrapper, self._set_close_parent)
        self._BTN_DEL['command'] = partial(self._button_click_wrapper, self._del_last_value_in_input)
        self._BTN_CLEAR['command'] = partial(self._button_click_wrapper, self._clear_input)
        self._BTN_RESULT['command'] = partial(self._button_click_wrapper, self._get_data_in_input)
        
        # 历史记录按钮事件 - 只有在历史管理器可用时才绑定
        if self.history_manager:
            self._BTN_HISTORY['command'] = self._show_history_window  # 历史窗口不需要重新聚焦
    
    def _button_click_wrapper(self, func):
        """按钮点击包装器，确保点击后输入框保持焦点"""
        func()
        # 确保输入框保持焦点和光标可见
        self._entrada.focus_set()
        # 将光标移到末尾
        self._entrada.icursor(tk.END)

    def _set_values_in_input(self, value):
        """Metódo responsável por captar o valor númerico clicado e setar no input"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)  # 获取当前光标位置
            
            if current_value == 'Erro':
                self._entrada.delete(0, tk.END)
                self._entrada.insert(0, value)
                self._entrada.icursor(1)  # 光标移到数字后面
                return

            if current_value == '0':
                self._entrada.delete(0, tk.END)
                self._entrada.insert(0, value)
                self._entrada.icursor(1)  # 光标移到数字后面
            elif self._lenght_max(current_value):
                # 在光标位置插入数字
                self._entrada.insert(cursor_pos, value)
                self._entrada.icursor(cursor_pos + 1)  # 光标移到插入数字后面
        except Exception as e:
            print(f"输入数字时出错: {e}")
    
    def _set_dot_in_input(self, dot):
        """Metódo responsável por setar o ponto de separação decimal no valor"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Erro':
                return 

            # 检查当前数字段是否已有小数点
            if len(current_value) > 0:
                # 找到光标位置前后的运算符
                left_part = current_value[:cursor_pos]
                right_part = current_value[cursor_pos:]
                
                # 找到当前数字段的范围
                left_operator_pos = -1
                for i in range(len(left_part) - 1, -1, -1):
                    if left_part[i] in '+-*/(':
                        left_operator_pos = i
                        break
                
                right_operator_pos = len(current_value)
                for i in range(len(right_part)):
                    if right_part[i] in '+-*/)':
                        right_operator_pos = cursor_pos + i
                        break
                
                # 检查当前数字段是否已有小数点
                current_number = current_value[left_operator_pos + 1:right_operator_pos]
                if '.' in current_number:
                    return  # 当前数字已有小数点，不添加

            if (len(current_value) > 0 and 
                cursor_pos > 0 and
                current_value[cursor_pos - 1] not in '.+-/*' and 
                self._lenght_max(current_value)):
                self._entrada.insert(cursor_pos, dot)
                self._entrada.icursor(cursor_pos + 1)
            elif cursor_pos == 0 or current_value[cursor_pos - 1] in '+-*/(':
                # 在运算符后添加 "0."
                self._entrada.insert(cursor_pos, '0.')
                self._entrada.icursor(cursor_pos + 2)
        except Exception as e:
            print(f"输入小数点时出错: {e}")

    def _set_open_parent(self):
        """Metódo para setar a abertura de parenteses no input"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Erro':
                self._clear_input()
                return

            if current_value == '0' and cursor_pos == 1:
                self._entrada.delete(0, tk.END)
                self._entrada.insert(0, '(')
                self._entrada.icursor(1)
            elif (cursor_pos == 0 or 
                  current_value[cursor_pos - 1] in '+-/*(' and 
                  self._lenght_max(current_value)):
                self._entrada.insert(cursor_pos, '(')
                self._entrada.icursor(cursor_pos + 1)
        except Exception as e:
            print(f"输入左括号时出错: {e}")
    
    def _set_close_parent(self):
        """Metódo para setar o fechamento de parenteses no input"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Erro':
                return

            # 检查括号平衡
            open_count = current_value.count('(')
            close_count = current_value.count(')')
            
            if open_count <= close_count:
                return  # 已经平衡或关闭括号过多
                
            if (cursor_pos > 0 and 
                current_value[cursor_pos - 1] not in '+-/*(' and 
                self._lenght_max(current_value)):
                self._entrada.insert(cursor_pos, ')')
                self._entrada.icursor(cursor_pos + 1)
        except Exception as e:
            print(f"输入右括号时出错: {e}")

    def _clear_input(self):
        """Reseta o input da calculadora, limpando-o por completo e inserindo o valor 0"""
        try:
            self._entrada.delete(0, tk.END)
            self._entrada.insert(0, 0)
            self._entrada.icursor(1)  # 光标移到0后面
        except Exception as e:
            print(f"清空输入时出错: {e}")
    
    def _del_last_value_in_input(self):
        """删除光标前面的字符"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Erro':
                self._clear_input()
                return

            if cursor_pos > 0:
                self._entrada.delete(cursor_pos - 1)
                self._entrada.icursor(cursor_pos - 1)
            
            # 如果删除后为空，设置为0
            if not self._entrada.get():
                self._entrada.insert(0, 0)
                self._entrada.icursor(1)
        except Exception as e:
            print(f"删除字符时出错: {e}")
    
    def _set_operator_in_input(self, operator):
        """Metódo responsável por captar o operador matemático clicado e setar no input"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Erro':
                return

            if current_value == '' or current_value == '0':
                if operator == '-':  # 允许负号作为第一个字符
                    if current_value == '0':
                        self._entrada.delete(0, tk.END)
                    self._entrada.insert(0, '-')
                    self._entrada.icursor(1)
                return
                
            # 避免连续运算符，但允许负号
            if cursor_pos > 0:
                prev_char = current_value[cursor_pos - 1]
                if prev_char in '+-*/' and operator != '-':
                    return
                # 如果最后是运算符且当前是负号，只在特定情况下允许
                if prev_char in '+-*/' and operator == '-':
                    if prev_char == '-':  # 避免连续负号
                        return
                        
            if self._lenght_max(current_value):
                self._entrada.insert(cursor_pos, operator)
                self._entrada.icursor(cursor_pos + len(operator))
        except Exception as e:
            print(f"输入运算符时出错: {e}")
            
    def _get_data_in_input(self):
        """Pega os dados com todas as operações contidos dentro do input
        para realizar o calculo e adiciona ao histórico"""
        try:
            current_value = self._entrada.get()
            
            if current_value == 'Erro' or not current_value:
                return

            # 保存计算表达式
            expression = current_value
            self._last_expression = expression
            
            result = self.calc.calculation(expression)
            self._set_result_in_input(result=result)
            
            # 添加到历史记录 - 添加空值检查
            if (self.history_manager and 
                result != 'Erro' and 
                expression and 
                expression != '0'):
                self.history_manager.add_calculation(expression, result)
        except Exception as e:
            print(f"计算时出错: {e}")
            self._entrada.delete(0, len(self._entrada.get()))
            self._entrada.insert(0, 'Erro')

    def _set_result_in_input(self, result=0):
        """Seta o resultado de toda a operação dentro do input"""
        try:
            self._entrada.delete(0, len(self._entrada.get()))
            self._entrada.insert(0, result)
            # 确保光标在结果末尾
            self._entrada.icursor(tk.END)
        except Exception as e:
            print(f"设置结果时出错: {e}")

    def _lenght_max(self, data_in_input):
        """Para verificar se o input atingiu a quantidade de caracteres máxima"""
        try:
            return len(str(data_in_input)) < 15  # 修改为小于15而不是大于等于15
        except:
            return False
            
    def start(self):
        """启动计算器应用"""
        print('\33[92mCalculadora Tk Iniciada. . .\33[m\n')
        if self.history_manager:
            print('\33[94m历史记录功能已启用 - 按 H 键或使用菜单查看历史记录\33[m\n')
        else:
            print('\33[93m历史记录功能不可用\33[m\n')
        print('\33[96m新功能: 光标可见 + Enter键计算 + 完整键盘支持\33[m\n')
        print('\33[95m快捷键: Enter=计算, Backspace=删除, C/Delete/Esc=清空, Ctrl+H=历史\33[m\n')
        self.master.mainloop()
    
    def _realod_app(self):
        """Reinicia o aplicativo."""
        try:
            python = sys.executable  # Recupera o path do executável do python
            os.execl(python, python, *sys.argv)
        except Exception as e:
            print(f"重启应用失败: {e}")
            messagebox.showerror("错误", f"重启应用失败: {e}")

    def _exit(self):
        """安全退出应用"""
        try:
            self.master.quit()
            self.master.destroy()
        except:
            exit()
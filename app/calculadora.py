# -*- coding: utf-8 -*-

# @author: Matheus Felipe (Original) + History Feature Extension
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

# Own modules
from .calculador import Calculador
from .history_manager import HistoryManager
from .history_window import HistoryWindow


class Calculadora(object):
    """Class for creating the calculator layout, distributing buttons
    and adding their functionalities.

    The buttons distributed in the layout are as shown in the example below:

        C | ( | ) | <
        7 | 8 | 9 | x
        4 | 5 | 6 | -
        1 | 2 | 3 | +
        . | 0 | = | /
        H |   | ^ | √

        NOTE: It's necessary to import the style module contained in the view package,
             and select one of its style classes.
             
        New feature: Calculation history with graphical interface.
        Improvements: Visible cursor and Enter key support for calculation.
    """

    def __init__(self, master):
        self.master = master
        self.calc = Calculador()
        
        # Initialize history manager with error handling
        try:
            self.history_manager = HistoryManager()
        except Exception as e:
            print(f"History initialization failed: {e}")
            self.history_manager = None

        self.settings = self._load_settings()
        
        # Define default style for macOS, if it's the operating system being used
        if platform.system() == 'Darwin':
            self.theme = self._get_theme('Default Theme For MacOS')
        else:
            self.theme = self._get_theme(self.settings['current_theme'])

        # Top-Level editing
        self.master.title('Calculator Tk')
        self.master.maxsize(width=335, height=415)
        self.master.minsize(width=335, height=415)
        self.master.geometry('-150+100')
        self.master['bg'] = self.theme['master_bg']

        # Input area
        self._frame_input = tk.Frame(self.master, bg=self.theme['frame_bg'], pady=4)
        self._frame_input.pack()

        # Button area
        self._frame_buttons = tk.Frame(self.master, bg=self.theme['frame_bg'], padx=2)
        self._frame_buttons.pack()

        # Initialization functions 
        self._create_input(self._frame_input)
        self._create_buttons(self._frame_buttons)
        self._create_menu(self.master)
        
        # Bind keyboard events
        self._bind_keyboard_events()
        
        # Store the last calculation expression for history
        self._last_expression = ""

    @staticmethod
    def _load_settings():
        """Utility to load the calculator configuration file."""
        try:
            with open('./app/settings/settings.json', mode='r', encoding='utf-8') as f:
                settings = json_load(f)
            return settings
        except (FileNotFoundError, ValueError) as e:
            print(f"Configuration file loading failed: {e}")
            # Return default configuration
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
        """Returns the style settings for the specified theme."""
        list_of_themes = self.settings.get('themes', [])

        found_theme = None
        for t in list_of_themes:
            if name == t['name']:
                found_theme = deepcopy(t)
                break
        
        # If theme not found, return default theme
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
        """Create input field and configure cursor visibility"""
        # Create input field configuration, ensuring cursor is visible
        input_config = deepcopy(self.theme['INPUT'])
        
        # Set cursor-related configurations
        input_config['insertbackground'] = input_config.get('fg', '#ffffff')  # Cursor color matches text color
        input_config['insertwidth'] = 2  # Cursor width
        input_config['insertborderwidth'] = 0  # Cursor border width
        input_config['insertontime'] = 600  # Cursor display time (milliseconds)
        input_config['insertofftime'] = 300  # Cursor hide time (milliseconds)
        
        self._entrada = tk.Entry(master, cnf=input_config)
        self._entrada.insert(0, 0)
        self._entrada.pack()
        
        # Ensure input field gets focus to show cursor
        self._entrada.focus_set()
    
    def _bind_keyboard_events(self):
        """Bind keyboard events"""
        # Only bind to input field to avoid duplicate triggering
        self._entrada.bind('<KeyPress>', self._on_key_press)
        self._entrada.bind('<Return>', self._on_enter_press)
        self._entrada.bind('<KP_Enter>', self._on_enter_press)  # Numeric keypad Enter
        
        # Ensure input field gets focus
        self._entrada.focus_set()
    
    def _on_key_press(self, event):
        """Handle keyboard key press events"""
        key = event.keysym
        char = event.char
        
        # Handle number keys
        if char.isdigit():
            self._set_values_in_input(int(char))
            return 'break'  # Prevent default behavior
        
        # Handle operators
        elif char in ['+', '-', '*', '/']:
            if char == '*':
                self._set_operator_in_input('*')
            else:
                self._set_operator_in_input(char)
            return 'break'
        
        # Handle decimal point
        elif char == '.':
            self._set_dot_in_input('.')
            return 'break'
        
        # Handle parentheses
        elif char == '(':
            self._set_open_parent()
            return 'break'
        elif char == ')':
            self._set_close_parent()
            return 'break'
        
        # Handle special keys
        elif key == 'BackSpace':
            self._del_last_value_in_input()
            return 'break'
        elif key in ['Delete', 'c', 'C']:
            self._clear_input()
            return 'break'
        elif key == 'Escape':
            self._clear_input()
            return 'break'
        
        # Handle Power operator (^)
        elif char == '^':
            self._set_operator_in_input('**')
            return 'break'
        
        # Handle equals sign
        elif char == '=':
            self._get_data_in_input()
            return 'break'
        
        # Handle history shortcut
        elif key.lower() == 'h' and event.state & 0x4:  # Ctrl+H
            if self.history_manager:
                self._show_history_window()
            return 'break'
        
        # For other keys, allow default behavior but restrict to only supported characters
        elif char and not char.isalnum() and char not in '+-*/().^=':
            return 'break'  # Block unsupported characters
        
        # Allow navigation keys (left/right arrows, etc.)
        elif key in ['Left', 'Right', 'Home', 'End']:
            return  # Allow default behavior
        
        # Block input for other cases
        else:
            return 'break'
    
    def _on_enter_press(self, event):
        """Handle Enter key press event"""
        self._get_data_in_input()
        return 'break'  # Prevent default behavior

    def _create_menu(self, master):
        self.master.option_add('*tearOff', FALSE)
        calc_menu = Menu(self.master)
        self.master.config(menu=calc_menu)

        # Configuration
        config = Menu(calc_menu)
        theme = Menu(config)
        # Theme menu
        theme_incompatible = ['Default Theme For MacOS']
        for t in self.settings.get('themes', []):
            name = t.get('name', '')
            if name in theme_incompatible:  # Ignore incompatible themes.
                continue
            else:
                theme.add_command(label=name, command=partial(self._change_theme_to, name))
        
        # Add history menu - only add when history manager is available
        if self.history_manager:
            history_menu = Menu(calc_menu)
            calc_menu.add_cascade(label='History', menu=history_menu)
            history_menu.add_command(label='View History (Ctrl+H)', command=self._show_history_window)
            history_menu.add_command(label='Clear History', command=self._clear_history_confirm)
        
        # Add help menu
        help_menu = Menu(calc_menu)
        calc_menu.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label='Keyboard Shortcuts', command=self._show_keyboard_shortcuts)
        
        # Configuration
        calc_menu.add_cascade(label='Configuration', menu=config)
        config.add_cascade(label='Theme', menu=theme)

        config.add_separator()
        config.add_command(label='Exit', command=self._exit)
    
    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts help"""
        shortcuts_text = """Keyboard Shortcuts:

Number keys (0-9): Input numbers
Operators (+, -, *, /): Input operators
Decimal point (.): Input decimal point
Parentheses ((, )): Input parentheses
^ : Power operation (**)
= or Enter: Calculate result
Backspace: Delete last character
Delete or C: Clear input
Escape: Clear input
Ctrl+H: Open history
H: History button

Mouse operations:
- Click buttons for input
- Double-click history items to use calculation
- Right-click history for more options"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)

    def _change_theme_to(self, name='Dark'):
        """Change theme settings and restart application"""
        try:
            self.settings['current_theme'] = name
            with open('./app/settings/settings.json', 'w', encoding='utf-8') as outfile:
                json_dump(self.settings, outfile, indent=4, ensure_ascii=False)
            self._realod_app()
        except Exception as e:
            messagebox.showerror("Error", f"Theme change failed: {e}")
    
    def _show_history_window(self):
        """Show history window"""
        if not self.history_manager:
            messagebox.showerror("Error", "History feature is not available")
            return
            
        try:
            HistoryWindow(
                parent=self.master,
                history_manager=self.history_manager,
                theme=self.theme,
                on_use_calculation=self._use_calculation_from_history
            )
        except Exception as e:
            print(f"Error opening history window: {e}")
            messagebox.showerror("Error", f"Unable to open history window: {e}")
    
    def _clear_history_confirm(self):
        """Confirm clearing history"""
        if not self.history_manager:
            messagebox.showerror("Error", "History feature is not available")
            return
            
        try:
            if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all history? This action cannot be undone!"):
                self.history_manager.clear_history()
                messagebox.showinfo("Success", "History has been cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear history: {e}")
    
    def _use_calculation_from_history(self, expression: str, result: str):
        """Use calculation from history"""
        try:
            # Clear current input
            self._entrada.delete(0, tk.END)
            # Insert expression
            self._entrada.insert(0, expression)
            # Ensure cursor is at the end
            self._entrada.icursor(tk.END)
            # Ensure input field gets focus to show cursor
            self._entrada.focus_set()
        except Exception as e:
            print(f"Failed to use history: {e}")
        
    def _create_buttons(self, master):
        """"Method responsible for creating all calculator buttons,
        from adding events to each button to distribution in grid layout.
        """

        # Set global configurations (width, height font etc) on specified button.
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

        # Set global configurations (width, height font etc) on specified button.
        btn_operador_config = deepcopy(self.theme.get('BTN_OPERADOR', {}))
        btn_operador_config.update(self.settings.get('global', {}))

        # Instantiation of numeric operator buttons
        self._BTN_SOMA = tk.Button(master, text='+', cnf=btn_operador_config)
        self._BTN_SUB = tk.Button(master, text='-', cnf=btn_operador_config)
        self._BTN_DIV = tk.Button(master, text='/', cnf=btn_operador_config)
        self._BTN_MULT = tk.Button(master, text='*', cnf=btn_operador_config)
        self._BTN_EXP = tk.Button(master, text='^', cnf=btn_operador_config)
        self._BTN_RAIZ = tk.Button(master, text='√', cnf=btn_operador_config)

        # Set global configurations (width, height font etc) on specified button.
        btn_default_config = deepcopy(self.theme.get('BTN_DEFAULT', {}))
        btn_default_config.update(self.settings.get('global', {}))
        
        btn_clear_config = deepcopy(self.theme.get('BTN_CLEAR', {}))
        btn_clear_config.update(self.settings.get('global', {}))

        # Instantiation of calculator functionality buttons
        self._BTN_ABRE_PARENTESE = tk.Button(master, text='(', cnf=btn_default_config)
        self._BTN_FECHA_PARENTESE = tk.Button(master, text=')', cnf=btn_default_config)
        self._BTN_CLEAR = tk.Button(master, text='C', cnf=btn_default_config)
        self._BTN_DEL = tk.Button(master, text='<', cnf=btn_clear_config)
        self._BTN_RESULT = tk.Button(master, text='=', cnf=btn_operador_config)
        self._BTN_DOT = tk.Button(master, text='.', cnf=btn_default_config)
        
        # Add history button - only enable when history manager is available
        if self.history_manager:
            self._BTN_HISTORY = tk.Button(master, text='H', cnf=btn_default_config)
        else:
            # If history feature is not available, create a disabled button
            disabled_config = deepcopy(btn_default_config)
            disabled_config['state'] = 'disabled'
            self._BTN_HISTORY = tk.Button(master, text='H', cnf=disabled_config)

        # Instantiation of empty buttons, reserved for future features
        self._BTN_VAZIO2 = tk.Button(master, text='', cnf=btn_operador_config, state='disabled')

        # Distribution of buttons in grid layout manager
        # Row 0
        self._BTN_CLEAR.grid(row=0, column=0, padx=1, pady=1)
        self._BTN_ABRE_PARENTESE.grid(row=0, column=1, padx=1, pady=1)
        self._BTN_FECHA_PARENTESE.grid(row=0, column=2, padx=1, pady=1)
        self._BTN_DEL.grid(row=0, column=3, padx=1, pady=1)

        # Row 1
        self._BTN_NUM_7.grid(row=1, column=0, padx=1, pady=1)
        self._BTN_NUM_8.grid(row=1, column=1, padx=1, pady=1)
        self._BTN_NUM_9.grid(row=1, column=2, padx=1, pady=1)
        self._BTN_MULT.grid(row=1, column=3, padx=1, pady=1)

        # Row 2
        self._BTN_NUM_4.grid(row=2, column=0, padx=1, pady=1)
        self._BTN_NUM_5.grid(row=2, column=1, padx=1, pady=1)
        self._BTN_NUM_6.grid(row=2, column=2, padx=1, pady=1)
        self._BTN_SUB.grid(row=2, column=3, padx=1, pady=1)

        # Row 3
        self._BTN_NUM_1.grid(row=3, column=0, padx=1, pady=1)
        self._BTN_NUM_2.grid(row=3, column=1, padx=1, pady=1)
        self._BTN_NUM_3.grid(row=3, column=2, padx=1, pady=1)
        self._BTN_SOMA.grid(row=3, column=3, padx=1, pady=1)

        # Row 4
        self._BTN_DOT.grid(row=4, column=0, padx=1, pady=1)
        self._BTN_NUM_0.grid(row=4, column=1, padx=1, pady=1)
        self._BTN_RESULT.grid(row=4, column=2, padx=1, pady=1)
        self._BTN_DIV.grid(row=4, column=3, padx=1, pady=1)

        # Row 5 - History button replaces first empty button
        self._BTN_HISTORY.grid(row=5, column=0, padx=1, pady=1)
        self._BTN_VAZIO2.grid(row=5, column=1, padx=1, pady=1)
        self._BTN_EXP.grid(row=5, column=2, padx=1, pady=1)
        self._BTN_RAIZ.grid(row=5, column=3, padx=1, pady=1)

        # Bind all buttons to refocus input field after click
        buttons = [
            self._BTN_NUM_0, self._BTN_NUM_1, self._BTN_NUM_2, self._BTN_NUM_3, self._BTN_NUM_4,
            self._BTN_NUM_5, self._BTN_NUM_6, self._BTN_NUM_7, self._BTN_NUM_8, self._BTN_NUM_9,
            self._BTN_SOMA, self._BTN_SUB, self._BTN_DIV, self._BTN_MULT, self._BTN_EXP, self._BTN_RAIZ,
            self._BTN_ABRE_PARENTESE, self._BTN_FECHA_PARENTESE, self._BTN_CLEAR, self._BTN_DEL,
            self._BTN_RESULT, self._BTN_DOT
        ]
        
        if self.history_manager:
            buttons.append(self._BTN_HISTORY)

        # Events for numeric buttons
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

        # Events for mathematical operation buttons
        self._BTN_SOMA['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '+'))
        self._BTN_SUB['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '-'))
        self._BTN_MULT['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '*'))
        self._BTN_DIV['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '/'))
        self._BTN_EXP['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '**'))
        self._BTN_RAIZ['command'] = partial(self._button_click_wrapper, partial(self._set_operator_in_input, '**(1/2)'))

        # Events for calculator functionality buttons
        self._BTN_DOT['command'] = partial(self._button_click_wrapper, partial(self._set_dot_in_input, '.'))
        self._BTN_ABRE_PARENTESE['command'] = partial(self._button_click_wrapper, self._set_open_parent)
        self._BTN_FECHA_PARENTESE['command'] = partial(self._button_click_wrapper, self._set_close_parent)
        self._BTN_DEL['command'] = partial(self._button_click_wrapper, self._del_last_value_in_input)
        self._BTN_CLEAR['command'] = partial(self._button_click_wrapper, self._clear_input)
        self._BTN_RESULT['command'] = partial(self._button_click_wrapper, self._get_data_in_input)
        
        # History button event - only bind when history manager is available
        if self.history_manager:
            self._BTN_HISTORY['command'] = self._show_history_window  # History window doesn't need refocus
    
    def _button_click_wrapper(self, func):
        """Button click wrapper, ensures input field maintains focus after click"""
        func()
        # Ensure input field maintains focus and cursor is visible
        self._entrada.focus_set()
        # Move cursor to end
        self._entrada.icursor(tk.END)

    def _set_values_in_input(self, value):
        """Method responsible for capturing the clicked numeric value and setting it in the input"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)  # Get current cursor position
            
            if current_value == 'Error':
                self._entrada.delete(0, tk.END)
                self._entrada.insert(0, value)
                self._entrada.icursor(1)  # Move cursor after the number
                return

            if current_value == '0':
                self._entrada.delete(0, tk.END)
                self._entrada.insert(0, value)
                self._entrada.icursor(1)  # Move cursor after the number
            elif self._lenght_max(current_value):
                # Insert number at cursor position
                self._entrada.insert(cursor_pos, value)
                self._entrada.icursor(cursor_pos + 1)  # Move cursor after inserted number
        except Exception as e:
            print(f"Error inputting number: {e}")
    
    def _set_dot_in_input(self, dot):
        """Method responsible for setting the decimal point separator in the value"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Error':
                return 

            # Check if current number segment already has a decimal point
            if len(current_value) > 0:
                # Find operators before and after cursor position
                left_part = current_value[:cursor_pos]
                right_part = current_value[cursor_pos:]
                
                # Find the range of current number segment
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
                
                # Check if current number segment already has decimal point
                current_number = current_value[left_operator_pos + 1:right_operator_pos]
                if '.' in current_number:
                    return  # Current number already has decimal point, don't add

            if (len(current_value) > 0 and 
                cursor_pos > 0 and
                current_value[cursor_pos - 1] not in '.+-/*' and 
                self._lenght_max(current_value)):
                self._entrada.insert(cursor_pos, dot)
                self._entrada.icursor(cursor_pos + 1)
            elif cursor_pos == 0 or current_value[cursor_pos - 1] in '+-*/(':
                # Add "0." after operator
                self._entrada.insert(cursor_pos, '0.')
                self._entrada.icursor(cursor_pos + 2)
        except Exception as e:
            print(f"Error inputting decimal point: {e}")

    def _set_open_parent(self):
        """Method to set opening parenthesis in input"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Error':
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
            print(f"Error inputting left parenthesis: {e}")
    
    def _set_close_parent(self):
        """Method to set closing parenthesis in input"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Error':
                return

            # Check parenthesis balance
            open_count = current_value.count('(')
            close_count = current_value.count(')')
            
            if open_count <= close_count:
                return  # Already balanced or too many closing parentheses
                
            if (cursor_pos > 0 and 
                current_value[cursor_pos - 1] not in '+-/*(' and 
                self._lenght_max(current_value)):
                self._entrada.insert(cursor_pos, ')')
                self._entrada.icursor(cursor_pos + 1)
        except Exception as e:
            print(f"Error inputting right parenthesis: {e}")

    def _clear_input(self):
        """Reset calculator input, completely clearing it and inserting value 0"""
        try:
            self._entrada.delete(0, tk.END)
            self._entrada.insert(0, 0)
            self._entrada.icursor(1)  # Move cursor after 0
        except Exception as e:
            print(f"Error clearing input: {e}")
    
    def _del_last_value_in_input(self):
        """Delete character before cursor"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Error':
                self._clear_input()
                return

            if cursor_pos > 0:
                self._entrada.delete(cursor_pos - 1)
                self._entrada.icursor(cursor_pos - 1)
            
            # If empty after deletion, set to 0
            if not self._entrada.get():
                self._entrada.insert(0, 0)
                self._entrada.icursor(1)
        except Exception as e:
            print(f"Error deleting character: {e}")
    
    def _set_operator_in_input(self, operator):
        """Method responsible for capturing the clicked mathematical operator and setting it in input"""
        try:
            current_value = self._entrada.get()
            cursor_pos = self._entrada.index(tk.INSERT)
            
            if current_value == 'Error':
                return

            if current_value == '' or current_value == '0':
                if operator == '-':  # Allow minus sign as first character
                    if current_value == '0':
                        self._entrada.delete(0, tk.END)
                    self._entrada.insert(0, '-')
                    self._entrada.icursor(1)
                return
                
            # Avoid consecutive operators, but allow minus sign
            if cursor_pos > 0:
                prev_char = current_value[cursor_pos - 1]
                if prev_char in '+-*/' and operator != '-':
                    return
                # If last is operator and current is minus, only allow in specific cases
                if prev_char in '+-*/' and operator == '-':
                    if prev_char == '-':  # Avoid consecutive minus signs
                        return
                        
            if self._lenght_max(current_value):
                self._entrada.insert(cursor_pos, operator)
                self._entrada.icursor(cursor_pos + len(operator))
        except Exception as e:
            print(f"Error inputting operator: {e}")
            
    def _get_data_in_input(self):
        """Get data with all operations contained within input
        to perform calculation and add to history"""
        try:
            current_value = self._entrada.get()
            
            if current_value == 'Error' or not current_value:
                return

            # Save calculation expression
            expression = current_value
            self._last_expression = expression
            
            result = self.calc.calculation(expression)
            self._set_result_in_input(result=result)
            
            # Add to history - add null value check
            if (self.history_manager and 
                result != 'Error' and 
                expression and 
                expression != '0'):
                self.history_manager.add_calculation(expression, result)
        except Exception as e:
            print(f"Error during calculation: {e}")
            self._entrada.delete(0, len(self._entrada.get()))
            self._entrada.insert(0, 'Error')

    def _set_result_in_input(self, result=0):
        """Set the result of entire operation within input"""
        try:
            self._entrada.delete(0, len(self._entrada.get()))
            self._entrada.insert(0, result)
            # Ensure cursor is at end of result
            self._entrada.icursor(tk.END)
        except Exception as e:
            print(f"Error setting result: {e}")

    def _lenght_max(self, data_in_input):
        """To check if input reached maximum character count"""
        try:
            return len(str(data_in_input)) < 15  # Changed to less than 15 instead of greater than or equal to 15
        except:
            return False
            
    def start(self):
        """Start calculator application"""
        print('\33[92mCalculator Tk Started. . .\33[m\n')
        if self.history_manager:
            print('\33[94mHistory feature enabled - Press H key or use menu to view history\33[m\n')
        else:
            print('\33[93mHistory feature not available\33[m\n')
        print('\33[96mNew features: Visible cursor + Enter key calculation + Full keyboard support\33[m\n')
        print('\33[95mShortcuts: Enter=calculate, Backspace=delete, C/Delete/Esc=clear, Ctrl+H=history\33[m\n')
        self.master.mainloop()
    
    def _realod_app(self):
        """Restart the application."""
        try:
            python = sys.executable  # Retrieve python executable path
            os.execl(python, python, *sys.argv)
        except Exception as e:
            print(f"Failed to restart application: {e}")
            messagebox.showerror("Error", f"Failed to restart application: {e}")

    def _exit(self):
        """Safely exit application"""
        try:
            self.master.quit()
            self.master.destroy()
        except:
            exit()
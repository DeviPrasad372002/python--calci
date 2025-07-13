# -*- coding: utf-8 -*-

# @author: History Feature Extension
# History window interface

import tkinter as tk
from tkinter import ttk, messagebox, StringVar
from functools import partial
from typing import Callable, List, Dict, Any

class HistoryWindow:
    """History window class, provides GUI interface for history records"""
    
    def __init__(self, parent, history_manager, theme: Dict, on_use_calculation: Callable):
        self.parent = parent
        self.history_manager = history_manager
        self.theme = theme
        self.on_use_calculation = on_use_calculation
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.setup_window()
        
        # Search variable
        self.search_var = StringVar()
        self.search_var.trace('w', self._on_search_change)
        
        # Currently displayed history
        self.current_history = []
        
        self._create_interface()
        self._load_history()
    
    def setup_window(self):
        """Set window properties"""
        self.window.title('Calculation History')
        self.window.geometry('600x500')
        self.window.minsize(500, 400)
        self.window.configure(bg=self.theme.get('master_bg', '#252729'))
        
        # Set window icon and properties
        self.window.transient(self.parent)
        self.window.grab_set()  # Modal window
        
        # Center display
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f'600x500+{x}+{y}')
    
    def _create_interface(self):
        """Create interface elements"""
        # Main frame
        main_frame = tk.Frame(self.window, bg=self.theme.get('frame_bg', '#252729'))
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top frame - title and search
        top_frame = tk.Frame(main_frame, bg=self.theme.get('frame_bg', '#252729'))
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            top_frame,
            text='Calculation History',
            font=('Arial', 16, 'bold'),
            bg=self.theme.get('frame_bg', '#252729'),
            fg=self.theme.get('INPUT', {}).get('fg', '#ffffff')
        )
        title_label.pack(side='left')
        
        # Search frame
        search_frame = tk.Frame(top_frame, bg=self.theme.get('frame_bg', '#252729'))
        search_frame.pack(side='right')
        
        tk.Label(
            search_frame,
            text='Search:',
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
        
        # Middle frame - history list
        middle_frame = tk.Frame(main_frame, bg=self.theme.get('frame_bg', '#252729'))
        middle_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create Treeview to display history
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Treeview style
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
        
        # Create Treeview
        columns = ('expression', 'result', 'time')
        self.tree = ttk.Treeview(
            middle_frame,
            columns=columns,
            show='headings',
            style='History.Treeview'
        )
        
        # Define columns
        self.tree.heading('expression', text='Expression')
        self.tree.heading('result', text='Result')
        self.tree.heading('time', text='Time')
        
        self.tree.column('expression', width=200, anchor='w')
        self.tree.column('result', width=150, anchor='e')
        self.tree.column('time', width=180, anchor='center')
        
        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(middle_frame, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(middle_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        middle_frame.grid_rowconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self._on_item_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)  # Right-click menu
        
        # Bottom frame - buttons
        bottom_frame = tk.Frame(main_frame, bg=self.theme.get('frame_bg', '#252729'))
        bottom_frame.pack(fill='x')
        
        # Statistics information
        self.stats_label = tk.Label(
            bottom_frame,
            text='',
            bg=self.theme.get('frame_bg', '#252729'),
            fg=self.theme.get('INPUT', {}).get('fg', '#ffffff'),
            font=('Arial', 9)
        )
        self.stats_label.pack(side='left')
        
        # Button frame
        button_frame = tk.Frame(bottom_frame, bg=self.theme.get('frame_bg', '#252729'))
        button_frame.pack(side='right')
        
        # Button configuration
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
        
        # Use button
        self.use_btn = tk.Button(
            button_frame,
            text='Use',
            command=self._use_selected,
            **btn_config
        )
        self.use_btn.pack(side='left', padx=(0, 5))
        
        # Delete button
        self.delete_btn = tk.Button(
            button_frame,
            text='Delete',
            command=self._delete_selected,
            **btn_config
        )
        self.delete_btn.pack(side='left', padx=(0, 5))
        
        # Clear button
        self.clear_btn = tk.Button(
            button_frame,
            text='Clear All',
            command=self._clear_all,
            **btn_config
        )
        self.clear_btn.pack(side='left', padx=(0, 5))
        
        # Close button
        self.close_btn = tk.Button(
            button_frame,
            text='Close',
            command=self.window.destroy,
            **btn_config
        )
        self.close_btn.pack(side='left')
        
        # Create right-click menu
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="Use this calculation", command=self._use_selected)
        self.context_menu.add_command(label="Copy expression", command=self._copy_expression)
        self.context_menu.add_command(label="Copy result", command=self._copy_result)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self._delete_selected)
    
    def _load_history(self):
        """Load and display history"""
        history = self.history_manager.get_history()
        self.current_history = history
        self._update_tree_view(history)
        self._update_statistics()
    
    def _update_tree_view(self, history_list: List[Dict]):
        """Update tree view"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add history records
        for calc in history_list:
            self.tree.insert('', 'end', values=(
                calc['expression'],
                calc['result'],
                calc['date_formatted']
            ), tags=(str(calc['id']),))
    
    def _update_statistics(self):
        """Update statistics information"""
        stats = self.history_manager.get_statistics()
        if stats['total_calculations'] > 0:
            text = f"Total calculations: {stats['total_calculations']}"
            if len(self.current_history) != stats['total_calculations']:
                text += f" (Showing: {len(self.current_history)})"
        else:
            text = "No calculation records"
        
        self.stats_label.config(text=text)
    
    def _on_search_change(self, *args):
        """Callback when search box content changes"""
        query = self.search_var.get()
        filtered_history = self.history_manager.search_history(query)
        self.current_history = filtered_history
        self._update_tree_view(filtered_history)
        self._update_statistics()
    
    def _on_item_double_click(self, event):
        """Use calculation when item is double-clicked"""
        self._use_selected()
    
    def _on_right_click(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _get_selected_calculation(self) -> Dict:
        """Get selected calculation record"""
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
        """Use selected calculation"""
        calc = self._get_selected_calculation()
        if calc:
            self.on_use_calculation(calc['expression'], calc['result'])
            self.window.destroy()
        else:
            messagebox.showwarning("Warning", "Please select a calculation record first")
    
    def _delete_selected(self):
        """Delete selected calculation"""
        calc = self._get_selected_calculation()
        if calc:
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete calculation '{calc['expression']} = {calc['result']}'?"):
                if self.history_manager.delete_calculation(calc['id']):
                    self._load_history()
                    messagebox.showinfo("Success", "Calculation record deleted")
                else:
                    messagebox.showerror("Error", "Delete failed")
        else:
            messagebox.showwarning("Warning", "Please select a calculation record first")
    
    def _clear_all(self):
        """Clear all history records"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all history? This action cannot be undone!"):
            self.history_manager.clear_history()
            self._load_history()
            messagebox.showinfo("Success", "All history records have been cleared")
    
    def _copy_expression(self):
        """Copy expression to clipboard"""
        calc = self._get_selected_calculation()
        if calc:
            self.window.clipboard_clear()
            self.window.clipboard_append(calc['expression'])
            messagebox.showinfo("Success", "Expression copied to clipboard")
        else:
            messagebox.showwarning("Warning", "Please select a calculation record first")
    
    def _copy_result(self):
        """Copy result to clipboard"""
        calc = self._get_selected_calculation()
        if calc:
            self.window.clipboard_clear()
            self.window.clipboard_append(calc['result'])
            messagebox.showinfo("Success", "Result copied to clipboard")
        else:
            messagebox.showwarning("Warning", "Please select a calculation record first")
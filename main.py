import customtkinter as ctk
import math

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.title("Modern Calculator")
window.geometry("400x500")

# Global durum değişkenleri
scientific_mode = False
current_function = None  # Aktif fonksiyon adı: "sqrt", "log", "sin", "cos", vb.
current_arg = ""         # Fonksiyon için girilen argüman
arg_index = None         # Giriş alanında argümanın başlama indeksi

# Girdi alanı
entry = ctk.CTkEntry(window, width=300, height=50, font=("Arial", 24), justify="right")
entry.grid(row=0, column=0, columnspan=4, pady=15, padx=10)

# Bilimsel fonksiyon tuşuna basıldığında: giriş alanını fonksiyon ifadesiyle doldurur ve argüman giriş indeksi ayarlanır.
def set_math_function(func):
    global current_function, current_arg, arg_index
    current_function = func
    current_arg = ""
    expr = f"math.{func}()"
    entry.delete(0, "end")
    entry.insert("end", expr)
    # Argüman, açılış parantezden hemen sonra başlar.
    arg_index = len(f"math.{func}(")

# Rakam veya nokta tuşlarına basıldığında:
def insert_digit(value):
    global current_function, current_arg, arg_index
    if current_function is not None and arg_index is not None:
        content = entry.get()
        # Eğer içerik zaten kapanış parantezini içeriyorsa, kaldırıp yeniden ekleyeceğiz.
        if content.endswith(")"):
            content = content[:-1]
        # İstenen değeri arg_index pozisyonunda ekle
        new_content = content[:arg_index] + value + content[arg_index:]
        current_arg += value
        arg_index += len(value)
        entry.delete(0, "end")
        entry.insert("end", new_content + ")")
    else:
        entry.insert("end", value)

# Operatör tuşuna basıldığında; eğer aktif bir fonksiyon varsa ifadenin sonuna kapanış parantezi eklenir.
def insert_operator(value):
    global current_function, current_arg, arg_index
    if current_function is not None:
        # Eğer kapanış parantezi yoksa (ama bizim yapımızda her zaman var), yine de tamamla.
        content = entry.get()
        if not content.endswith(")"):
            entry.delete(0, "end")
            entry.insert("end", content + ")")
        current_function = None
        current_arg = ""
        arg_index = None
    entry.insert("end", value)

# Girdi alanını temizle
def clear_entry():
    global current_function, current_arg, arg_index
    entry.delete(0, "end")
    current_function = None
    current_arg = ""
    arg_index = None

# Hesaplamayı yap; eğer aktif fonksiyon varsa ifadenin sonunu kapatır.
def calculate():
    global current_function, current_arg, arg_index
    expr = entry.get()
    if current_function is not None:
        if not expr.strip().endswith(")"):
            expr += ")"
        current_function = None
        current_arg = ""
        arg_index = None
    try:
        result = eval(expr, {"math": math})
        entry.delete(0, "end")
        entry.insert("end", str(result))
    except Exception as e:
        entry.delete(0, "end")
        entry.insert("end", "Error")

# Standart hesap makinesi tuşları
buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
    ('0', 4, 0), ('.', 4, 1), ('+', 4, 2), ('=', 4, 3)
]

for (text, row, col) in buttons:
    if text == "=":
        ctk.CTkButton(window, text=text, width=70, height=50, font=("Arial", 18),
                      command=calculate, fg_color="#4CAF50").grid(row=row, column=col, pady=5, padx=5)
    elif text in {"+", "-", "*", "/"}:
        ctk.CTkButton(window, text=text, width=70, height=50, font=("Arial", 18),
                      command=lambda t=text: insert_operator(t)).grid(row=row, column=col, pady=5, padx=5)
    else:
        ctk.CTkButton(window, text=text, width=70, height=50, font=("Arial", 18),
                      command=lambda t=text: insert_digit(t)).grid(row=row, column=col, pady=5, padx=5)

# Clear butonu
ctk.CTkButton(window, text="Clear", width=150, height=50, font=("Arial", 18),
              command=clear_entry, fg_color="#F44336").grid(row=5, column=0, columnspan=2, pady=5, padx=5)

# Bilimsel mod tuşları: "log", "√", "x^y", "sin", "cos"
def enable_scientific_mode():
    global scientific_mode
    if not scientific_mode:
        ctk.CTkButton(window, text="log", width=70, height=50, font=("Arial", 18),
                      command=lambda: set_math_function("log")).grid(row=1, column=4, pady=5, padx=5)
        ctk.CTkButton(window, text="√", width=70, height=50, font=("Arial", 18),
                      command=lambda: set_math_function("sqrt")).grid(row=2, column=4, pady=5, padx=5)
        ctk.CTkButton(window, text="x^y", width=70, height=50, font=("Arial", 18),
                      command=lambda: insert_operator("**")).grid(row=3, column=4, pady=5, padx=5)
        ctk.CTkButton(window, text="sin", width=70, height=50, font=("Arial", 18),
                      command=lambda: set_math_function("sin")).grid(row=4, column=4, pady=5, padx=5)
        ctk.CTkButton(window, text="cos", width=70, height=50, font=("Arial", 18),
                      command=lambda: set_math_function("cos")).grid(row=5, column=4, pady=5, padx=5)
        window.geometry("600x500")
        scientific_mode = True

ctk.CTkButton(window, text="Scientific Mode", width=150, height=50, font=("Arial", 18),
              command=enable_scientific_mode, fg_color="#008CBA").grid(row=5, column=2, columnspan=2, pady=5, padx=5)

window.mainloop()

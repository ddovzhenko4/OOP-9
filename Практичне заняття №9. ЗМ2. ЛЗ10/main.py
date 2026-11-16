import math
import tkinter as tk
from tkinter import messagebox


class TabulationApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Табулювання функції")
        self.root.geometry("920x520")

        # Змінні стану прапорців (CheckBox)
        self.var_screen = tk.BooleanVar(value=True)   # На екран
        self.var_file = tk.BooleanVar(value=False)    # У файл
        self.var_array = tk.BooleanVar(value=True)    # У масив
        self.var_deriv = tk.BooleanVar(value=False)   # Похідна

        self.last_points = []

        self._build_menus()
        self._build_ui()

    def _build_menus(self):
        # Головне меню (MainMenu)
        main_menu = tk.Menu(self.root)

        calc_menu = tk.Menu(main_menu, tearoff=0)
        calc_menu.add_command(label="Протабулювати", command=self.tabulate)
        calc_menu.add_command(label="Очистити поле виведення", command=self.clear_memo)
        main_menu.add_cascade(label="Обчислення", menu=calc_menu)

        end_menu = tk.Menu(main_menu, tearoff=0)
        end_menu.add_command(label="Про програму", command=self.show_about)
        end_menu.add_command(label="Вийти", command=self.root.quit)
        main_menu.add_cascade(label="Кінець", menu=end_menu)

        self.root.config(menu=main_menu)

        # Контекстне меню форми (PopupMenu1)
        self.popup_main = tk.Menu(self.root, tearoff=0)
        self.popup_main.add_command(label="Очистити поле виведення", command=self.clear_memo)
        self.popup_main.add_command(label="Вийти", command=self.root.quit)

        # Контекстне меню панелі прапорців (PopupMenu2)
        self.popup_group = tk.Menu(self.root, tearoff=0)
        self.popup_group.add_command(label="Зняти всі прапорці", command=self.uncheck_all)
        self.popup_group.add_command(label="Встановити всі прапорці", command=self.check_all)
        self.popup_group.add_command(label="Встановити інверсивно", command=self.invert_checks)

    def _build_ui(self):
        # Заголовок формули по центру
        lbl_func = tk.Label(self.root, text="y = sin(x) + 1", font=("Arial", 20, "bold"))
        lbl_func.pack(pady=(10, 8))

        content = tk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # 1. Багаторядкове поле виведення (Memo зі ScrollBars = ssBoth)
        memo_frame = tk.Frame(content)
        memo_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        scroll_y = tk.Scrollbar(memo_frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(memo_frame, orient=tk.HORIZONTAL)

        self.memo = tk.Text(
            memo_frame,
            width=32,
            wrap="none",
            font=("Consolas", 10),
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )
        scroll_y.config(command=self.memo.yview)
        scroll_x.config(command=self.memo.xview)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.memo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 2. Центральна колонка: GroupBox, CheckBox та поля Edit1..3
        controls_frame = tk.Frame(content)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=14)

        group_box = tk.LabelFrame(controls_frame, text="Виведення", padx=10, pady=6)
        group_box.pack(fill=tk.X)

        cb1 = tk.Checkbutton(group_box, text="На екран", variable=self.var_screen)
        cb2 = tk.Checkbutton(group_box, text="У файл", variable=self.var_file)
        cb3 = tk.Checkbutton(group_box, text="У масив", variable=self.var_array)
        for cb in (cb1, cb2, cb3):
            cb.pack(anchor="w")

        # Прапорець "Похідна" зі шрифтом 12 розміру
        cb_deriv = tk.Checkbutton(
            controls_frame,
            text="Похідна",
            variable=self.var_deriv,
            font=("Arial", 12),
        )
        cb_deriv.pack(anchor="w", pady=(8, 10))

        # Поля введення меж і кроку
        tk.Label(controls_frame, text="Ліва межа").pack(anchor="w")
        self.edit_a = tk.Entry(controls_frame, width=16)
        self.edit_a.insert(0, "1")
        self.edit_a.pack(anchor="w", pady=(0, 6))

        tk.Label(controls_frame, text="Права межа").pack(anchor="w")
        self.edit_b = tk.Entry(controls_frame, width=16)
        self.edit_b.insert(0, "2")
        self.edit_b.pack(anchor="w", pady=(0, 6))

        tk.Label(controls_frame, text="Крок").pack(anchor="w")
        self.edit_h = tk.Entry(controls_frame, width=16)
        self.edit_h.insert(0, "0.1")
        self.edit_h.pack(anchor="w", pady=(0, 12))

        # 3. Область графіка (аналог Chart)
        self.canvas = tk.Canvas(content, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw_chart(self.last_points))

        # Прив'язка контекстних меню
        self.root.bind("<Button-3>", self._show_main_popup)
        self.root.bind("<Button-2>", self._show_main_popup)

        for widget in (group_box, cb1, cb2, cb3):
            widget.bind("<Button-3>", self._show_group_popup)
            widget.bind("<Button-2>", self._show_group_popup)

    def _show_main_popup(self, event):
        self.popup_main.tk_popup(event.x_root, event.y_root)

    def _show_group_popup(self, event):
        self.popup_group.tk_popup(event.x_root, event.y_root)
        return "break"  # Блокує відкриття головного контекстного меню поверх цього

    # Обробники команд меню
    def clear_memo(self):
        self.memo.delete("1.0", tk.END)

    def show_about(self):
        messagebox.showinfo("Про програму", "Програма табулювання функції y = sin(x) + 1")

    def uncheck_all(self):
        self.var_screen.set(False)
        self.var_file.set(False)
        self.var_array.set(False)

    def check_all(self):
        self.var_screen.set(True)
        self.var_file.set(True)
        self.var_array.set(True)

    def invert_checks(self):
        self.var_screen.set(not self.var_screen.get())
        self.var_file.set(not self.var_file.get())
        self.var_array.set(not self.var_array.get())

    def tabulate(self):
        try:
            a = float(self.edit_a.get().replace(",", "."))
            b = float(self.edit_b.get().replace(",", "."))
            h = float(self.edit_h.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Помилка", "Введи коректні числові значення!")
            return

        if h <= 0 or a > b:
            messagebox.showerror("Помилка", "Крок має бути > 0, а ліва межа <= правої!")
            return

        y_array = []          # Одновимірний масив значень Y
        points = []
        max_y = math.sin(a) + 1
        min_y = math.sin(a) + 1
        count_range = 0       # Кількість елементів у (0.5; 1)

        header = "X\tY\tY'" if self.var_deriv.get() else "X\tY"
        rows = [header]

        x = a
        while x <= b + h / 2.0:
            y = math.sin(x) + 1
            dy = math.cos(x)  # Похідна від sin(x) + 1 

            # Визначення min та max
            if y > max_y:
                max_y = y
            if y < min_y:
                min_y = y

            # Підрахунок елементів
            if 0.5 < y < 1.0:
                count_range += 1

            # Збереження у масив
            if self.var_array.get():
                y_array.append(y)

            if self.var_deriv.get():
                rows.append(f"{x:.2f}\t{y:.2f}\t{dy:.2f}")
            else:
                rows.append(f"{x:.2f}\t{y:.2f}")

            points.append((x, y))
            x += h

        # Виведення на екран
        if self.var_screen.get():
            for row in rows:
                self.memo.insert(tk.END, row + "\n")
            self.memo.insert(tk.END, "-" * 24 + "\n")
            self.memo.insert(tk.END, f"Max = {max_y:.2f}\n")
            self.memo.insert(tk.END, f"Min = {min_y:.2f}\n")
            self.memo.insert(tk.END, f"Елементів у (0.5; 1): {count_range}\n")
            if self.var_array.get():
                self.memo.insert(tk.END, f"Записано в масив: {len(y_array)} ел.\n")

        # Виведення у файл
        if self.var_file.get():
            with open("result.txt", "w", encoding="utf-8") as f:
                for row in rows:
                    f.write(row + "\n")

        # Побудова графіка разом із табулюванням
        self.last_points = points
        self.draw_chart(points)

    def draw_chart(self, points):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            return

        # Заголовок графіка (Title)
        self.canvas.create_text(
            w // 2,
            18,
            text="Графік функції y = sin(x) + 1",
            fill="blue",
            font=("Arial", 11, "bold"),
        )

        pad_left, pad_right, pad_top, pad_bottom = 45, 20, 38, 35
        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom

        self.canvas.create_rectangle(
            pad_left, pad_top, w - pad_right, h - pad_bottom, outline="#888"
        )

        if len(points) < 2:
            return

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        dx = (max_x - min_x) or 1.0
        dy = (max_y - min_y) or 1.0

        # Координатна сітка та підписи осей
        steps = 5
        for i in range(steps + 1):
            gx = pad_left + (plot_w * i / steps)
            gy = h - pad_bottom - (plot_h * i / steps)
            val_x = min_x + dx * i / steps
            val_y = min_y + dy * i / steps

            self.canvas.create_line(gx, pad_top, gx, h - pad_bottom, fill="#eee", dash=(2, 2))
            self.canvas.create_line(pad_left, gy, w - pad_right, gy, fill="#eee", dash=(2, 2))

            self.canvas.create_text(gx, h - pad_bottom + 14, text=f"{val_x:.2f}", font=("Arial", 8))
            self.canvas.create_text(pad_left - 22, gy, text=f"{val_y:.2f}", font=("Arial", 8))

        # Масштабування точок та малювання кривої графіка
        coords = []
        for px, py in points:
            cx = pad_left + ((px - min_x) / dx) * plot_w
            cy = h - pad_bottom - ((py - min_y) / dy) * plot_h
            coords.extend([cx, cy])

        self.canvas.create_line(*coords, fill="red", width=2)


if __name__ == "__main__":
    root = tk.Tk()
    app = TabulationApp(root)
    root.mainloop()
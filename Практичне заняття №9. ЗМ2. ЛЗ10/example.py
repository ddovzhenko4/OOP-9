import math
import tkinter as tk
from tkinter import messagebox


class CarDepreciationApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AutoMatch — Табулювання вартості автомобіля")
        self.root.geometry("960x540")

        # Коефіцієнт річної амортизації (15%)
        self.k = 0.15

        # Змінні прапорців (CheckBox)
        self.var_screen = tk.BooleanVar(value=True)   # На екран
        self.var_file = tk.BooleanVar(value=False)    # У файл
        self.var_array = tk.BooleanVar(value=True)    # У масив
        self.var_deriv = tk.BooleanVar(value=False)   # Похідна (втрата $/рік)

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

        # Контекстне меню форми (PopupMenu1 + команда "Вийти")
        self.popup_main = tk.Menu(self.root, tearoff=0)
        self.popup_main.add_command(label="Очистити поле виведення", command=self.clear_memo)
        self.popup_main.add_command(label="Вийти", command=self.root.quit)

        # Контекстне меню панелі прапорців (PopupMenu2)
        self.popup_group = tk.Menu(self.root, tearoff=0)
        self.popup_group.add_command(label="Зняти всі прапорці", command=self.uncheck_all)
        self.popup_group.add_command(label="Встановити всі прапорці", command=self.check_all)
        self.popup_group.add_command(label="Встановити інверсивно", command=self.invert_checks)

    def _build_ui(self):
        # Заголовок із математичною моделлю знецінення авто
        lbl_func = tk.Label(
            self.root,
            text="P(t) = P₀ · e^(-0.15 · t)",
            font=("Arial", 18, "bold"),
        )
        lbl_func.pack(pady=(10, 8))

        content = tk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # 1. Багаторядкове поле виведення (аналог Memo зі ScrollBars = ssBoth)
        memo_frame = tk.Frame(content)
        memo_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        scroll_y = tk.Scrollbar(memo_frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(memo_frame, orient=tk.HORIZONTAL)

        self.memo = tk.Text(
            memo_frame,
            width=36,
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

        # 2. Центральна панель: GroupBox, CheckBox та поля Edit
        controls_frame = tk.Frame(content)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=14)

        group_box = tk.LabelFrame(controls_frame, text="Виведення", padx=10, pady=6)
        group_box.pack(fill=tk.X)

        cb1 = tk.Checkbutton(group_box, text="На екран", variable=self.var_screen)
        cb2 = tk.Checkbutton(group_box, text="У файл", variable=self.var_file)
        cb3 = tk.Checkbutton(group_box, text="У масив", variable=self.var_array)
        for cb in (cb1, cb2, cb3):
            cb.pack(anchor="w")

        cb_deriv = tk.Checkbutton(
            controls_frame,
            text="Похідна (втрата $/рік)",
            variable=self.var_deriv,
            font=("Arial", 12),
        )
        cb_deriv.pack(anchor="w", pady=(8, 10))

        # Поля введення параметрів автомобіля та інтервалу табулювання
        tk.Label(controls_frame, text="Початкова ціна P₀ ($)").pack(anchor="w")
        self.edit_p0 = tk.Entry(controls_frame, width=18)
        self.edit_p0.insert(0, "20000")
        self.edit_p0.pack(anchor="w", pady=(0, 6))

        tk.Label(controls_frame, text="Ліва межа (вік, р.)").pack(anchor="w")
        self.edit_a = tk.Entry(controls_frame, width=18)
        self.edit_a.insert(0, "0")
        self.edit_a.pack(anchor="w", pady=(0, 6))

        tk.Label(controls_frame, text="Права межа (вік, р.)").pack(anchor="w")
        self.edit_b = tk.Entry(controls_frame, width=18)
        self.edit_b.insert(0, "5")
        self.edit_b.pack(anchor="w", pady=(0, 6))

        tk.Label(controls_frame, text="Крок (р.)").pack(anchor="w")
        self.edit_h = tk.Entry(controls_frame, width=18)
        self.edit_h.insert(0, "0.5")
        self.edit_h.pack(anchor="w", pady=(0, 12))

        # 3. Область графіка (аналог Chart)
        self.canvas = tk.Canvas(content, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw_chart(self.last_points))

        # Прив'язка контекстних меню (права кнопка миші)
        self.root.bind("<Button-3>", self._show_main_popup)
        self.root.bind("<Button-2>", self._show_main_popup)

        for widget in (group_box, cb1, cb2, cb3):
            widget.bind("<Button-3>", self._show_group_popup)
            widget.bind("<Button-2>", self._show_group_popup)

    def _show_main_popup(self, event):
        self.popup_main.tk_popup(event.x_root, event.y_root)

    def _show_group_popup(self, event):
        self.popup_group.tk_popup(event.x_root, event.y_root)
        return "break"

    def clear_memo(self):
        self.memo.delete("1.0", tk.END)

    def show_about(self):
        messagebox.showinfo(
            "Про програму",
            "Модуль прогнозування амортизації авто для ІС «AutoMatch».\n"
            "Модель: P(t) = P0 * exp(-0.15 * t)",
        )

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
            p0 = float(self.edit_p0.get().replace(",", "."))
            a = float(self.edit_a.get().replace(",", "."))
            b = float(self.edit_b.get().replace(",", "."))
            h = float(self.edit_h.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Помилка", "Введи коректні числові значення!")
            return

        if p0 <= 0 or h <= 0 or a < 0 or a > b:
            messagebox.showerror("Помилка", "Перевір межі віку, ціну (> 0) та крок (> 0)!")
            return

        price_array = []      # Одновимірний масив значень ціни
        points = []
        max_price = p0 * math.exp(-self.k * a)
        min_price = max_price
        in_budget_count = 0   # Кількість точок у бюджеті (10000; 15000) $

        header = "Вік\tЦіна ($)\tВтрата/рік" if self.var_deriv.get() else "Вік\tЦіна ($)"
        rows = [header]

        t = a
        while t <= b + h / 2.0:
            price = p0 * math.exp(-self.k * t)
            d_price = -self.k * p0 * math.exp(-self.k * t)  # Похідна P'(t)

            # Визначення мінімальної та максимальної ціни на інтервалі
            if price > max_price:
                max_price = price
            if price < min_price:
                min_price = price

            # Підрахунок елементів у цільовому бюджеті (10 000; 15 000)
            if 10000.0 < price < 15000.0:
                in_budget_count += 1

            # Запис у масив за увімкненого прапорця "У масив"
            if self.var_array.get():
                price_array.append(round(price, 2))

            if self.var_deriv.get():
                rows.append(f"{t:.1f}\t{price:.2f}\t{d_price:.2f}")
            else:
                rows.append(f"{t:.1f}\t{price:.2f}")

            points.append((t, price))
            t += h

        # Виведення результатів на екран у Memo
        if self.var_screen.get():
            for row in rows:
                self.memo.insert(tk.END, row + "\n")
            self.memo.insert(tk.END, "-" * 30 + "\n")
            self.memo.insert(tk.END, f"Max ціна = {max_price:.2f} $\n")
            self.memo.insert(tk.END, f"Min ціна = {min_price:.2f} $\n")
            self.memo.insert(tk.END, f"У бюджеті (10k–15k $): {in_budget_count}\n")
            if self.var_array.get():
                self.memo.insert(tk.END, f"У масиві збережено: {len(price_array)} ел.\n")

        # Збереження таблиці у файл
        if self.var_file.get():
            with open("car_price_tabulation.txt", "w", encoding="utf-8") as f:
                for row in rows:
                    f.write(row + "\n")

        # Побудова графіка знецінення авто
        self.last_points = points
        self.draw_chart(points)

    def draw_chart(self, points):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            return

        self.canvas.create_text(
            w // 2,
            18,
            text="Графік зниження вартості автомобіля P(t)",
            fill="blue",
            font=("Arial", 11, "bold"),
        )

        pad_left, pad_right, pad_top, pad_bottom = 60, 20, 38, 35
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

        steps = 5
        for i in range(steps + 1):
            gx = pad_left + (plot_w * i / steps)
            gy = h - pad_bottom - (plot_h * i / steps)
            val_x = min_x + dx * i / steps
            val_y = min_y + dy * i / steps

            self.canvas.create_line(gx, pad_top, gx, h - pad_bottom, fill="#eee", dash=(2, 2))
            self.canvas.create_line(pad_left, gy, w - pad_right, gy, fill="#eee", dash=(2, 2))

            self.canvas.create_text(gx, h - pad_bottom + 14, text=f"{val_x:.1f} р.", font=("Arial", 8))
            self.canvas.create_text(pad_left - 28, gy, text=f"{val_y:.0f}$", font=("Arial", 8))

        coords = []
        for px, py in points:
            cx = pad_left + ((px - min_x) / dx) * plot_w
            cy = h - pad_bottom - ((py - min_y) / dy) * plot_h
            coords.extend([cx, cy])

        self.canvas.create_line(*coords, fill="red", width=2)


if __name__ == "__main__":
    root = tk.Tk()
    app = CarDepreciationApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

DATA_FILE = "weather_data.json"


class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x500")

        # Хранилище записей
        self.entries = []
        self.load_from_file()

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_view()
        self.create_button_frame()

        # Обновить отображение
        self.refresh_display()

    def create_input_frame(self):
        """Поля ввода новой записи"""
        input_frame = tk.LabelFrame(self.root, text="Добавить новую запись", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Температура
        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.temp_entry = tk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Осадки (переместил на первую строку)
        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="Есть осадки", variable=self.precip_var).grid(row=0, column=4, padx=10, pady=5)

        # Описание
        tk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.desc_entry = tk.Entry(input_frame, width=50)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Кнопка добавления (теперь в отдельном ряду)
        self.add_btn = tk.Button(input_frame, text="Добавить запись", command=self.add_entry, bg="#4CAF50", fg="white")
        self.add_btn.grid(row=2, column=0, columnspan=5, pady=10)

        # Настройка растягивания колонок
        input_frame.columnconfigure(1, weight=1)

    def create_filter_frame(self):
        """Фрейм фильтрации"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация записей", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по дате
        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=20)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по температуре
        tk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Кнопки фильтрации и сброса
        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=4, padx=5, pady=5)

        self.reset_btn = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_btn.grid(row=0, column=5, padx=5, pady=5)

    def create_tree_view(self):
        """Таблица для отображения записей"""
        # Создаем фрейм для таблицы и скролла
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("id", width=50)
        self.tree.column("date", width=120)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_button_frame(self):
        """Кнопки сохранения/загрузки"""
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.save_btn = tk.Button(btn_frame, text="Сохранить в JSON", command=self.save_to_file, bg="#2196F3",
                                  fg="white")
        self.save_btn.pack(side="left", padx=5)

        self.load_btn = tk.Button(btn_frame, text="Загрузить из JSON", command=self.load_from_file_ui, bg="#FF9800",
                                  fg="white")
        self.load_btn.pack(side="left", padx=5)

        self.delete_btn = tk.Button(btn_frame, text="Удалить выбранное", command=self.delete_selected, bg="#f44336",
                                    fg="white")
        self.delete_btn.pack(side="left", padx=5)

        # Добавил кнопку редактирования
        self.edit_btn = tk.Button(btn_frame, text="Редактировать", command=self.edit_selected, bg="#9C27B0", fg="white")
        self.edit_btn.pack(side="left", padx=5)

    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_entry(self):
        """Добавление записи с проверкой ввода"""
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()

        # Проверка даты
        if not date:
            messagebox.showerror("Ошибка", "Дата не может быть пустой")
            return
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        # Проверка температуры
        if not temp_str:
            messagebox.showerror("Ошибка", "Температура не может быть пустой")
            return
        try:
            temperature = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        # Проверка описания
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        # Создание ID
        new_id = max([e["id"] for e in self.entries], default=0) + 1

        # Добавление записи
        entry = {
            "id": new_id,
            "date": date,
            "temperature": temperature,
            "description": desc,
            "precipitation": precipitation
        }
        self.entries.append(entry)

        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

        self.refresh_display()
        messagebox.showinfo("Успех", "Запись добавлена")

    def edit_selected(self):
        """Редактирование выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования")
            return

        item = self.tree.item(selected[0])
        entry_id = int(item["values"][0])

        # Находим запись
        entry = next((e for e in self.entries if e["id"] == entry_id), None)
        if entry:
            # Заполняем поля для редактирования
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, entry["date"])
            self.temp_entry.delete(0, tk.END)
            self.temp_entry.insert(0, str(entry["temperature"]))
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, entry["description"])
            self.precip_var.set(entry["precipitation"])

            # Удаляем старую запись
            self.entries = [e for e in self.entries if e["id"] != entry_id]
            self.refresh_display()

            messagebox.showinfo("Редактирование", "Теперь вы можете изменить запись и нажать 'Добавить запись'")

    def refresh_display(self, filtered_entries=None):
        """Обновление таблицы"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        display_entries = filtered_entries if filtered_entries is not None else self.entries

        # Сортируем по дате (новые сверху)
        display_entries = sorted(display_entries, key=lambda x: x["date"], reverse=True)

        for entry in display_entries:
            precip_text = "Да" if entry["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                entry["id"],
                entry["date"],
                entry["temperature"],
                entry["description"],
                precip_text
            ))

    def apply_filter(self):
        """Применение фильтров"""
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered = self.entries[:]

        # Фильтр по дате
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты фильтра")
                return
            filtered = [e for e in filtered if e["date"] == filter_date]

        # Фильтр по температуре
        if filter_temp_str:
            try:
                temp_threshold = float(filter_temp_str)
                filtered = [e for e in filtered if e["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом")
                return

        self.refresh_display(filtered)

        if not filtered:
            messagebox.showinfo("Фильтр", "Нет записей, соответствующих фильтру")

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_display()

    def delete_selected(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        item = self.tree.item(selected[0])
        entry_id = int(item["values"][0])

        confirm = messagebox.askyesno("Подтверждение", "Удалить выбранную запись?")
        if confirm:
            self.entries = [e for e in self.entries if e["id"] != entry_id]
            self.refresh_display()
            messagebox.showinfo("Успех", "Запись удалена")

    def save_to_file(self):
        """Сохранение в JSON"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Сохранено в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_file(self):
        """Загрузка из JSON"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
                return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")
            return False
        return False

    def load_from_file_ui(self):
        """Загрузка из JSON """
        if self.load_from_file():
            self.refresh_display()
            messagebox.showinfo("Успех", f"Загружено из {DATA_FILE}")
        else:
            messagebox.showwarning("Предупреждение", "Файл не найден или пуст")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
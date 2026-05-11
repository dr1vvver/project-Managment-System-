from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import database
import db_products
import db_requests

class App:
    def __init__(self, root):
        self.root = root
        try:
            self.root.iconbitmap("Наш декор.ico")
        except:
            pass
        self.root.title("Наш декор - Учёт продукции")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        
        self.container = Frame(root)
        self.container.pack(fill=BOTH, expand=True)
        
        self.screens = {}
        self.trees = {}
        self.requests_trees = {}
        self.partners_trees = {}
        
        self.current_user_id = None
        self.current_user_name = None
        self.current_role = None
        self.current_rating = None
        self.current_product_for_edit = None
        self.current_active_tree = None
        
        self.add_screen("main", self.create_main_screen)
        self.add_screen("login", self.create_login_screen)
        self.add_screen("partner_dashboard", self.create_partner_dashboard)
        self.add_screen("admin_dashboard", self.create_admin_dashboard)
        self.add_screen("manager_dashboard", self.create_manager_dashboard)
        
        self.show_screen("main")
    
    def add_screen(self, name, create_func):
        frame = Frame(self.container)
        frame.pack(fill=BOTH, expand=True)
        self.screens[name] = frame
        create_func(frame)
    
    def show_screen(self, name):
        for frame in self.screens.values():
            frame.pack_forget()
        self.screens[name].pack(fill=BOTH, expand=True)
        
        if name == "partner_dashboard":
            self.current_active_tree = "partner"
        elif name == "admin_dashboard":
            self.current_active_tree = "admin"
        elif name == "manager_dashboard":
            self.current_active_tree = "manager"
        
        if name in ["partner_dashboard", "admin_dashboard", "manager_dashboard"]:
            self.load_products(self.current_active_tree)
            if name != "partner_dashboard":
                self.load_partners()
    
    # ==================== ГЛАВНЫЙ ЭКРАН ====================
    def create_main_screen(self, frame):
        try:
            img = Image.open("Наш декор.png")
            img = img.resize((300, 150), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = Label(frame, image=logo_img)
            logo_label.image = logo_img
            logo_label.pack(pady=20)
        except:
            pass
        
        Label(frame, text="НАШ ДЕКОР", font=("Gabriola", 36, "bold"), fg="#2D6033").pack(pady=10)
        Label(frame, text="Производственная компания по выпуску обоев", font=("Gabriola", 24)).pack(pady=5)
        
        Button(frame, text="Войти", command=lambda: self.show_screen("login"),
               font=("Gabriola", 16), bg="#2D6033", fg="white", padx=30, pady=8).pack(pady=40)
        Button(frame, text="Выход", command=self.root.quit, font=("Gabriola", 14)).pack(pady=10)
    
    # ==================== АВТОРИЗАЦИЯ ====================
    def create_login_screen(self, frame):
        try:
            img = Image.open("Наш декор.png")
            img = img.resize((200, 100), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = Label(frame, image=logo_img)
            logo_label.image = logo_img
            logo_label.pack(pady=20)
        except:
            pass
        
        Label(frame, text="НАШ ДЕКОР", font=("Gabriola", 32, "bold"), fg="#2D6033").pack(pady=10)
        Label(frame, text="Авторизация", font=("Gabriola", 20)).pack(pady=5)
        
        form_frame = Frame(frame)
        form_frame.pack(pady=20)
        
        Label(form_frame, text="Логин:", font=("Gabriola", 16)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.login_entry = Entry(form_frame, width=25, font=("Gabriola", 14))
        self.login_entry.grid(row=0, column=1, padx=10, pady=10)
        
        Label(form_frame, text="Пароль:", font=("Gabriola", 16)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = Entry(form_frame, width=25, font=("Gabriola", 14), show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        btn_frame = Frame(frame)
        btn_frame.pack(pady=20)
        
        Button(btn_frame, text="Войти", command=self.check_credentials,
               font=("Gabriola", 14), bg="#2D6033", fg="white", padx=20).pack(side="left", padx=10)
        
        self.login_entry.bind("<Return>", lambda e: self.check_credentials())
        self.password_entry.bind("<Return>", lambda e: self.check_credentials())
    
    # ==================== ПАРТНЁР ====================
    def create_partner_dashboard(self, frame):
        top_frame = Frame(frame, bg="#2D6033")
        top_frame.pack(fill="x")
    
        Label(top_frame, text="НАШ ДЕКОР", font=("Gabriola", 18, "bold"), fg="white", bg="#2D6033").pack(side="left", padx=10)
    
    # Безопасное получение значений
        name = self.current_user_name if self.current_user_name else "Партнёр"
        rating = self.current_rating if self.current_rating else 0
        discount = rating * 2
    
        Label(top_frame, text="Личный кабинет Партнёра", font=("Gabriola", 14), fg="white", bg="#2D6033").pack(side="right", padx=20)
    
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    # Вкладка "Каталог"
        catalog_frame = Frame(notebook)
        notebook.add(catalog_frame, text="Каталог продукции")
        self._create_product_table(catalog_frame, "partner")
    
        btn_frame = Frame(catalog_frame)
        btn_frame.pack(pady=10)
        Button(btn_frame, text="Создать заявку", command=self.create_request_form,
            font=("Gabriola", 12), bg="#4CAF50", fg="white", padx=15).pack(side="left", padx=5)
        Button(btn_frame, text="Материалы", command=self.show_materials,
            font=("Gabriola", 12), bg="#9C27B0", fg="white", padx=15).pack(side="left", padx=5)
        Button(btn_frame, text="Расчёт материалов", command=self.calculate_materials_report,
            font=("Gabriola", 12), bg="#00BCD4", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Обновить", command=lambda: self.load_products("partner"),
            font=("Gabriola", 12), bg="#2196F3", fg="white", padx=15).pack(side="left", padx=5)
    
    # Вкладка "Мои заявки"
        requests_frame = Frame(notebook)
        notebook.add(requests_frame, text="Мои заявки")
        self._create_requests_table(requests_frame, "partner")
    
        exit_frame = Frame(frame)
        exit_frame.pack(fill="x", pady=5)
        Button(exit_frame, text="Выйти", command=self.logout,
            font=("Gabriola", 12), bg="#555555", fg="white", padx=15).pack(side="right", padx=20)
    
    # ==================== АДМИНИСТРАТОР ====================
    def create_admin_dashboard(self, frame):
        top_frame = Frame(frame, bg="#2D6033")
        top_frame.pack(fill="x")
        
        Label(top_frame, text="НАШ ДЕКОР", font=("Gabriola", 18, "bold"), fg="white", bg="#2D6033").pack(side="left", padx=10)
        Label(top_frame, text=f"Администратор: {self.current_user_name}", font=("Gabriola", 12), fg="white", bg="#2D6033").pack(side="left", padx=20)
        Label(top_frame, text="Панель управления", font=("Gabriola", 14), fg="white", bg="#2D6033").pack(side="right", padx=20)
        
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Продукция"
        products_frame = Frame(notebook)
        notebook.add(products_frame, text="Управление продукцией")
        self._create_product_table(products_frame, "admin")
        
        btn_frame = Frame(products_frame)
        btn_frame.pack(pady=10)
        Button(btn_frame, text="Добавить", command=self.add_product,
               font=("Gabriola", 12), bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Редактировать", command=self.edit_product,
               font=("Gabriola", 12), bg="#FF9800", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Удалить", command=self.delete_product,
               font=("Gabriola", 12), bg="#f44336", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Материалы", command=self.show_materials,
               font=("Gabriola", 12), bg="#9C27B0", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Расчёт материалов", command=self.calculate_materials_report,
               font=("Gabriola", 12), bg="#00BCD4", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Обновить", command=lambda: self.load_products("admin"),
               font=("Gabriola", 12), bg="#2196F3", fg="white", padx=10).pack(side="left", padx=3)
        
        # Вкладка "Заявки"
        requests_frame = Frame(notebook)
        notebook.add(requests_frame, text="Все заявки")
        self._create_requests_table(requests_frame, "admin")
        
        # Вкладка "Партнёры"
        partners_frame = Frame(notebook)
        notebook.add(partners_frame, text="Партнёры")
        self._create_partners_table(partners_frame, "admin")
        
        exit_frame = Frame(frame)
        exit_frame.pack(fill="x", pady=5)
        Button(exit_frame, text="Выйти", command=self.logout,
               font=("Gabriola", 12), bg="#555555", fg="white", padx=15).pack(side="right", padx=20)
    
    # ==================== МЕНЕДЖЕР ====================
    def create_manager_dashboard(self, frame):
        top_frame = Frame(frame, bg="#2D6033")
        top_frame.pack(fill="x")
        
        Label(top_frame, text="НАШ ДЕКОР", font=("Gabriola", 18, "bold"), fg="white", bg="#2D6033").pack(side="left", padx=10)
        Label(top_frame, text=f"Менеджер: {self.current_user_name}", font=("Gabriola", 12), fg="white", bg="#2D6033").pack(side="left", padx=20)
        Label(top_frame, text="Панель менеджера", font=("Gabriola", 14), fg="white", bg="#2D6033").pack(side="right", padx=20)
        
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Продукция"
        products_frame = Frame(notebook)
        notebook.add(products_frame, text="Управление продукцией")
        self._create_product_table(products_frame, "manager")
        
        btn_frame = Frame(products_frame)
        btn_frame.pack(pady=10)
        Button(btn_frame, text="Добавить", command=self.add_product,
               font=("Gabriola", 12), bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Редактировать", command=self.edit_product,
               font=("Gabriola", 12), bg="#FF9800", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Материалы", command=self.show_materials,
               font=("Gabriola", 12), bg="#9C27B0", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Расчёт материалов", command=self.calculate_materials_report,
               font=("Gabriola", 12), bg="#00BCD4", fg="white", padx=10).pack(side="left", padx=3)
        Button(btn_frame, text="Обновить", command=lambda: self.load_products("manager"),
               font=("Gabriola", 12), bg="#2196F3", fg="white", padx=10).pack(side="left", padx=3)
        
        # Вкладка "Заявки"
        requests_frame = Frame(notebook)
        notebook.add(requests_frame, text="Заявки партнёров")
        self._create_requests_table(requests_frame, "manager")
        
        # Вкладка "Партнёры"
        partners_frame = Frame(notebook)
        notebook.add(partners_frame, text="Партнёры")
        self._create_partners_table(partners_frame, "manager")
        
        exit_frame = Frame(frame)
        exit_frame.pack(fill="x", pady=5)
        Button(exit_frame, text="Выйти", command=self.logout,
               font=("Gabriola", 12), bg="#555555", fg="white", padx=15).pack(side="right", padx=20)
    
    # ==================== ТАБЛИЦА ПРОДУКЦИИ ====================
    def _create_product_table(self, frame, role):
        table_frame = Frame(frame)
        table_frame.pack(fill=BOTH, expand=True)
        
        columns = ("artikul", "product_name", "product_type", "roll_width", "cost", "prod_time", "workshop")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        tree.heading("artikul", text="Артикул")
        tree.heading("product_name", text="Наименование")
        tree.heading("product_type", text="Тип")
        tree.heading("roll_width", text="Ширина (м)")
        tree.heading("cost", text="Себестоимость (руб)")
        tree.heading("prod_time", text="Время изготовления (ч)")
        tree.heading("workshop", text="Цех")
        
        tree.column("artikul", width=100, anchor="center")
        tree.column("product_name", width=350)
        tree.column("product_type", width=130, anchor="center")
        tree.column("roll_width", width=80, anchor="center")
        tree.column("cost", width=120, anchor="center")
        tree.column("prod_time", width=100, anchor="center")
        tree.column("workshop", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.trees[role] = tree
        self.load_products(role)
    
    def load_products(self, role):
        
        if role == "partner" and self.current_user_id:
            self.update_current_rating()
        
        if role not in self.trees:
            return
        
        tree = self.trees[role]
        for row in tree.get_children():
            tree.delete(row)
        
        products = db_products.get_all_products()
        discount = 1 - (self.current_rating * 2 / 100) if self.current_rating and role == "partner" else 1
        
        for p in products:
            artikul, name, p_type, width, min_price, description, prod_time, workshop = p
            cost = db_products.calculate_product_cost(artikul)
            if role == "partner":
                cost = cost * discount
            tree.insert("", "end", values=(artikul, name, p_type, f"{width:.2f}", f"{cost:.2f}", prod_time or "-", workshop or "-"))
    
    # ==================== ТАБЛИЦА ЗАЯВОК ====================
    def _create_requests_table(self, frame, role):
        table_frame = Frame(frame)
        table_frame.pack(fill=BOTH, expand=True)
        
        if role == "partner":
            columns = ("id", "product", "quantity", "status", "date", "comment")
            headings = ("№", "Продукт", "Кол-во", "Статус", "Дата", "Комментарий")
        else:
            columns = ("id", "partner", "phone", "product", "quantity", "status", "date")
            headings = ("№", "Партнёр", "Телефон", "Продукт", "Кол-во", "Статус", "Дата")
        
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        widths = [50, 250, 80, 120, 100, 150] if role == "partner" else [50, 180, 120, 200, 80, 120, 150]
        for i, heading in enumerate(headings):
            tree.heading(columns[i], text=heading)
            tree.column(columns[i], width=widths[i])
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.requests_trees[role] = tree
        self.load_requests(role)
        
        btn_frame = Frame(frame)
        btn_frame.pack(pady=10)
        
        if role == "partner":
            Button(btn_frame, text="Обновить", command=lambda: self.load_requests("partner"),
                   font=("Gabriola", 11), bg="#2196F3", fg="white", padx=10).pack(side="left", padx=5)
        elif role == "manager":
            Button(btn_frame, text="Обновить", command=lambda: self.load_requests("manager"),
                   font=("Gabriola", 11), bg="#2196F3", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="В обработку", command=lambda: self.change_request_status("manager", "В обработке"),
                   font=("Gabriola", 11), bg="#FF9800", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Выполнено", command=lambda: self.change_request_status("manager", "Выполнено"),
                   font=("Gabriola", 11), bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Отменено", command=lambda: self.change_request_status("manager", "Отменено"),
                   font=("Gabriola", 11), bg="#f44336", fg="white", padx=10).pack(side="left", padx=5)
        elif role == "admin":
            Button(btn_frame, text="Обновить", command=lambda: self.load_requests("admin"),
                   font=("Gabriola", 11), bg="#2196F3", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="В обработку", command=lambda: self.change_request_status("admin", "В обработке"),
                   font=("Gabriola", 11), bg="#FF9800", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Выполнено", command=lambda: self.change_request_status("admin", "Выполнено"),
                   font=("Gabriola", 11), bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Отменено", command=lambda: self.change_request_status("admin", "Отменено"),
                   font=("Gabriola", 11), bg="#f44336", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Удалить", command=lambda: self.delete_request("admin"),
                   font=("Gabriola", 11), bg="#555555", fg="white", padx=10).pack(side="left", padx=5)
    
    def load_requests(self, role):
        if role not in self.requests_trees:
            return
        
        tree = self.requests_trees[role]
        for row in tree.get_children():
            tree.delete(row)
        
        if role == "partner":
            data = db_requests.get_requests_by_partner(self.current_user_id)
            for req in data:
                tree.insert("", "end", values=req)
        else:
            data = db_requests.get_all_requests()
            for req in data:
                tree.insert("", "end", values=req)
    
    def change_request_status(self, role, new_status):
        tree = self.requests_trees.get(role)
        if not tree:
            return
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку")
            return
        request_id = tree.item(selected[0])["values"][0]
        db_requests.update_request_status(request_id, new_status)
        self.load_requests(role)
        messagebox.showinfo("Успешно", f"Статус изменён на '{new_status}'")
    
    def delete_request(self, role):
        tree = self.requests_trees.get(role)
        if not tree:
            return
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку")
            return
        request_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Подтверждение", "Удалить заявку?"):
            db_requests.delete_request(request_id)
            self.load_requests(role)
            messagebox.showinfo("Успешно", "Заявка удалена")
    
    # ==================== ТАБЛИЦА ПАРТНЁРОВ ====================
    def _create_partners_table(self, frame, role):
        table_frame = Frame(frame)
        table_frame.pack(fill=BOTH, expand=True)
        
        columns = ("id", "name", "inn", "phone", "email", "rating", "date")
        headings = ("ID", "Компания", "ИНН", "Телефон", "Email", "Рейтинг", "Дата регистрации")
        
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        widths = [50, 200, 120, 120, 150, 80, 120]
        for i, heading in enumerate(headings):
            tree.heading(columns[i], text=heading)
            tree.column(columns[i], width=widths[i])
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.partners_trees[role] = tree
        self.load_partners()
        
        btn_frame = Frame(frame)
        btn_frame.pack(pady=10)
        
        if role == "manager":
            Button(btn_frame, text="Обновить", command=self.load_partners,
                   font=("Gabriola", 11), bg="#2196F3", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Добавить партнёра", command=self.add_partner_form,
                   font=("Gabriola", 11), bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Изменить рейтинг", command=self.change_rating_form,
                   font=("Gabriola", 11), bg="#FF9800", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="История рейтинга", command=self.show_rating_history,
                   font=("Gabriola", 11), bg="#9C27B0", fg="white", padx=10).pack(side="left", padx=5)
        elif role == "admin":
            Button(btn_frame, text="Обновить", command=self.load_partners,
                   font=("Gabriola", 11), bg="#2196F3", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Добавить партнёра", command=self.add_partner_form,
                   font=("Gabriola", 11), bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Изменить рейтинг", command=self.change_rating_form,
                   font=("Gabriola", 11), bg="#FF9800", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="История рейтинга", command=self.show_rating_history,
                   font=("Gabriola", 11), bg="#9C27B0", fg="white", padx=10).pack(side="left", padx=5)
            Button(btn_frame, text="Удалить партнёра", command=self.delete_partner_form,
                   font=("Gabriola", 11), bg="#f44336", fg="white", padx=10).pack(side="left", padx=5)
    
    def load_partners(self):
        if "manager" in self.partners_trees:
            tree = self.partners_trees["manager"]
            for row in tree.get_children():
                tree.delete(row)
            partners = database.get_all_partners()
            for p in partners:
                tree.insert("", "end", values=p)
        
        if "admin" in self.partners_trees:
            tree = self.partners_trees["admin"]
            for row in tree.get_children():
                tree.delete(row)
            partners = database.get_all_partners()
            for p in partners:
                tree.insert("", "end", values=p)
                
    def add_partner_form(self):
        window = Toplevel(self.root)
        window.title("Регистрация нового партнёра")
        window.geometry("1050x800")
        window.transient(self.root)
        window.grab_set()
        
        Label(window, text="Регистрация партнёра", font=("Gabriola", 16, "bold")).pack(pady=10)
        
        form_frame = Frame(window)
        form_frame.pack(pady=10, padx=20)
        
        labels = ["Название компании:", "Телефон:", "Логин:", "Пароль:", "ИНН:", "Email:", "Начальный рейтинг:"]
        entries = {}
        
        for i, label in enumerate(labels):
            Label(form_frame, text=label, font=("Gabriola", 12)).grid(row=i, column=0, padx=10, pady=8, sticky="e")
            entry = Entry(form_frame, width=25, font=("Gabriola", 12))
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[label] = entry
        
        entries["Начальный рейтинг:"].insert(0, "0")
        
        def save():
            try:
                name = entries["Название компании:"].get().strip()
                phone = entries["Телефон:"].get().strip()
                login = entries["Логин:"].get().strip()
                password = entries["Пароль:"].get().strip()
                inn = entries["ИНН:"].get().strip()
                email = entries["Email:"].get().strip()
                rating = float(entries["Начальный рейтинг:"].get().strip())
                
                if not all([name, login, password]):
                    messagebox.showerror("Ошибка", "Заполните название, логин и пароль")
                    return
                
                if database.add_partner(name, phone, login, password, inn, email, rating):
                    messagebox.showinfo("Успешно", "Партнёр добавлен")
                    window.destroy()
                    self.load_partners()
                else:
                    messagebox.showerror("Ошибка", "Логин уже существует")
            except ValueError:
                messagebox.showerror("Ошибка", "Рейтинг должен быть числом")
        
        Button(window, text="Сохранить", command=save,
               font=("Gabriola", 12), bg="#4CAF50", fg="white", padx=20).pack(pady=20)
    
    def change_rating_form(self):
        role = "manager" if self.current_role == "manager" else "admin"
        tree = self.partners_trees.get(role)
        if not tree:
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите партнёра")
            return
        
        partner_id = tree.item(selected[0])["values"][0]
        partner_name = tree.item(selected[0])["values"][1]
        current_rating = tree.item(selected[0])["values"][5]
        
        window = Toplevel(self.root)
        window.title("Изменение рейтинга")
        window.geometry("1000x550")
        window.transient(self.root)
        window.grab_set()
        
        Label(window, text=f"Партнёр: {partner_name}", font=("Gabriola", 14)).pack(pady=10)
        Label(window, text=f"Текущий рейтинг: {current_rating}", font=("Gabriola", 12)).pack()
        
        Label(window, text="Новый рейтинг (0-5):", font=("Gabriola", 12)).pack(pady=5)
        rating_entry = Entry(window, width=10, font=("Gabriola", 12))
        rating_entry.pack()
        
        Label(window, text="Причина изменения:", font=("Gabriola", 12)).pack(pady=5)
        reason_entry = Entry(window, width=40, font=("Gabriola", 12))
        reason_entry.pack()
        
        def save():
            try:
                new_rating = float(rating_entry.get())
                if new_rating < 0 or new_rating > 5:
                    messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 5")
                    return
                
                reason = reason_entry.get().strip()
                database.update_partner_rating(partner_id, new_rating, self.current_user_id, reason)
                messagebox.showinfo("Успешно", "Рейтинг изменён")
                window.destroy()
                self.load_partners()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")
        
        Button(window, text="Сохранить", command=save,
               font=("Gabriola", 12), bg="#4CAF50", fg="white", padx=20).pack(pady=20)
    
    def show_rating_history(self):
        role = "manager" if self.current_role == "manager" else "admin"
        tree = self.partners_trees.get(role)
        if not tree:
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите партнёра")
            return
        
        partner_id = tree.item(selected[0])["values"][0]
        partner_name = tree.item(selected[0])["values"][1]
        
        history = database.get_rating_history(partner_id)
        if not history:
            messagebox.showinfo("История", "История изменений рейтинга пуста")
            return
        
        window = Toplevel(self.root)
        window.title(f"История рейтинга: {partner_name}")
        window.geometry("1000x500")
        
        Label(window, text=f"История изменения рейтинга", font=("Gabriola", 14, "bold")).pack(pady=10)
        
        columns = ("old", "new", "who", "date", "reason")
        tree_hist = ttk.Treeview(window, columns=columns, show="headings", height=15)
        tree_hist.heading("old", text="Было")
        tree_hist.heading("new", text="Стало")
        tree_hist.heading("who", text="Кто изменил")
        tree_hist.heading("date", text="Дата")
        tree_hist.heading("reason", text="Причина")
        
        tree_hist.column("old", width=80, anchor="center")
        tree_hist.column("new", width=80, anchor="center")
        tree_hist.column("who", width=150)
        tree_hist.column("date", width=150)
        tree_hist.column("reason", width=200)
        
        for h in history:
            tree_hist.insert("", "end", values=h)
        
        tree_hist.pack(fill="both", expand=True, padx=10, pady=10)
        
        Button(window, text="Закрыть", command=window.destroy,
               font=("Gabriola", 11), bg="#2D6033", fg="white", padx=20).pack(pady=10)
    
    def delete_partner_form(self):
        tree = self.partners_trees.get("admin")
        if not tree:
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите партнёра")
            return
        
        partner_id = tree.item(selected[0])["values"][0]
        partner_name = tree.item(selected[0])["values"][1]
        
        if messagebox.askyesno("Подтверждение", f"Удалить партнёра '{partner_name}'?"):
            database.delete_partner(partner_id)
            self.load_partners()
            messagebox.showinfo("Успешно", "Партнёр удалён")
    
    # ==================== СОЗДАНИЕ ЗАЯВКИ ====================
    def create_request_form(self):
        tree = self.trees.get("partner")
        if not tree:
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите продукт в каталоге")
            return
        
        artikul = tree.item(selected[0])["values"][0]
        product_name = tree.item(selected[0])["values"][1]
        
        window = Toplevel(self.root)
        window.title("Оформление заявки")
        window.geometry("1000x550")
        window.transient(self.root)
        window.grab_set()
        
        Label(window, text="Оформление заявки", font=("Gabriola", 16, "bold")).pack(pady=10)
        Label(window, text=f"Продукт: {product_name}", font=("Gabriola", 12), fg="#2D6033").pack()
        
        form_frame = Frame(window)
        form_frame.pack(pady=20)
        
        Label(form_frame, text="Количество:", font=("Gabriola", 12)).grid(row=0, column=0, padx=10, pady=8)
        quantity_entry = Entry(form_frame, width=10, font=("Gabriola", 12))
        quantity_entry.grid(row=0, column=1, padx=10, pady=8)
        quantity_entry.insert(0, "1")
        
        Label(form_frame, text="Комментарий:", font=("Gabriola", 12)).grid(row=1, column=0, padx=10, pady=8)
        comment_text = Text(form_frame, width=30, height=5, font=("Gabriola", 11))
        comment_text.grid(row=1, column=1, padx=10, pady=8)
        
        def submit():
            try:
                quantity = int(quantity_entry.get())
                if quantity <= 0:
                    raise ValueError
                comment = comment_text.get("1.0", END).strip()
                db_requests.create_request(
                    self.current_user_id, self.current_user_name, "", 
                    artikul, product_name, quantity, comment
                )
                messagebox.showinfo("Успешно", "Заявка отправлена")
                window.destroy()
                self.load_requests("partner")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное количество")
        
        Button(window, text="Отправить", command=submit,
               font=("Gabriola", 12), bg="#4CAF50", fg="white", padx=20).pack(pady=20)
    
    # ==================== УПРАВЛЕНИЕ ПРОДУКТАМИ ====================
    def add_product(self):
        self.current_product_for_edit = None
        self._show_product_form()
    
    def edit_product(self):
        if self.current_active_tree == "admin":
            tree = self.trees.get("admin")
        elif self.current_active_tree == "manager":
            tree = self.trees.get("manager")
        else:
            return
        
        if not tree:
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите продукт")
            return
        
        self.current_product_for_edit = tree.item(selected[0])["values"][0]
        self._show_product_form()
    
    def delete_product(self):
        tree = self.trees.get("admin")
        if not tree:
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите продукт")
            return
        
        artikul = tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Подтверждение", f"Удалить продукт {artikul}?"):
            db_products.delete_product(artikul)
            for role in ["admin", "manager", "partner"]:
                if role in self.trees:
                    self.load_products(role)
            messagebox.showinfo("Успешно", "Продукт удалён")
    
    def _show_product_form(self):
        window = Toplevel(self.root)
        is_edit = self.current_product_for_edit is not None
        
        window.title("Редактирование продукции" if is_edit else "Добавление продукции")
        window.geometry("1000x850")
        
        Label(window, text="НАШ ДЕКОР", font=("Gabriola", 16, "bold"), fg="#2D6033").pack(pady=10)
        
        title = "Редактирование продукции" if is_edit else "Добавление продукции"
        Label(window, text=title, font=("Gabriola", 14)).pack()
        
        form_frame = Frame(window)
        form_frame.pack(pady=20, padx=20, fill=X)
        
        self.product_widgets = {}
        row = 0
        
        if not is_edit:
            Label(form_frame, text="Артикул:", font=("Gabriola", 12)).grid(row=row, column=0, padx=10, pady=8, sticky="e")
            self.product_widgets["artikul"] = Entry(form_frame, width=30, font=("Gabriola", 12))
            self.product_widgets["artikul"].grid(row=row, column=1, padx=10, pady=8)
            row += 1
        
        Label(form_frame, text="Тип продукции:", font=("Gabriola", 12)).grid(row=row, column=0, padx=10, pady=8, sticky="e")
        types = ["Декоративные обои", "Фотообои", "Обои под покраску", "Стеклообои"]
        self.product_widgets["product_type"] = ttk.Combobox(form_frame, values=types, state="readonly", width=27)
        self.product_widgets["product_type"].grid(row=row, column=1, padx=10, pady=8)
        row += 1
        
        Label(form_frame, text="Наименование:", font=("Gabriola", 12)).grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.product_widgets["product_name"] = Entry(form_frame, width=30, font=("Gabriola", 12))
        self.product_widgets["product_name"].grid(row=row, column=1, padx=10, pady=8)
        row += 1
        
        Label(form_frame, text="Мин. стоимость (руб):", font=("Gabriola", 12)).grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.product_widgets["min_price"] = Entry(form_frame, width=30, font=("Gabriola", 12))
        self.product_widgets["min_price"].grid(row=row, column=1, padx=10, pady=8)
        row += 1
        
        Label(form_frame, text="Ширина рулона (м):", font=("Gabriola", 12)).grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.product_widgets["roll_width"] = Entry(form_frame, width=30, font=("Gabriola", 12))
        self.product_widgets["roll_width"].grid(row=row, column=1, padx=10, pady=8)
        row += 1
        
        btn_frame = Frame(window)
        btn_frame.pack(pady=20)
        
        Button(btn_frame, text="Сохранить", command=self.save_product,
               font=("Gabriola", 12), bg="#4CAF50", fg="white", padx=20).pack(side="left", padx=10)
        Button(btn_frame, text="Отмена", command=window.destroy,
               font=("Gabriola", 12), bg="#f44336", fg="white", padx=20).pack(side="left", padx=10)
        
        if is_edit:
            product = db_products.get_product_by_artikul(self.current_product_for_edit)
            if product:
                self.product_widgets["product_type"].set(product[1])
                self.product_widgets["product_name"].insert(0, product[2])
                self.product_widgets["min_price"].insert(0, str(product[3]))
                self.product_widgets["roll_width"].insert(0, str(product[4]))
    
    def save_product(self):
        try:
            product_type = self.product_widgets["product_type"].get()
            product_name = self.product_widgets["product_name"].get()
            min_price = float(self.product_widgets["min_price"].get())
            roll_width = float(self.product_widgets["roll_width"].get())
            
            if not product_type or not product_name:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            if self.current_product_for_edit:
                db_products.update_product(self.current_product_for_edit, product_type, product_name, min_price, roll_width)
                messagebox.showinfo("Успешно", "Продукт обновлён")
            else:
                artikul = self.product_widgets["artikul"].get()
                if not artikul:
                    messagebox.showerror("Ошибка", "Введите артикул")
                    return
                if db_products.add_product(artikul, product_type, product_name, min_price, roll_width):
                    messagebox.showinfo("Успешно", "Продукт добавлен")
                else:
                    messagebox.showerror("Ошибка", "Артикул уже существует")
                    return
            
            for role in ["admin", "manager", "partner"]:
                if role in self.trees:
                    self.load_products(role)
            
            self.product_window.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числа")
    
    # ==================== МАТЕРИАЛЫ И РАСЧЁТ ====================
    def show_materials(self):
        if self.current_active_tree == "admin":
            tree = self.trees.get("admin")
        elif self.current_active_tree == "manager":
            tree = self.trees.get("manager")
        else:
            tree = self.trees.get("partner")
        
        if not tree:
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите продукт")
            return
        
        artikul = tree.item(selected[0])["values"][0]
        materials = db_products.get_product_materials(artikul)
        
        if not materials:
            messagebox.showinfo("Материалы", "Материалы не найдены")
            return
        
        window = Toplevel(self.root)
        window.title(f"Материалы для продукта {artikul}")
        window.geometry("600x400")
        
        Label(window, text=f"Состав продукции", font=("Gabriola", 16)).pack(pady=10)
        
        columns = ("name", "quantity", "unit", "price")
        tree_mat = ttk.Treeview(window, columns=columns, show="headings", height=15)
        tree_mat.heading("name", text="Материал")
        tree_mat.heading("quantity", text="Количество")
        tree_mat.heading("unit", text="Ед. изм.")
        tree_mat.heading("price", text="Цена за ед.")
        
        for m in materials:
            tree_mat.insert("", "end", values=(m[0], m[1], m[2], m[3]))
        
        tree_mat.pack(fill="both", expand=True, padx=10, pady=10)
        Button(window, text="Закрыть", command=window.destroy,
               font=("Gabriola", 11), bg="#2196F3", fg="white", padx=20).pack(pady=10)
    
    def calculate_materials_report(self):
        tree = self.trees.get(self.current_active_tree)
        if not tree or not tree.selection():
            messagebox.showwarning("Предупреждение", "Выберите продукт")
            return
    
        artikul = tree.item(tree.selection()[0])["values"][0]
        product_name = tree.item(tree.selection()[0])["values"][1]
    
        # Окно для ввода количества
        w = Toplevel(self.root)
        w.title("Расчёт материалов")
        w.geometry("400x200")
        w.transient(self.root)
        w.grab_set()
    
        Label(w, text=f"Продукт: {product_name}", font=("Gabriola", 14)).pack(pady=10)
        Label(w, text="Количество для производства:", font=("Gabriola", 12)).pack()
        q_entry = Entry(w, font=("Gabriola", 12))
        q_entry.pack(pady=5)
        q_entry.insert(0, "100")
    
        def calc():
            try:
                quantity = int(q_entry.get())
                if quantity <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Ошибка", "Введите корректное количество")
                return
        
            # Получаем расчёт
            materials = db_products.calculate_materials_for_production(artikul, quantity)
        
            if not materials:
                messagebox.showinfo("", "Материалы не найдены")
                w.destroy()
                return
        
        # НОВОЕ ОКНО С РЕЗУЛЬТАТАМИ
            result_window = Toplevel(self.root)
            result_window.title(f"Расчёт материалов для {product_name}")
            result_window.geometry("750x500")
            result_window.transient(self.root)
            
            Label(result_window, text=f"Расчёт для производства {quantity} ед. '{product_name}'", 
                font=("Gabriola", 14, "bold")).pack(pady=10)
        
        # Таблица результатов
            columns = ("material", "required", "purchase", "waste", "unit", "cost")
            tree_res = ttk.Treeview(result_window, columns=columns, show="headings", height=15)
            tree_res.heading("material", text="Материал")
            tree_res.heading("required", text="Требуется")
            tree_res.heading("purchase", text="К закупке")
            tree_res.heading("waste", text="Брак, %")
            tree_res.heading("unit", text="Ед.")
            tree_res.heading("cost", text="Стоимость, руб")
        
            tree_res.column("material", width=250)
            tree_res.column("required", width=90, anchor="center")
            tree_res.column("purchase", width=90, anchor="center")
            tree_res.column("waste", width=70, anchor="center")
            tree_res.column("unit", width=60, anchor="center")
            tree_res.column("cost", width=100, anchor="center")
        
            total_cost = 0
            for m in materials:
                tree_res.insert("", "end", values=(
                    m['material'], m['required'], m['purchase'], 
                    m['waste_percent'], m['unit'], m['cost']
                ))
                total_cost += m['cost']
        
            tree_res.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Итоговая строка
            Label(result_window, text=f"Общая стоимость материалов: {total_cost:,.2f} руб.", 
                font=("Gabriola", 12, "bold"), fg="#2D6033").pack(pady=5)
        
            Button(result_window, text="Закрыть", command=result_window.destroy,
                font=("Gabriola", 11), bg="#2D6033", fg="white", padx=20).pack(pady=10)
        
            w.destroy()
    
        Button(w, text="Рассчитать", command=calc,
            font=("Gabriola", 12), bg="#4CAF50", fg="white", padx=20).pack(pady=20)
    
    # ==================== ВЫХОД И АВТОРИЗАЦИЯ ====================
    def logout(self):
        self.current_user_id = None
        self.current_user_name = None
        self.current_role = None
        self.current_rating = None
        self.show_screen("main")
    
    def update_current_rating(self):
        """Обновляет рейтинг текущего пользователя из БД"""
        import sqlite3
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT rating FROM profiles WHERE id = ?", (self.current_user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            self.current_rating = result[0]
        return self.current_rating
    
    def check_credentials(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
    
        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return
    
        is_valid, role, user_id, user_name, rating = database.verify_user(login, password)
    
        if is_valid:
            self.current_user_id = user_id
            self.current_user_name = user_name
            self.current_role = role
            self.current_rating = rating if rating else 0
            self.update_current_rating()
        
            if role == "admin":
                self.show_screen("admin_dashboard")
            elif role == "manager":
                self.show_screen("manager_dashboard")
            elif role == "partner":
                # Принудительно обновляем рейтинг из БД (на всякий случай)
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                cursor.execute("SELECT rating FROM profiles WHERE id = ?", (user_id,))
                fresh_rating = cursor.fetchone()
                conn.close()
    
                if fresh_rating:
                    self.current_rating = fresh_rating[0]
                else:
                    self.current_rating = rating if rating else 0
    
                self.show_screen("partner_dashboard")
                self.root.after(50, lambda: self.load_products("partner"))
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")


def main():
    print("Инициализация баз данных...")
    database.init_db()
    db_products.init_db()
    db_requests.init_db()

    root = Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
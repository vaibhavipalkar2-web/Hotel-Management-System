import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import sqlite3
import os
import re
import json  # Added to read theme configuration
from datetime import datetime as dt

# --- Theme Configuration Loader ---
def load_theme():
    default_theme = {
        "login_bg": "#3c502c",
        "login_text": "#7f9382",
        "header_bg": "#442c50",
        "header_label_bg": "#482c50",
        "accent_color": "#50372c",
        "button_primary": "#349edb",
        "button_success": "#27ae60",
        "bg_light": "#f5f5f5",
        "bg_white": "white"
    }
    if os.path.exists("theme.json"):
        try:
            with open("theme.json", "r") as f:
                user_theme = json.load(f)
                # Ensure all required keys exist, fall back to default if missing
                for key in default_theme:
                    if key not in user_theme:
                        user_theme[key] = default_theme[key]
                return user_theme
        except Exception:
            return default_theme
    return default_theme

THEME = load_theme()

# --- Database Setup ---
def init_db():
    con = sqlite3.connect('hotel.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_number INTEGER PRIMARY KEY,
            beds INTEGER, ac VARCHAR(100), tv VARCHAR(150),
            internet VARCHAR(100), price INTEGER, status VARCHAR(200) DEFAULT 'Available'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(150), last_name VARCHAR(50), contact_number VARCHAR(15),
            email VARCHAR(100), address TEXT, room_number INTEGER,
            check_in_date DATE, check_out_date DATE, status VARCHAR(20),
            FOREIGN KEY (room_number) REFERENCES rooms(room_number)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, guest_id INTEGER,
            room_number INTEGER, amount INTEGER, payment_method VARCHAR(20),
            payment_date DATE, payment_time TIME, status VARCHAR(20),
            card_number VARCHAR(20), upi_id VARCHAR(50), mobile_number VARCHAR(15)
        )
    """)
    
    cur.execute("SELECT COUNT(*) FROM rooms")
    if cur.fetchone()[0] == 0:
        sample_rooms = [
            (101, 2, 'Yes', 'Yes', 'Yes', 2000, 'Available'),
            (102, 1, 'No', 'Yes', 'No', 1000, 'Available'),
            (103, 2, 'Yes', 'Yes', 'Yes', 2500, 'Available'),
            (104, 3, 'Yes', 'No', 'Yes', 3000, 'Available'),
            (105, 1, 'Yes', 'Yes', 'Yes', 1500, 'Available'),
            (106, 2, 'No', 'No', 'Yes', 1800, 'Available'),
            (107, 1, 'Yes', 'No', 'No', 1200, 'Available'),
            (108, 3, 'Yes', 'Yes', 'Yes', 3500, 'Available')
        ]
        cur.executemany("INSERT INTO rooms VALUES (?,?,?,?,?,?,?)", sample_rooms)
    
    con.commit()
    con.close()

class HotelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hotel Management System")
        self.geometry("1200x850") 
        self.resizable(True, True)
        
        self._frame = None
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        init_db()
        self.switch_frame(LoginFrame)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill="both", expand=True)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=THEME["login_bg"])
        login_container = tk.Frame(self, bg=THEME["bg_white"], padx=40, pady=40, bd=2, relief="groove")
        login_container.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(login_container, text="HOTEL LOGIN", font=("Arial", 24, "bold"), bg=THEME["bg_white"], fg=THEME["login_text"]).pack(pady=(0, 20))
        tk.Label(login_container, text="Username", font=("Arial", 12), bg=THEME["bg_white"]).pack(anchor="w")
        self.username_entry = tk.Entry(login_container, font=("Arial", 12), width=30, bd=2)
        self.username_entry.pack(pady=(5, 15))
        tk.Label(login_container, text="Password", font=("Arial", 12), bg=THEME["bg_white"]).pack(anchor="w")
        self.password_entry = tk.Entry(login_container, font=("Arial", 12), width=30, bd=2, show="*")
        self.password_entry.pack(pady=(5, 20))
        
        login_btn = tk.Button(login_container, text="Login", font=("Arial", 12, "bold"), 
                              bg=THEME["button_primary"], fg="white", width=25, command=self.check_login)
        login_btn.pack()

    def check_login(self):
        u = self.username_entry.get()
        p = self.password_entry.get()
        if u == "admin" and p == "admin":
            self.master.switch_frame(DashboardFrame)
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

class DashboardFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=THEME["bg_light"])

        header = tk.Frame(self, bg=THEME["header_bg"], height=92)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="KINGS BHAVAN",
            font=("Arial", 26, "bold"),
            bg=THEME["header_bg"],
            fg="white"
        ).pack(pady=(18, 0))

        tk.Label(
            header,
            text="HOTEL MANAGEMENT SYSTEM",
            font=("Arial", 10, "bold"),
            bg=THEME["header_bg"],
            fg=THEME["accent_color"]
        ).pack(pady=(2, 0))

        self.toolbar = tk.Frame(self, bg=THEME["bg_white"], height=118, bd=0)
        self.toolbar.pack(fill="x")
        self.toolbar.pack_propagate(False)

        self.nav_images = []

        buttons_info = [
            ("images\\Hotelstatus.png", "Dashboard", self.show_status),
            ("images\\Rooms.png", "Rooms", self.show_rooms),
            ("images\\Bookroom.png", "Reserve", self.show_reserve),
            ("images\\Payments.png", "Checkout", self.show_payments),
            ("images\\PaymentHistory.png", "History", self.show_payment_history),
            ("images\\guests.png", "Customers", self.show_customers),
            ("images\\receptionnew.jpg", "Contact", self.show_contact),
            ("images\\logout.png", "Logout", lambda: self.master.switch_frame(LoginFrame))
        ]

        for path, label_text, cmd in buttons_info:
            btn_unit = tk.Frame(self.toolbar, bg=THEME["bg_white"])
            btn_unit.pack(side="left", padx=9, pady=12)

            try:
                img = ImageTk.PhotoImage(
                    Image.open(path).resize((42, 42), Image.Resampling.LANCZOS)
                )
                self.nav_images.append(img)

                btn = tk.Button(
                    btn_unit, image=img,
                    bg=THEME["bg_white"],
                    activebackground=THEME["header_bg"],
                    bd=0, cursor="hand2", command=cmd
                )
            except Exception:
                btn = tk.Button(
                    btn_unit, text=label_text,
                    bg=THEME["button_primary"], fg="white",
                    bd=0, width=12, height=2,
                    cursor="hand2", command=cmd
                )

            btn.pack()
            tk.Label(
                btn_unit, text=label_text,
                font=("Arial", 9, "bold"),
                bg=THEME["bg_white"],
                fg="white"
            ).pack(pady=(4, 0))

        self.content_area = tk.Frame(self, bg=THEME["bg_light"], bd=0)
        self.content_area.pack(fill="both", expand=True, padx=18, pady=18)

        self.show_status()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_status(self):
        self.clear_content()

        con = sqlite3.connect("hotel.db")
        cur = con.cursor()

        cur.execute("SELECT COUNT(*) FROM rooms")
        total_rooms = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM rooms WHERE status='Available'")
        available_rooms = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM rooms WHERE status IN ('Occupied', 'Booked')")
        booked_rooms = cur.fetchone()[0]

        staff_count = 12
        con.close()

        tk.Label(
            self.content_area,
            text="DASHBOARD OVERVIEW",
            font=("Arial", 22, "bold"),
            bg=THEME["bg_light"],
            fg="white"
        ).pack(anchor="w", padx=25, pady=(22, 3))

        tk.Label(
            self.content_area,
            text="Monitor rooms, reservations and hotel activity",
            font=("Arial", 11),
            bg=THEME["bg_light"],
            fg="#cbd5e1"
        ).pack(anchor="w", padx=25, pady=(0, 25))

        cards_frame = tk.Frame(self.content_area, bg=THEME["bg_light"])
        cards_frame.pack(pady=10)

        def create_card(parent, title, value, color, subtitle):
            card = tk.Frame(parent, bg=color, width=220, height=145)
            card.pack_propagate(False)
            card.pack(side="left", padx=12, pady=8)

            tk.Label(card, text=title, font=("Arial", 11, "bold"),
                     bg=color, fg="#e2e8f0").pack(anchor="w", padx=18, pady=(20, 4))

            tk.Label(card, text=str(value), font=("Arial", 30, "bold"),
                     bg=color, fg="white").pack(anchor="w", padx=18)

            tk.Label(card, text=subtitle, font=("Arial", 9),
                     bg=color, fg="#cbd5e1").pack(anchor="w", padx=18, pady=(4, 0))

        create_card(cards_frame, "TOTAL ROOMS", total_rooms, "#334155", "All hotel rooms")
        create_card(cards_frame, "AVAILABLE", available_rooms, "#166534", "Ready for booking")
        create_card(cards_frame, "OCCUPIED", booked_rooms, "#b91c1c", "Current reservations")
        create_card(cards_frame, "HOTEL STAFF", staff_count, "#075985", "Team members")

        info_box = tk.Frame(self.content_area, bg=THEME["bg_white"], bd=1, relief="solid")
        info_box.pack(fill="x", padx=38, pady=28)

        tk.Label(info_box, text="WELCOME TO KINGS BHAVAN",
                 font=("Arial", 14, "bold"),
                 bg=THEME["bg_white"],
                 fg=THEME["accent_color"]).pack(anchor="w", padx=22, pady=(16, 4))

        tk.Label(info_box,
                 text="Use the menu above to manage rooms, reservations, customers and payments.",
                 font=("Arial", 11),
                 bg=THEME["bg_white"],
                 fg="#cbd5e1").pack(anchor="w", padx=22, pady=(0, 16))

    def show_rooms(self):
        self.clear_content()
        tk.Label(self.content_area, text="Room Availability & Details", font=("Arial", 18, "bold"), bg=THEME["bg_white"]).pack(pady=10)
        filter_frame = tk.Frame(self.content_area, bg=THEME["bg_white"])
        filter_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(filter_frame, text="Filter by Status:", font=("Arial", 11), bg=THEME["bg_white"]).pack(side="left", padx=5)
        self.room_status_filter = ttk.Combobox(filter_frame, values=["All", "Available", "Occupied"], state="readonly", width=15)
        self.room_status_filter.set("All")
        self.room_status_filter.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Apply Filter", command=self.refresh_room_table, bg=THEME["button_primary"], fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        table_frame = tk.Frame(self.content_area, bg=THEME["bg_white"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("room_no", "beds", "ac", "tv", "internet", "price", "status")
        self.rooms_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns: self.rooms_tree.heading(col, text=col.replace("_", " ").title())
        self.rooms_tree.pack(fill="both", expand=True)
        self.refresh_room_table()

    def refresh_room_table(self):
        for item in self.rooms_tree.get_children(): self.rooms_tree.delete(item)
        status_val = self.room_status_filter.get()
        query = "SELECT * FROM rooms"
        params = ()
        if status_val != "All":
            query += " WHERE status=?"
            params = (status_val,)
        con = sqlite3.connect('hotel.db'); cur = con.cursor()
        cur.execute(query, params)
        for row in cur.fetchall(): self.rooms_tree.insert("", "end", values=row)
        con.close()

    def show_customers(self):
        self.clear_content()
        tk.Label(self.content_area, text="CUSTOMER RECORDS", font=("Arial", 20, "bold"), bg=THEME["bg_white"], fg="#2c3e50").pack(pady=20)
        search_frame = tk.Frame(self.content_area, bg=THEME["bg_white"])
        search_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(search_frame, text="Search Name/Contact:", font=("Arial", 11), bg=THEME["bg_white"]).pack(side="left", padx=5)
        self.cust_search_entry = tk.Entry(search_frame, font=("Arial", 11), width=30, bd=1, relief="solid")
        self.cust_search_entry.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.refresh_customer_table, bg=THEME["button_primary"], fg="white").pack(side="left", padx=5)
        table_frame = tk.Frame(self.content_area, bg=THEME["bg_white"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("id", "name", "contact", "email", "room", "check_in", "check_out", "status")
        self.cust_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        headings = ["ID", "Guest Name", "Contact", "Email", "Room", "Check-In", "Check-Out", "Status"]
        for col, head in zip(columns, headings):
            self.cust_tree.heading(col, text=head)
            self.cust_tree.column(col, width=100)
        self.cust_tree.pack(fill="both", expand=True)
        self.refresh_customer_table()

    def refresh_customer_table(self):
        for item in self.cust_tree.get_children(): self.cust_tree.delete(item)
        search_term = self.cust_search_entry.get().strip()
        con = sqlite3.connect('hotel.db'); cur = con.cursor()
        if search_term:
            cur.execute("""SELECT id, first_name || ' ' || last_name, contact_number, email, room_number, 
                           check_in_date, check_out_date, status FROM guests 
                           WHERE first_name LIKE ? OR last_name LIKE ? OR contact_number LIKE ?""", 
                        (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            cur.execute("""SELECT id, first_name || ' ' || last_name, contact_number, email, room_number, 
                           check_in_date, check_out_date, status FROM guests ORDER BY id DESC""")
        for row in cur.fetchall():
            display_row = list(row)
            if not display_row[6]: display_row[6] = "---"
            self.cust_tree.insert("", "end", values=display_row)
        con.close()

    def show_contact(self):
        self.clear_content()
        BG_COLOR = THEME["bg_white"]
        tk.Label(self.content_area, text="STAFF CONTACT DIRECTORY", font=("msserif", 24, "bold"), bg=BG_COLOR, fg="#2c3e50").pack(pady=(20, 5))
        tk.Frame(self.content_area, height=3, bg=THEME["button_primary"], width=400).pack(pady=(0, 20))

        contact_container = tk.Frame(self.content_area, bg=BG_COLOR)
        contact_container.pack(fill="both", expand=True, padx=50)

        staff_members = [
            {"role": "Manager", "name": "Ms. vaibhavi palkar", "ext": "025", "mail": "Manager@hotelname.com", "img": "images\\newman.jpg"},
            {"role": "Customer Executive", "name": "Ms. Siddhi", "ext": "032", "mail": "Costoexe@hotelname.com", "img": "images\\receptionnew.jpg"},
            {"role": "Restaurant", "name": "Mr. Kunal", "ext": "028", "mail": "Restaurant@hotelname.com", "img": "images\\fchefnew.jpg"},
            {"role": "Room Service", "name": "Ms. sandhya", "ext": "041", "mail": "Roomsserv@hotelname.com", "img": "images\\roomservicenew.jpg"}
        ]

        self.staff_photo_refs = []

        for i, staff in enumerate(staff_members):
            row, col = i // 2, i % 2
            card = tk.Frame(contact_container, bg=THEME["bg_white"], bd=1, relief="solid", padx=10, pady=10)
            card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            
            try:
                img_path = staff["img"]
                pil_img = Image.open(img_path).resize((100, 100), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                self.staff_photo_refs.append(tk_img)
                tk.Label(card, image=tk_img, bg=THEME["bg_white"]).pack(side="left", padx=10)
            except Exception:
                tk.Label(card, text="[No Img]", bg="#eee", width=10).pack(side="left", padx=10)

            info_frame = tk.Frame(card, bg=THEME["bg_white"])
            info_frame.pack(side="left", padx=10)
            
            tk.Label(info_frame, text=staff["role"], font=("Arial", 16, "bold"), bg=THEME["bg_white"], fg="black").pack(anchor="w")
            tk.Label(info_frame, text=staff["name"], font=("Arial", 11), bg=THEME["bg_white"], fg="#555").pack(anchor="w", pady=(5, 0))
            tk.Label(info_frame, text=f"Extension : {staff['ext']}", font=("Arial", 11), bg=THEME["bg_white"], fg="#555").pack(anchor="w")
            tk.Label(info_frame, text=f"Mail : {staff['mail']}", font=("Arial", 11), bg=THEME["bg_white"], fg=THEME["button_primary"]).pack(anchor="w")

        contact_container.grid_columnconfigure(0, weight=1)
        contact_container.grid_columnconfigure(1, weight=1)

    def show_reserve(self):
        self.clear_content()
        BG_COLOR, ACCENT_COLOR, BTN_COLOR = THEME["bg_white"], THEME["accent_color"], THEME["button_success"]
        main_container = tk.Frame(self.content_area, bg=BG_COLOR)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        form_frame = tk.Frame(main_container, bg=BG_COLOR)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        tk.Label(form_frame, text="RESERVE ROOM", font=("msserif", 20, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w")
        tk.Frame(form_frame, height=2, bg=ACCENT_COLOR, width=300).pack(anchor="w", pady=(0, 20))
        
        self.inputs = {}
        def add_field(parent, label, key, row, col, width=25):
            f = tk.Frame(parent, bg=BG_COLOR)
            f.grid(row=row, column=col, padx=10, pady=10, sticky="w")
            tk.Label(f, text=label, font=("msserif", 12), bg=BG_COLOR, fg="#555").pack(anchor="w")
            e = tk.Entry(f, font=("Arial", 11), width=width, bd=1, relief="solid")
            e.pack(pady=2, ipady=3)
            self.inputs[key] = e

        fields_container = tk.Frame(form_frame, bg=BG_COLOR)
        fields_container.pack(fill="x", anchor="n")
        
        add_field(fields_container, "First Name*", "fname", 0, 0)
        add_field(fields_container, "Last Name*", "lname", 0, 1)
        add_field(fields_container, "Contact No.* (10 digits)", "contact", 1, 0)
        add_field(fields_container, "Email*", "email", 1, 1)
        add_field(fields_container, "Address", "address", 2, 0)
        add_field(fields_container, "Room No.*", "room_no", 2, 1)
        add_field(fields_container, "No. of Days*", "days", 3, 0)
        
        guest_count_frame = tk.Frame(fields_container, bg=BG_COLOR)
        guest_count_frame.grid(row=3, column=1, sticky="w", padx=10)
        tk.Label(guest_count_frame, text="Adults*", font=("msserif", 12), bg=BG_COLOR, fg="#555").grid(row=0, column=0, sticky="w")
        self.inputs['adults'] = tk.Entry(guest_count_frame, font=("Arial", 11), width=10, bd=1, relief="solid")
        self.inputs['adults'].grid(row=1, column=0, pady=2, ipady=3, padx=(0, 10))
        tk.Label(guest_count_frame, text="Children", font=("msserif", 12), bg=BG_COLOR, fg="#555").grid(row=0, column=1, sticky="w")
        self.inputs['children'] = tk.Entry(guest_count_frame, font=("Arial", 11), width=10, bd=1, relief="solid")
        self.inputs['children'].grid(row=1, column=1, pady=2, ipady=3)

        btn_frame = tk.Frame(form_frame, bg=BG_COLOR)
        btn_frame.pack(pady=30, anchor="w", padx=10)
        tk.Button(btn_frame, text="CONFIRM BOOKING", font=("Arial", 11, "bold"), bg=BTN_COLOR, fg="white", width=20, height=2, bd=0, command=self.process_reservation).pack(side="left", padx=(0, 10))
        tk.Button(btn_frame, text="RESET", font=("Arial", 11, "bold"), bg="#95a5a6", fg="white", width=15, height=2, bd=0, command=self.show_reserve).pack(side="left")

        filter_frame = tk.LabelFrame(main_container, text=" FILTER ROOMS ", font=("msserif", 15, "bold"), bg="white", fg=ACCENT_COLOR, bd=2, relief="groove")
        filter_frame.pack(side="right", fill="y", padx=10, ipadx=10, ipady=10)
        self.var_beds, self.var_ac, self.var_tv, self.var_internet = [tk.StringVar(value="All") for _ in range(4)]
        def add_filter_option(label, var, values):
            container = tk.Frame(filter_frame, bg="white")
            container.pack(fill="x", padx=15, pady=5)
            tk.Label(container, text=label, font=("Arial", 10, "bold"), bg="white", fg="#555").pack(anchor="w")
            ttk.Combobox(container, textvariable=var, values=values, state="readonly", width=22).pack(pady=2)
        add_filter_option("No. of Beds", self.var_beds, ["All", "1", "2", "3"]); add_filter_option("AC Available", self.var_ac, ["All", "Yes", "No"])
        add_filter_option("TV Available", self.var_tv, ["All", "Yes", "No"]); add_filter_option("Internet", self.var_internet, ["All", "Yes", "No"])
        tk.Button(filter_frame, text="Search Rooms", bg=THEME["button_primary"], fg="white", font=("Arial", 10, "bold"), command=self.search_rooms).pack(fill="x", padx=15, pady=15)
        self.room_listbox = tk.Listbox(filter_frame, font=("Arial", 11), height=10); self.room_listbox.pack(fill="both", expand=True, padx=15, pady=10)
        self.room_listbox.bind('<<ListboxSelect>>', self.on_room_select); self.search_rooms()

    def search_rooms(self):
        query = "SELECT room_number, price FROM rooms WHERE status='Available'"
        params = []
        if self.var_beds.get() != "All": query += " AND beds=?"; params.append(self.var_beds.get())
        if self.var_ac.get() != "All": query += " AND ac=?"; params.append(self.var_ac.get())
        if self.var_tv.get() != "All": query += " AND tv=?"; params.append(self.var_tv.get())
        if self.var_internet.get() != "All": query += " AND internet=?"; params.append(self.var_internet.get())
        self.room_listbox.delete(0, tk.END)
        con = sqlite3.connect('hotel.db'); cur = con.cursor()
        cur.execute(query, tuple(params)); rows = cur.fetchall(); con.close()
        for r in rows: self.room_listbox.insert(tk.END, f"Room {r[0]} - ₹{r[1]}")

    def on_room_select(self, event):
        selection = self.room_listbox.curselection()
        if selection:
            text = self.room_listbox.get(selection[0])
            self.inputs['room_no'].delete(0, tk.END); self.inputs['room_no'].insert(0, text.split()[1])

    def process_reservation(self):
        data = {k: v.get().strip() for k, v in self.inputs.items()}
        errors = []
        
        if not data['fname'] or not data['fname'].isalpha(): errors.append("Valid First Name is required.")
        if not data['lname'] or not data['lname'].isalpha(): errors.append("Valid Last Name is required.")
        if not (data['contact'].isdigit() and len(data['contact']) == 10): errors.append("Contact must be 10 digits.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']): errors.append("Valid email is required.")
        if not data['room_no']: errors.append("Room No. is required.")
        
        try:
            if int(data['days']) <= 0: errors.append("Days must be positive.")
            if int(data['adults']) <= 0: errors.append("At least 1 adult is required.")
            if data['children'] and int(data['children']) < 0: errors.append("Children count invalid.")
        except ValueError:
            errors.append("Numeric fields must be digits.")

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        try:
            con = sqlite3.connect('hotel.db'); cur = con.cursor()
            cur.execute("SELECT status FROM rooms WHERE room_number=?", (data['room_no'],))
            res = cur.fetchone()
            if not res or res[0] != 'Available': messagebox.showerror("Error", "Room not available."); return
            
            cur.execute("""INSERT INTO guests (first_name, last_name, contact_number, email, address, room_number, status, check_in_date)
                           VALUES (?, ?, ?, ?, ?, ?, 'Checked In', ?)""", 
                           (data['fname'], data['lname'], data['contact'], data['email'], data['address'], data['room_no'], dt.now().strftime('%Y-%m-%d')))
            cur.execute("UPDATE rooms SET status='Occupied' WHERE room_number=?", (data['room_no'],))
            con.commit(); con.close()
            messagebox.showinfo("Success", "Booking confirmed!"); self.show_status()
        except Exception as e: messagebox.showerror("Error", str(e))

    def show_payments(self):
        self.clear_content()
        BG_COLOR, ACCENT_COLOR = THEME["bg_white"], THEME["accent_color"]
        main_container = tk.Frame(self.content_area, bg=BG_COLOR)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        filter_frame = tk.LabelFrame(main_container, text=" SELECT OCCUPIED ROOM ", font=("msserif", 15, "bold"), bg="white", fg=ACCENT_COLOR, bd=2, relief="groove")
        filter_frame.pack(side="left", fill="y", padx=(0, 20), ipadx=10, ipady=10)
        self.pay_room_listbox = tk.Listbox(filter_frame, font=("Arial", 11), width=30, bd=1, relief="solid")
        self.pay_room_listbox.pack(fill="both", expand=True, padx=15, pady=10)
        self.pay_room_listbox.bind('<<ListboxSelect>>', self.on_payment_room_select)
        tk.Button(filter_frame, text="Refresh List", bg=THEME["button_primary"], fg="white", font=("Arial", 10, "bold"), command=self.refresh_occupied_rooms).pack(fill="x", padx=15, pady=5)

        details_frame = tk.Frame(main_container, bg=BG_COLOR)
        details_frame.pack(side="right", fill="both", expand=True)
        tk.Label(details_frame, text="PAYMENT & CHECKOUT", font=("msserif", 20, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w")
        tk.Frame(details_frame, height=2, bg=ACCENT_COLOR, width=350).pack(anchor="w", pady=(0, 20))

        lookup_bar = tk.Frame(details_frame, bg=BG_COLOR)
        lookup_bar.pack(fill="x", pady=10)
        tk.Label(lookup_bar, text="Room No:", font=("Arial", 12, "bold"), bg=BG_COLOR).pack(side="left")
        self.pay_room_no_entry = tk.Entry(lookup_bar, font=("Arial", 12), width=10, bd=1, relief="solid")
        self.pay_room_no_entry.pack(side="left", padx=10)
        tk.Button(lookup_bar, text="SEARCH GUEST", bg=THEME["button_primary"], fg="white", font=("Arial", 10, "bold"), command=self.lookup_guest_for_payment).pack(side="left")

        self.pay_info_container = tk.LabelFrame(details_frame, text=" Guest Information ", bg="white", font=("Arial", 12, "bold"), padx=30, pady=20, bd=2, relief="groove")
        self.pay_info_container.pack(fill="x", pady=10)
        self.pay_labels = {}
        info_fields = [("Guest Name", "name"), ("Contact No", "contact"), ("Check-in Date", "date"), ("Total Amount", "amount")]
        for i, (l, k) in enumerate(info_fields):
            tk.Label(self.pay_info_container, text=f"{l}:", bg="white", font=("Arial", 11, "bold"), fg="#2c3e50").grid(row=i, column=0, sticky="w", pady=5)
            self.pay_labels[k] = tk.Label(self.pay_info_container, text="---", bg="white", font=("Arial", 11), fg="#555")
            self.pay_labels[k].grid(row=i, column=1, sticky="w", padx=30, pady=5)

        pay_method_frame = tk.Frame(details_frame, bg=BG_COLOR)
        pay_method_frame.pack(fill="x", pady=10)
        tk.Label(pay_method_frame, text="Select Payment Method:", font=("Arial", 12, "bold"), bg=BG_COLOR).pack(side="left")
        self.pay_method_combo = ttk.Combobox(pay_method_frame, values=["Cash", "Credit Card", "Debit Card", "UPI / Online"], state="readonly", font=("Arial", 11), width=20)
        self.pay_method_combo.set("Cash")
        self.pay_method_combo.pack(side="left", padx=10)

        actions_frame = tk.Frame(details_frame, bg=BG_COLOR)
        actions_frame.pack(pady=20, anchor="w")
        tk.Button(actions_frame, text="COMPLETE CHECKOUT", bg=THEME["button_success"], fg="white", font=("Arial", 12, "bold"), width=25, height=2, bd=0, command=self.finalize_payment).pack(side="left", padx=(0, 10))

        self.refresh_occupied_rooms()

    def refresh_occupied_rooms(self):
        self.pay_room_listbox.delete(0, tk.END)
        con = sqlite3.connect('hotel.db'); cur = con.cursor()
        cur.execute("SELECT room_number, status FROM rooms WHERE status='Occupied' ORDER BY room_number")
        rows = cur.fetchall(); con.close()
        for r in rows:
            self.pay_room_listbox.insert(tk.END, f"Room {r[0]} - [ {r[1]} ]")

    def on_payment_room_select(self, event):
        selection = self.pay_room_listbox.curselection()
        if selection:
            text = self.pay_room_listbox.get(selection[0])
            room_no = text.split()[1]
            self.pay_room_no_entry.delete(0, tk.END)
            self.pay_room_no_entry.insert(0, room_no)
            self.lookup_guest_for_payment()

    def lookup_guest_for_payment(self):
        r_no = self.pay_room_no_entry.get().strip()
        if not r_no: return
        con = sqlite3.connect('hotel.db'); cur = con.cursor()
        cur.execute("""SELECT first_name, last_name, contact_number, check_in_date, rooms.price 
                       FROM guests JOIN rooms ON guests.room_number = rooms.room_number 
                       WHERE guests.room_number=? AND guests.status='Checked In'""", (r_no,))
        row = cur.fetchone(); con.close()
        if row:
            self.pay_labels['name'].config(text=f"{row[0]} {row[1]}")
            self.pay_labels['contact'].config(text=row[2])
            self.pay_labels['date'].config(text=row[3])
            self.pay_labels['amount'].config(text=f"${row[4]}")
            self.current_guest_room = r_no
        else:
            for k in self.pay_labels: self.pay_labels[k].config(text="---")

    def finalize_payment(self):
        if not hasattr(self, 'current_guest_room') or not self.current_guest_room:
            messagebox.showwarning("Selection Required", "Please select a room to checkout.")
            return
        method = self.pay_method_combo.get()
        confirm = messagebox.askyesno("Confirm", f"Process {method} payment and checkout for Room {self.current_guest_room}?")
        if not confirm: return

        con = sqlite3.connect('hotel.db'); cur = con.cursor()
        cur.execute("""SELECT id, rooms.price FROM guests JOIN rooms ON guests.room_number = rooms.room_number 
                       WHERE guests.room_number=? AND guests.status='Checked In'""", (self.current_guest_room,))
        res = cur.fetchone()
        if res:
            g_id, price = res
            cur.execute("""INSERT INTO payments (guest_id, room_number, amount, payment_method, payment_date, payment_time, status) 
                           VALUES (?, ?, ?, ?, ?, ?, 'Completed')""", 
                        (g_id, self.current_guest_room, price, method, dt.now().strftime('%Y-%m-%d'), dt.now().strftime('%H:%M:%S')))
        
        cur.execute("UPDATE guests SET status='Checked Out', check_out_date=? WHERE room_number=? AND status='Checked In'", 
                    (dt.now().strftime('%Y-%m-%d'), self.current_guest_room))
        cur.execute("UPDATE rooms SET status='Available' WHERE room_number=?", (self.current_guest_room,))
        con.commit(); con.close()
        
        messagebox.showinfo("Success", f"Payment successful. Room {self.current_guest_room} is now available.")
        self.current_guest_room = None
        self.show_status()

    def show_payment_history(self):
        self.clear_content()
        tk.Label(self.content_area, text="PAYMENT TRANSACTION HISTORY", font=("Arial", 20, "bold"), bg=THEME["bg_white"], fg="#2c3e50").pack(pady=20)
        table_frame = tk.Frame(self.content_area, bg=THEME["bg_white"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("id", "guest", "room", "amount", "method", "date", "time")
        self.pay_history_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        headings = ["TXN ID", "Guest Name", "Room", "Amount", "Method", "Date", "Time"]
        for col, head in zip(columns, headings):
            self.pay_history_tree.heading(col, text=head)
            self.pay_history_tree.column(col, width=120, anchor="center")
        
        self.pay_history_tree.pack(fill="both", expand=True)
        self.refresh_payment_history()

    def refresh_payment_history(self):
        for item in self.pay_history_tree.get_children(): self.pay_history_tree.delete(item)
        con = sqlite3.connect('hotel.db'); cur = con.cursor()
        cur.execute("""SELECT payments.id, guests.first_name || ' ' || guests.last_name, 
                       payments.room_number, payments.amount, payments.payment_method, 
                       payments.payment_date, payments.payment_time 
                       FROM payments 
                       JOIN guests ON payments.guest_id = guests.id 
                       ORDER BY payments.id DESC""")
        for row in cur.fetchall():
            display_row = list(row)
            display_row[3] = f"${display_row[3]}"
            self.pay_history_tree.insert("", "end", values=display_row)
        con.close()

if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()
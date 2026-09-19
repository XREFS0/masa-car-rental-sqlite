"""
Developed by MASA
All Rights Reserved.
"""

import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta


def init_db():
    conn = sqlite3.connect("car_rental.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS cars (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        model TEXT, brand TEXT, 
                        price_per_day REAL, 
                        status TEXT DEFAULT "Available")""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        customer_name TEXT, car_model TEXT, car_id INTEGER,
                        date_rented TEXT, due_date TEXT, total_price REAL,
                        status TEXT DEFAULT "Active")""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        username TEXT UNIQUE, password TEXT, role TEXT,
                        full_name TEXT, phone TEXT, address TEXT)""")

    cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    conn.commit()
    conn.close()


class EditCarWindow(ctk.CTkToplevel):
    def __init__(self, master, car_id, current_data, callback):
        super().__init__(master)
        self.title("MASA - Edit Vehicle")
        self.geometry("350x400")
        self.callback = callback
        self.car_id = car_id
        self.attributes("-topmost", True)
        ctk.CTkLabel(self, text="Update Car Details", font=("Arial", 18, "bold")).pack(pady=20)
        self.br_e = ctk.CTkEntry(self, width=250)
        self.br_e.insert(0, current_data[1])
        self.br_e.pack(pady=10)
        self.mo_e = ctk.CTkEntry(self, width=250)
        self.mo_e.insert(0, current_data[0])
        self.mo_e.pack(pady=10)
        self.pr_e = ctk.CTkEntry(self, width=250)
        self.pr_e.insert(0, str(current_data[2]))
        self.pr_e.pack(pady=10)
        ctk.CTkButton(self, text="Save Changes", command=self.save, fg_color="#2E86C1").pack(pady=20)

    def save(self):
        try:
            conn = sqlite3.connect("car_rental.db")
            conn.execute(
                "UPDATE cars SET brand=?, model=?, price_per_day=? WHERE id=?",
                (self.br_e.get(), self.mo_e.get(), float(self.pr_e.get()), self.car_id),
            )
            conn.commit()
            conn.close()
            self.callback()
            self.destroy()
        except:
            messagebox.showerror("Error", "Invalid Data")


class EditUserWindow(ctk.CTkToplevel):
    def __init__(self, master, user_id, current_data, callback):
        super().__init__(master)
        self.title("MASA - Edit Customer Profile")
        self.geometry("400x550")
        self.callback = callback
        self.user_id = user_id
        self.attributes("-topmost", True)

        ctk.CTkLabel(self, text="Update Customer Profile", font=("Arial", 20, "bold")).pack(pady=20)

        def safe_add(label, val):
            ctk.CTkLabel(self, text=label).pack(anchor="w", padx=50)
            e = ctk.CTkEntry(self, width=300)
            if val:
                e.insert(0, str(val))
            e.pack(pady=(0, 10))
            return e

        self.n_e = safe_add("Full Name", current_data[1])
        self.ph_e = safe_add("Phone Number", current_data[2])
        self.ad_e = safe_add("Home Address", current_data[3])
        self.ps_e = safe_add("Reset Password", current_data[4])

        ctk.CTkButton(
            self, text="UPDATE ACCOUNT", fg_color="#2E86C1", height=45, width=200, command=self.save
        ).pack(pady=25)

    def save(self):
        conn = sqlite3.connect("car_rental.db")
        conn.execute(
            "UPDATE users SET full_name=?, phone=?, address=?, password=? WHERE id=?",
            (self.n_e.get(), self.ph_e.get(), self.ad_e.get(), self.ps_e.get(), self.user_id),
        )
        conn.commit()
        conn.close()
        self.callback()
        self.destroy()
        messagebox.showinfo("Success", "Profile Updated Successfully")


class CarRentalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MASA - Car Rental System")
        self.geometry("1200x850")
        ctk.set_appearance_mode("dark")
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        self.show_login()

    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def check_overdue(self, due_date_str):
        try:
            return datetime.now() > datetime.strptime(due_date_str, "%Y-%m-%d")
        except:
            return False

    def show_login(self):
        self.clear_screen()
        f = ctk.CTkFrame(self.main_container, width=350, height=450)
        f.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(f, text="CAR RENTAL", font=("Impact", 45)).pack(pady=30)
        u_e = ctk.CTkEntry(f, placeholder_text="Username", width=250)
        u_e.pack(pady=10)
        p_e = ctk.CTkEntry(f, placeholder_text="Password", show="*", width=250)
        p_e.pack(pady=10)
        rv = ctk.StringVar(value="customer")
        ctk.CTkSegmentedButton(f, values=["customer", "admin"], variable=rv).pack(pady=15)

        def login():
            conn = sqlite3.connect("car_rental.db")
            res = conn.execute(
                "SELECT role FROM users WHERE username=? AND password=? AND role=?",
                (u_e.get(), p_e.get(), rv.get()),
            ).fetchone()
            conn.close()
            if res:
                self.current_user = u_e.get()
                self.setup_layout(res[0])
            else:
                messagebox.showerror("Error", "Access Denied")

        ctk.CTkButton(f, text="Sign In", command=login, width=250, height=40).pack(pady=20)

    def setup_layout(self, role):
        self.clear_screen()
        self.sidebar = ctk.CTkFrame(self.main_container, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(self.sidebar, text="DASHBOARD", font=("Arial", 14, "bold")).pack(pady=25)
        if role == "admin":
            ctk.CTkButton(self.sidebar, text="Fleet Control", command=self.admin_fleet_view).pack(
                pady=5, padx=20, fill="x"
            )
            ctk.CTkButton(self.sidebar, text="Manage Customers", command=self.admin_user_crud_view).pack(
                pady=5, padx=20, fill="x"
            )
            ctk.CTkButton(self.sidebar, text="Rental Monitor", command=self.admin_monitor_view).pack(
                pady=5, padx=20, fill="x"
            )
        else:
            ctk.CTkButton(self.sidebar, text="Available Cars", command=self.user_rent_view).pack(
                pady=5, padx=20, fill="x"
            )
            ctk.CTkButton(self.sidebar, text="My Rentals", command=self.user_my_rentals_view).pack(
                pady=5, padx=20, fill="x"
            )
        ctk.CTkButton(self.sidebar, text="Log Out", fg_color="#C0392B", command=self.show_login).pack(
            side="bottom", pady=25, padx=20, fill="x"
        )
        self.content = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content.pack(side="right", fill="both", expand=True, padx=25, pady=20)
        self.admin_fleet_view() if role == "admin" else self.user_rent_view()

    def admin_monitor_view(self):
        for w in self.content.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.content, text="System Monitor", font=("Arial", 24, "bold")).pack(anchor="w")
        scroll = ctk.CTkScrollableFrame(self.content)
        scroll.pack(fill="both", expand=True, pady=10)
        h = ctk.CTkFrame(scroll, fg_color="#333")
        h.pack(fill="x", pady=2)
        ctk.CTkLabel(h, text="Customer", width=150).pack(side="left", padx=5)
        ctk.CTkLabel(h, text="Car", width=150).pack(side="left", padx=5)
        ctk.CTkLabel(h, text="Due Date", width=120).pack(side="left", padx=5)
        ctk.CTkLabel(h, text="Alerts", width=120).pack(side="left", padx=5)

        conn = sqlite3.connect("car_rental.db")
        for b in conn.execute("SELECT * FROM bookings WHERE status='Active'").fetchall():
            over = self.check_overdue(b[5])
            r = ctk.CTkFrame(scroll, border_width=1 if over else 0, border_color="red")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=b[1], width=150).pack(side="left", padx=5)
            ctk.CTkLabel(r, text=b[2], width=150).pack(side="left", padx=5)
            ctk.CTkLabel(r, text=b[5], width=120).pack(side="left", padx=5)
            ctk.CTkLabel(
                r, text="⚠️ OVERDUE" if over else "Active", text_color="red" if over else "green", width=120
            ).pack(side="left", padx=5)
            ctk.CTkButton(
                r,
                text="Return",
                width=80,
                fg_color="#E67E22",
                command=lambda bid=b[0], cid=b[3]: self.process_return(bid, cid, self.admin_monitor_view),
            ).pack(side="right", padx=10)
        conn.close()

    def admin_user_crud_view(self):
        for w in self.content.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.content, text="Manage Customer Accounts", font=("Arial", 24, "bold")).pack(
            anchor="w"
        )
        f = ctk.CTkFrame(self.content)
        f.pack(fill="x", pady=10)
        u_e = ctk.CTkEntry(f, placeholder_text="Username")
        u_e.grid(row=0, column=0, padx=5, pady=5)
        p_e = ctk.CTkEntry(f, placeholder_text="Password")
        p_e.grid(row=0, column=1, padx=5, pady=5)
        n_e = ctk.CTkEntry(f, placeholder_text="Full Name")
        n_e.grid(row=1, column=0, padx=5, pady=5)
        ph_e = ctk.CTkEntry(f, placeholder_text="Phone")
        ph_e.grid(row=1, column=1, padx=5, pady=5)

        def create():
            try:
                conn = sqlite3.connect("car_rental.db")
                conn.execute(
                    "INSERT INTO users (username, password, role, full_name, phone) VALUES (?, ?, 'customer', ?, ?)",
                    (u_e.get(), p_e.get(), n_e.get(), ph_e.get()),
                )
                conn.commit()
                conn.close()
                self.admin_user_crud_view()
            except:
                messagebox.showerror("Error", "Username Taken")

        ctk.CTkButton(f, text="Register", command=create, fg_color="#1E8449").grid(
            row=0, column=2, rowspan=2, padx=10
        )

        scroll = ctk.CTkScrollableFrame(self.content, label_text="Database")
        scroll.pack(fill="both", expand=True)
        conn = sqlite3.connect("car_rental.db")
        for u in conn.execute(
            "SELECT id, username, full_name, phone, address, password FROM users WHERE role='customer'"
        ).fetchall():
            r = ctk.CTkFrame(scroll)
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=f"{u[1]} | {u[2]}", width=300, anchor="w").pack(side="left", padx=10)
            ctk.CTkButton(
                r,
                text="Delete",
                fg_color="#7B241C",
                width=60,
                command=lambda uid=u[0]: [
                    sqlite3.connect("car_rental.db")
                    .execute("DELETE FROM users WHERE id=?", (uid,))
                    .connection.commit(),
                    self.admin_user_crud_view(),
                ],
            ).pack(side="right", padx=5)
            ctk.CTkButton(
                r,
                text="Edit",
                fg_color="#2E86C1",
                width=60,
                command=lambda user=u: EditUserWindow(self, user[0], user[1:], self.admin_user_crud_view),
            ).pack(side="right", padx=5)
        conn.close()

    def user_my_rentals_view(self):
        for w in self.content.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.content, text="My Active Rentals", font=("Arial", 24, "bold")).pack(
            anchor="w", pady=10
        )
        scroll = ctk.CTkScrollableFrame(self.content)
        scroll.pack(fill="both", expand=True)
        conn = sqlite3.connect("car_rental.db")
        for b in conn.execute(
            "SELECT * FROM bookings WHERE customer_name=? AND status='Active'", (self.current_user,)
        ).fetchall():
            over = self.check_overdue(b[5])
            r = ctk.CTkFrame(scroll, border_width=2 if over else 0, border_color="red")
            r.pack(fill="x", pady=10, padx=10)
            ctk.CTkLabel(r, text=f"{b[2]}", font=("Arial", 18, "bold")).pack(
                anchor="w", padx=20, pady=(10, 0)
            )
            txt = "🚨 OVERDUE - PLEASE RETURN" if over else f"Return by: {b[5]}"
            ctk.CTkLabel(r, text=txt, text_color="red" if over else "gray").pack(
                anchor="w", padx=20, pady=(0, 10)
            )
            ctk.CTkButton(
                r,
                text="Return Vehicle",
                fg_color="#27AE60",
                command=lambda bid=b[0], cid=b[3]: self.process_return(bid, cid, self.user_my_rentals_view),
            ).pack(side="right", padx=20, pady=10)
        conn.close()

    def process_return(self, bid, cid, refresh):
        conn = sqlite3.connect("car_rental.db")
        conn.execute("UPDATE cars SET status='Available' WHERE id=?", (cid,))
        conn.execute("UPDATE bookings SET status='Returned' WHERE id=?", (bid,))
        conn.commit()
        conn.close()
        refresh()

    def admin_fleet_view(self):
        for w in self.content.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.content, text="Fleet Control", font=("Arial", 24, "bold")).pack(anchor="w")
        f = ctk.CTkFrame(self.content)
        f.pack(fill="x", pady=10)
        b_e = ctk.CTkEntry(f, placeholder_text="Brand", width=120)
        b_e.grid(row=0, column=0, padx=5)
        m_e = ctk.CTkEntry(f, placeholder_text="Model", width=120)
        m_e.grid(row=0, column=1, padx=5)
        p_e = ctk.CTkEntry(f, placeholder_text="Price", width=80)
        p_e.grid(row=0, column=2, padx=5)

        def add():
            conn = sqlite3.connect("car_rental.db")
            conn.execute(
                "INSERT INTO cars (brand, model, price_per_day) VALUES (?, ?, ?)",
                (b_e.get(), m_e.get(), float(p_e.get())),
            )
            conn.commit()
            conn.close()
            self.admin_fleet_view()

        ctk.CTkButton(f, text="Add", width=80, command=add).grid(row=0, column=3, padx=5)
        scroll = ctk.CTkScrollableFrame(self.content)
        scroll.pack(fill="both", expand=True)
        conn = sqlite3.connect("car_rental.db")
        for c in conn.execute("SELECT * FROM cars").fetchall():
            r = ctk.CTkFrame(scroll)
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=f"{c[2]} {c[1]} - ${c[3]}/d", width=250, anchor="w").pack(
                side="left", padx=10
            )
            ctk.CTkButton(
                r,
                text="Del",
                fg_color="#7B241C",
                width=60,
                command=lambda cid=c[0]: [
                    sqlite3.connect("car_rental.db")
                    .execute("DELETE FROM cars WHERE id=?", (cid,))
                    .connection.commit(),
                    self.admin_fleet_view(),
                ],
            ).pack(side="right", padx=5)
            ctk.CTkButton(
                r,
                text="Edit",
                fg_color="#2E86C1",
                width=60,
                command=lambda car=c: EditCarWindow(self, car[0], car[1:4], self.admin_fleet_view),
            ).pack(side="right", padx=5)
        conn.close()

    def user_rent_view(self):
        for w in self.content.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.content, text="Available for Booking", font=("Arial", 24, "bold")).pack(
            anchor="w", pady=10
        )
        scroll = ctk.CTkScrollableFrame(self.content)
        scroll.pack(fill="both", expand=True)
        conn = sqlite3.connect("car_rental.db")
        for c in conn.execute("SELECT * FROM cars WHERE status='Available'").fetchall():
            r = ctk.CTkFrame(scroll, fg_color="#2b2b2b")
            r.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(r, text=f"{c[2]} {c[1]} - ${c[3]}/day", font=("Arial", 16)).pack(
                side="left", padx=20, pady=15
            )
            d_e = ctk.CTkEntry(r, placeholder_text="Days", width=60)
            d_e.pack(side="right", padx=10)
            ctk.CTkButton(
                r, text="Rent Now", width=100, command=lambda car=c, ent=d_e: self.rent_proc(car, ent)
            ).pack(side="right", padx=10)
        conn.close()

    def rent_proc(self, car, ent):
        try:
            d = int(ent.get())
            now = datetime.now()
            due = now + timedelta(days=d)
            conn = sqlite3.connect("car_rental.db")
            conn.execute("UPDATE cars SET status='Rented' WHERE id=?", (car[0],))
            conn.execute(
                "INSERT INTO bookings (customer_name, car_model, car_id, date_rented, due_date, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    self.current_user,
                    f"{car[2]} {car[1]}",
                    car[0],
                    now.strftime("%Y-%m-%d"),
                    due.strftime("%Y-%m-%d"),
                    d * car[3],
                ),
            )
            conn.commit()
            conn.close()
            self.user_rent_view()
            messagebox.showinfo("Success", "Booking Confirmed!")
        except:
            messagebox.showerror("Error", "Enter number of days")


if __name__ == "__main__":
    init_db()
    app = CarRentalApp()
    app.mainloop()

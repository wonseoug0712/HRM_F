import tkinter as tk
from tkinter import simpledialog, messagebox, Listbox, Entry, Label, Button, END, OptionMenu, StringVar
import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_table()

    def setup_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                age INTEGER NOT NULL,
                position TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                user_id INTEGER,
                content TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

    def add_user(self, username, age, position, email, phone):
        self.cursor.execute('INSERT INTO users (username, age, position, email, phone) VALUES (?, ?, ?, ?, ?)',
                            (username, age, position, email, phone))
        self.conn.commit()

    def fetch_all_users(self, order_by='username'):
        if order_by == 'username':
            self.cursor.execute('SELECT * FROM users ORDER BY username')
        elif order_by == 'age':
            self.cursor.execute('SELECT * FROM users ORDER BY age')
        elif order_by == 'position':
            positions = ['인턴', '사원', '주임', '대리', '과장', '차장', '부장', '이사', '상무', '전무', '부사장', '사장']
            position_clause = 'CASE position ' + ' '.join(f"WHEN '{pos}' THEN {i}" for i, pos in enumerate(positions)) + ' END'
            self.cursor.execute(f'SELECT * FROM users ORDER BY {position_clause}')
        return self.cursor.fetchall()

    def fetch_user_info(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()

    def delete_user(self, user_id):
        self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.conn.commit()

    def add_note(self, user_id, content):
        self.cursor.execute('INSERT INTO notes (user_id, content) VALUES (?, ?)', (user_id, content))
        self.conn.commit()

    def fetch_notes(self, user_id):
        self.cursor.execute('SELECT content FROM notes WHERE user_id = ?', (user_id,))
        return self.cursor.fetchall()

    def search_users(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username LIKE ?', ('%' + username + '%',))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

def add_user():
    username = simpledialog.askstring("Add User", "Enter username:")
    age = simpledialog.askinteger("Add User", "Enter age:")
    position = simpledialog.askstring("Add User", "Enter position:")
    email = simpledialog.askstring("Add User", "Enter email:")
    phone = simpledialog.askstring("Add User", "Enter phone:")
    db.add_user(username, age, position, email, phone)
    messagebox.showinfo("Info", "User added successfully!")
    populate_list()

def view_user_info():
    try:
        selected_index = user_list.curselection()[0]
        user_id = user_ids[selected_index]
        user_info = db.fetch_user_info(user_id)
        info_text = f"ID: {user_info[0]}, Username: {user_info[1]}, Age: {user_info[2]}, Position: {user_info[3]}, Email: {user_info[4]}, Phone: {user_info[5]}"
        notes = db.fetch_notes(user_id)
        notes_text = '\n'.join(note[0] for note in notes)
        messagebox.showinfo("User Info", info_text + "\nNotes:\n" + notes_text)
    except IndexError:
        messagebox.showerror("Error", "Please select a user from the list")

def delete_user():
    try:
        selected_index = user_list.curselection()[0]
        user_id = user_ids[selected_index]
        db.delete_user(user_id)
        messagebox.showinfo("Info", "User deleted successfully!")
        populate_list()
    except IndexError:
        messagebox.showerror("Error", "Please select a user from the list")

def add_note():
    try:
        selected_index = user_list.curselection()[0]
        user_id = user_ids[selected_index]
        note_content = simpledialog.askstring("Add Note", "Enter note content:")
        if note_content:
            db.add_note(user_id, note_content)
            messagebox.showinfo("Info", "Note added successfully!")
    except IndexError:
        messagebox.showerror("Error", "Please select a user from the list")

def search_user():
    query = search_entry.get()
    user_list.delete(0, END)
    user_ids.clear()
    users = db.search_users(query)
    for user in users:
        user_list.insert(END, f"{user[1]} - {user[3]} - {user[2]}")
        user_ids.append(user[0])

def change_font(new_font):
    user_list.configure(font=(new_font, 12))
    for widget in window.winfo_children():
        if isinstance(widget, Button) or isinstance(widget, Label):
            widget.configure(font=(new_font, 12))

def populate_list(order_by='username'):
    user_list.delete(0, END)
    user_ids.clear()
    users = db.fetch_all_users(order_by)
    for user in users:
        user_list.insert(END, f"{user[1]} - {user[3]} - {user[2]}")
        user_ids.append(user[0])

# GUI setup
window = tk.Tk()
window.title("User Management System")
window.geometry("800x500")
window.configure(bg='light gray')

# Styling
label_style = {'bg': 'light gray', 'font': ('Arial', 12)}

# Layout frames
top_frame = tk.Frame(window, bg='light gray')
top_frame.pack(side=tk.TOP, fill=tk.X)
middle_frame = tk.Frame(window, bg='light gray')
middle_frame.pack(fill=tk.X)
bottom_frame = tk.Frame(window, bg='light gray')
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Font selection
font_var = StringVar(window)
font_var.set("Arial")  # default value
fonts = ["Arial", "Times New Roman", "Helvetica", "Courier"]
font_menu = OptionMenu(top_frame, font_var, *fonts, command=change_font)
font_menu.pack(side=tk.RIGHT, padx=10, pady=10)

# Search box
Label(top_frame, text="Search User:", **label_style).pack(side=tk.LEFT, padx=10, pady=10)
search_entry = Entry(top_frame, font=('Arial', 12), width=20)
search_entry.pack(side=tk.LEFT, padx=10)
search_button = Button(top_frame, text="Search", command=search_user, font=('Arial', 12))
search_button.pack(side=tk.LEFT, padx=10)

# User list
user_list = Listbox(middle_frame, width=80, height=15, font=('Arial', 12))
user_list.pack(padx=20, pady=20)

# Buttons for sorting
sort_frame = tk.Frame(window, bg='light gray')
sort_frame.pack(fill=tk.X)
name_sort_btn = Button(sort_frame, text="Sort by Name", command=lambda: populate_list('username'), font=('Arial', 12))
name_sort_btn.pack(side=tk.LEFT, padx=10, pady=10)
age_sort_btn = Button(sort_frame, text="Sort by Age", command=lambda: populate_list('age'), font=('Arial', 12))
age_sort_btn.pack(side=tk.LEFT, padx=10)
position_sort_btn = Button(sort_frame, text="Sort by Position", command=lambda: populate_list('position'), font=('Arial', 12))
position_sort_btn.pack(side=tk.LEFT, padx=10)

# Buttons
add_button = Button(bottom_frame, text="Add User", command=add_user, font=('Arial', 12), width=15)
add_button.pack(side=tk.LEFT, padx=10, pady=10)
view_info_button = Button(bottom_frame, text="View Info", command=view_user_info, font=('Arial', 12), width=15)
view_info_button.pack(side=tk.LEFT, padx=10)
add_note_button = Button(bottom_frame, text="Add Note", command=add_note, font=('Arial', 12), width=15)
add_note_button.pack(side=tk.LEFT, padx=10)
delete_button = Button(bottom_frame, text="Delete User", command=delete_user, font=('Arial', 12), width=15)
delete_button.pack(side=tk.LEFT, padx=10)

user_ids = []  # to store user IDs

# Database setup and initial list population
db = DatabaseManager('users.db')
populate_list()  # initially populate the list

window.mainloop()

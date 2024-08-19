import tkinter as tk
from tkinter import messagebox, filedialog
from db_analyze import DatabaseHandler

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLAlchemy GUI")

        # Database File selection
        self.db_path = tk.StringVar()
        self.db_path.set("No file selected")
        self.db_label = tk.Label(root, textvariable=self.db_path)
        self.db_label.grid(row=0, column=0, columnspan=2)
        self.db_button = tk.Button(root, text="Select DB File", command=self.select_db_file)
        self.db_button.grid(row=1, column=0, columnspan=2)

        # Table selection dropdown
        self.table_label = tk.Label(root, text="Select Table:")
        self.table_label.grid(row=2, column=0)
        self.table_var = tk.StringVar(root)
        self.table_dropdown = tk.OptionMenu(root, self.table_var, "")
        self.table_dropdown.grid(row=2, column=1)

        # Dynamic fields frame
        self.fields_frame = tk.Frame(root)
        self.fields_frame.grid(row=3, column=0, columnspan=2)

        # Row count label
        self.row_count_label = tk.Label(root, text="")
        self.row_count_label.grid(row=4, column=0, columnspan=2)

        # Buttons
        self.add_button = tk.Button(root, text="Add Entry", command=self.add_entry, state=tk.DISABLED)
        self.add_button.grid(row=5, column=0)
        
        self.update_button = tk.Button(root, text="Update Entry", command=self.update_entry, state=tk.DISABLED)
        self.update_button.grid(row=5, column=1)
        
        self.delete_button = tk.Button(root, text="Delete Entry", command=self.delete_entry, state=tk.DISABLED)
        self.delete_button.grid(row=6, column=0)
        
        self.query_button = tk.Button(root, text="Query Entries", command=self.query_entries, state=tk.DISABLED)
        self.query_button.grid(row=6, column=1)
        
        self.result_text = tk.Text(root, height=10, width=50)
        self.result_text.grid(row=7, column=0, columnspan=2)

        self.db_handler = None
        self.fields = {}

    def select_db_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("SQLite Database Files", "*.db")])
        if file_path:
            self.db_path.set(file_path)
            self.db_handler = DatabaseHandler(file_path)
            self.update_table_dropdown()

    def update_table_dropdown(self):
        tables = list(self.db_handler.get_table_names())
        if tables:
            self.table_var.set(tables[0])  # Set the first table name initially
            self.table_dropdown['menu'].delete(0, 'end')  # Clear existing menu items
            for table in tables:
                self.table_dropdown['menu'].add_command(
                    label=table, 
                    command=lambda t=table: self.table_var.set(t) or self.update_fields(t)
                )
            self.update_fields(tables[0])  # Initialize fields with the first table
            self.enable_buttons()
        else:
            messagebox.showerror("Error", "No tables found in the selected database")

    def update_fields(self, table_name):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.fields = {}
        self.db_handler.set_current_table(table_name)
        columns = self.db_handler.get_columns()
        if not columns:
            messagebox.showerror("Error", "No columns found in the selected table")
            return

        for idx, column in enumerate(columns):
            label = tk.Label(self.fields_frame, text=column + ":")
            label.grid(row=idx, column=0)
            entry = tk.Entry(self.fields_frame)
            entry.grid(row=idx, column=1)
            self.fields[column] = entry

        self.show_row_count()
        self.enable_buttons()

    def show_row_count(self):
        if self.db_handler.current_table is None:
            self.row_count_label.config(text="No table selected.")
            return

        entries = self.db_handler.query_entries()
        row_count = len(entries)

        self.row_count_label.config(text=f"Table has {row_count} rows. Next row will be {row_count}.")

    def enable_buttons(self):
        self.add_button.config(state=tk.NORMAL)
        self.update_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)
        self.query_button.config(state=tk.NORMAL)
        print("Buttons enabled")  # 调试信息

    def add_entry(self):
        try:
            data = {column: entry.get() for column, entry in self.fields.items()}
            print("Adding entry with data:", data)  # 调试信息
            self.db_handler.add_entry(**data)
            messagebox.showinfo("Success", "Entry added successfully")
            self.update_fields(self.table_var.get())  # 更新字段以反映新的行数
        except Exception as e:
            print("Error adding entry:", e)
            messagebox.showerror("Error", f"Failed to add entry: {e}")

    def update_entry(self):
        try:
            primary_key = list(self.fields.keys())[0]
            where_clause = (self.db_handler.current_table.c[primary_key] == self.fields[primary_key].get())
            data = {column: entry.get() for column, entry in self.fields.items()}
            self.db_handler.update_entry(where_clause, **data)
            messagebox.showinfo("Success", "Entry updated successfully")
        except Exception as e:
            print("Error updating entry:", e)
            messagebox.showerror("Error", f"Failed to update entry: {e}")

    def delete_entry(self):
        try:
            primary_key = list(self.fields.keys())[0]
            where_clause = (self.db_handler.current_table.c[primary_key] == self.fields[primary_key].get())
            self.db_handler.delete_entry(where_clause)
            messagebox.showinfo("Success", "Entry deleted successfully")
        except Exception as e:
            print("Error deleting entry:", e)
            messagebox.showerror("Error", f"Failed to delete entry: {e}")

    def query_entries(self):
        try:
            self.db_handler.set_current_table(self.table_var.get())
            entries = self.db_handler.query_entries()
            self.result_text.delete(1.0, tk.END)
            for row in entries:
                entry_text = ', '.join([f"{column}: {value}" for column, value in row.items()])
                self.result_text.insert(tk.END, entry_text + "\n")
        except Exception as e:
            print("Error querying entries:", e)
            messagebox.showerror("Error", f"Failed to query entries: {e}")

# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()

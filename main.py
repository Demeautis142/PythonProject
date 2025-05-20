import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import sqlite3


class MyDatabase:

    def __init__(self):
        self.conn = sqlite3.connect("mydatabase.db")
        self.cursor = self.conn.cursor()

        self.create_table_text = '''CREATE TABLE IF NOT EXISTS ingredient (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT, 
                                    count INT, 
                                    value REAL)'''
        self.insert_table_text = "INSERT INTO ingredient (name, count, value) VALUES (?, ?, ?)"
        self.read_table_text = "SELECT * FROM ingredient WHERE id=?"
        self.read_all_table_text = "SELECT * FROM ingredient"
        self.update_table_text = "UPDATE ingredient SET name=?, count=?, value=? WHERE id=?"
        self.update_table_name_text = "UPDATE ingredient SET name=?, count=?, value=? WHERE name=?"
        self.delete_table_text = "DELETE FROM ingredient WHERE id=?"
        self.delete_all_table_text = "DELETE FROM ingredient"
        self.cursor.execute(self.create_table_text)

    def insert_ingredient(self, name, count, value):
        self.cursor.execute(self.insert_table_text, (name, count, value))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_ingredient(self, id):
        self.cursor.execute(self.read_table_text, (id,))
        return self.cursor.fetchone()

    def get_all_ingredient(self):
        self.cursor.execute(self.read_all_table_text)
        return self.cursor.fetchall()

    def update_ingredient(self, id, name, count, value):
        self.cursor.execute(self.update_table_text, (name, count, value, id))
        self.conn.commit()
        return self.cursor.rowcount

    def update_ingredient_name(self, name, count, value):
        self.cursor.execute(self.update_table_text, (name, count, value, name))
        self.conn.commit()
        return self.cursor.rowcount

    def delete_ingredient(self, id):
        self.cursor.execute(self.delete_table_text, (id,))
        self.conn.commit()
        return self.cursor.rowcount

    def delete_all_ingredient(self):
        self.cursor.execute(self.delete_all_table_text)
        self.conn.commit()
        return self.cursor.rowcount

    def close_connection(self):
        self.conn.close()


mdb = MyDatabase()
products = mdb.get_all_ingredient()


def update_list_products():
    for item in tree.get_children():
        tree.delete(item)
    products = mdb.get_all_ingredient()
    for product in products:
        tree.insert("", tk.END, values=product)
    list_products = [tree.item(item, "values")[0] for item in tree.get_children()]
    combo_products["values"] = list_products


def add_product():
    name = entry_name.get()
    count = entry_quantity.get()
    value = entry_price.get()

    if name and count.isdigit() and value.replace('.', '', 1).isdigit():
        mdb.insert_ingredient(name, count, value)

        entry_name.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        entry_price.delete(0, tk.END)
        label_message.config(text="Product successfully added", fg="green")
        update_list_products()
    else:
        label_message.config(text="Please enter valid values", fg="red")


def modify_product():
    id = combo_products.get()

    if not id:
        label_message.config(text="Select a product", fg="red")
        return

    name = entry_name.get()
    count = entry_quantity.get()
    value = entry_price.get()

    if count.isdigit() and value.replace('.', '', 1).isdigit():
        count = int(count)
        value = float(value)
        mdb.update_ingredient(id, name, count, value)
        label_message.config(text="Correctly modified product", fg="green")
        update_list_products()
    else:
        label_message.config(text="Please enter valid values", fg="red")


def calculate_total():
    total = 0
    for item in tree.get_children():
        values = tree.item(item, "values")
        cant = int(values[2])
        value = float(values[3])
        total += cant * value

    label_total.config(text=f"Total: ${total:.2f}")


def graph_product():
    names = []
    quantities = []

    for item in tree.get_children():
        values = tree.item(item, "values")
        names.append(values[1])
        quantities.append(int(values[2]))

    plt.figure(figsize=(8, 5))
    plt.bar(names, quantities, color='royalblue')
    plt.xlabel("Product")
    plt.ylabel("Amount")
    plt.title("Quantity of products")
    plt.xticks(rotation=45)
    plt.show()


def remove_product():
    id = combo_products.get()

    if not id:
        label_message.config(text="Select a product", fg="red")
        return

    mdb.delete_ingredient(id)
    label_message.config(text="Correctly modified product", fg="green")
    update_list_products()
    entry_name.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    combo_products.set('')


def export_txt():
    with open("products.txt", "w") as archivo:
        archivo.write("ID\tProduct\tAmount\tPrice\n")
        for item in tree.get_children():
            values = tree.item(item, "values")
            name = values[1]
            count = int(values[2])
            price = float(values[3])
            archivo.write(f"{values[0]}\t{values[1]}\t{values[2]}\t${price:.2f}\n")
    label_message.config(text="Products exported to products.txt", fg="blue")


def on_closing():
    mdb.close_connection()
    root.destroy()


def on_select(event):
    selected_item = combo_products.get()
    list_ingredient = mdb.get_ingredient(selected_item)
    entry_name.delete(0, tk.END)
    entry_name.insert(0, list_ingredient[1])
    entry_quantity.delete(0, tk.END)
    entry_quantity.insert(0, list_ingredient[2])
    entry_price.delete(0, tk.END)
    entry_price.insert(0, list_ingredient[3])


root = tk.Tk()
root.title("Product List")

frame_tabla = tk.Frame(root)
frame_tabla.pack(side=tk.LEFT, padx=10, pady=10)

frame_form = tk.Frame(root)
frame_form.pack(side=tk.LEFT, padx=10, pady=10)

frame_action = tk.Frame(root)
frame_action.pack(side=tk.LEFT, padx=10, pady=10)

tree = ttk.Treeview(frame_tabla, columns=("ID", "Product", "Amount", "Price"), show="headings")

tree.heading("ID", text="ID")
tree.heading("Product", text="Product")
tree.heading("Amount", text="Amount")
tree.heading("Price", text="Price")

tree.column("ID", width=50)
tree.column("Product", width=150)
tree.column("Amount", width=80)
tree.column("Price", width=80)

tree.pack()


tk.Label(frame_form, text="Name:").pack()
entry_name = tk.Entry(frame_form)
entry_name.pack()

tk.Label(frame_form, text="Amount:").pack()
entry_quantity = tk.Entry(frame_form)
entry_quantity.pack()

tk.Label(frame_form, text="Price:").pack()
entry_price = tk.Entry(frame_form)
entry_price.pack()

button_add = tk.Button(frame_form, text="Add product", command=add_product)
button_add.pack(pady=5)

tk.Label(frame_action, text="Select product to modify:").pack()
combo_products = ttk.Combobox(frame_action)


combo_products.bind("<<ComboboxSelected>>", on_select)

combo_products.pack()
update_list_products()

button_modify = tk.Button(frame_action, text="Modify product", command=modify_product)
button_modify.pack(pady=5)

button_total = tk.Button(frame_action, text="Calculate total", command=calculate_total)
button_total.pack(pady=5)

button_graph = tk.Button(frame_action, text="Graph products", command=graph_product)
button_graph.pack(pady=5)

button_graph = tk.Button(frame_action, text="Delete product", command=remove_product)
button_graph.pack(pady=5)

button_export = tk.Button(frame_action, text="Export a TXT", command=export_txt)
button_export.pack(pady=5)

label_total = tk.Label(frame_action, text="Total: $0.00")
label_total.pack()

label_message = tk.Label(frame_action, text="")
label_message.pack()

root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == '__main__':
    root.mainloop()

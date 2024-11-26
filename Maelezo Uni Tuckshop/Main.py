import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.simpledialog
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from ttkthemes import ThemedTk

# Initialize Firebase
cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


class TuckShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tuck Shop Management System")
        self.root.geometry("1200x700")

        # Style Configuration
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Helvetica", 24, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 12))
        self.style.configure("Card.TFrame", relief="raised", padding=10)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Main container
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.grid(row=0, column=0, sticky="nsew")

        # Header
        header = ttk.Frame(self.main_container)
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(header, text="Tuck Shop Management",
                  style="Title.TLabel").pack()
        ttk.Label(header, text="Manage your treats and offers with ease",
                  style="Subtitle.TLabel").pack()

        # Left Panel - Item Management
        self.left_panel = ttk.LabelFrame(
            self.main_container, text="Item Management", padding="10")
        self.left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        # Item Form
        self.setup_item_form()

        # Right Panel - Item List
        self.right_panel = ttk.LabelFrame(
            self.main_container, text="Available Items", padding="10")
        self.right_panel.grid(row=1, column=1, sticky="nsew")

        # Items Treeview
        self.setup_items_treeview()

        # Offers Panel
        self.offers_panel = ttk.LabelFrame(
            self.main_container, text="Special Offers", padding="10")
        self.offers_panel.grid(
            row=2, column=0, columnspan=2, sticky="nsew", pady=(20, 0))

        self.setup_offers_section()

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)

    def setup_item_form(self):
        # Item Form Fields
        fields = ['Name', 'Price', 'Category', 'Stock']
        self.item_vars = {field: tk.StringVar() for field in fields}

        for i, field in enumerate(fields):
            ttk.Label(self.left_panel, text=field).grid(
                row=i, column=0, pady=5, padx=5, sticky="w")
            ttk.Entry(self.left_panel, textvariable=self.item_vars[field]).grid(
                row=i, column=1, pady=5, padx=5, sticky="ew")

        # Buttons
        button_frame = ttk.Frame(self.left_panel)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Item",
                   command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update",
                   command=self.update_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete",
                   command=self.delete_item).pack(side=tk.LEFT, padx=5)

    def setup_items_treeview(self):
        columns = ('name', 'price', 'category', 'stock')
        self.tree = ttk.Treeview(
            self.right_panel, columns=columns, show='headings')

        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=100)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.right_panel, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind select event
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)

        # Configure grid weights
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(0, weight=1)

    def setup_offers_section(self):
        # Offers management
        offers_frame = ttk.Frame(self.offers_panel)
        offers_frame.pack(fill=tk.X, expand=True)

        # Current offers display
        self.offers_text = tk.Text(offers_frame, height=4, width=50)
        self.offers_text.pack(side=tk.LEFT, fill=tk.BOTH,
                              expand=True, padx=(0, 10))

        # Offer controls
        offer_controls = ttk.Frame(offers_frame)
        offer_controls.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Button(offer_controls, text="Add Offer",
                   command=self.add_offer).pack(pady=2)
        ttk.Button(offer_controls, text="Remove Offer",
                   command=self.remove_offer).pack(pady=2)

    def load_data(self):
        # Load items from Firebase
        items_ref = db.collection('items')
        items = items_ref.get()

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert items into treeview
        for item in items:
            data = item.to_dict()
            self.tree.insert('', tk.END, values=(
                data['name'],
                data['price'],
                data['category'],
                data['stock']
            ))

        # Load offers
        offers_ref = db.collection('offers').get()
        self.offers_text.delete(1.0, tk.END)
        for offer in offers_ref:
            self.offers_text.insert(
                tk.END, f"• {offer.to_dict()['description']}\n")

    def add_item(self):
        # Get values from form
        item_data = {field.lower(): var.get()
                     for field, var in self.item_vars.items()}

        # Validate data
        if not all(item_data.values()):
            messagebox.showerror("Error", "All fields are required!")
            return

        # Add to Firebase
        db.collection('items').add(item_data)

        # Refresh display
        self.load_data()
        self.clear_form()

    def update_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Warning", "Please select an item to update!")
            return

        # Get values from form
        item_data = {field.lower(): var.get()
                     for field, var in self.item_vars.items()}

        # Update in Firebase
        item_ref = db.collection('items').where(
            'name', '==', self.tree.item(selected[0])['values'][0])
        for doc in item_ref.get():
            doc.reference.update(item_data)

        # Refresh display
        self.load_data()
        self.clear_form()

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Warning", "Please select an item to delete!")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            # Delete from Firebase
            item_ref = db.collection('items').where(
                'name', '==', self.tree.item(selected[0])['values'][0])
            for doc in item_ref.get():
                doc.reference.delete()

            # Refresh display
            self.load_data()
            self.clear_form()

    def item_selected(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']

            # Update form fields
            for field, value in zip(self.item_vars.keys(), values):
                self.item_vars[field].set(value)

    def clear_form(self):
        for var in self.item_vars.values():
            var.set('')

    def add_offer(self):
        # Simple dialog for adding offers
        offer = tkinter.simpledialog.askstring(
            "New Offer", "Enter offer description:")
        if offer:
            db.collection('offers').add({
                'description': offer,
                'created_at': datetime.now()
            })
            self.load_data()

    def remove_offer(self):
        # Get selected offer text
        try:
            selected_line = self.offers_text.get("sel.first", "sel.last")
            if messagebox.askyesno("Confirm Delete", "Delete selected offer?"):
                # Delete from Firebase
                offer_ref = db.collection('offers').where(
                    'description', '==', selected_line.strip('• \n'))
                for doc in offer_ref.get():
                    doc.reference.delete()
                self.load_data()
        except tk.TclError:
            messagebox.showwarning(
                "Warning", "Please select an offer to remove!")


if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Using a modern theme
    app = TuckShopApp(root)
    root.mainloop()

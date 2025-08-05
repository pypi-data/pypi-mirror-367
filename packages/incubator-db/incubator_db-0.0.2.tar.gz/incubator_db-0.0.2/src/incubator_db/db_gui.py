import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from src.incubator_db.db import DB

class GUI:
    def __init__(self):
        self.root = ttk.Window(title = "Incubator Data Base", themename="superhero")
        self.root.geometry("1200x800")
        self.db = DB()
        self.tables = self.db.get_tables()

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=8)

        style = ttk.Style()
        style.configure("Default.TButton")

        self.bool_slot = False
        self.bool_plate_actions = False
        self.bool_plates = False

        self.button_slots = ttk.Button(text="Slots", style="Default.TButton", command=self.callback_slots)
        self.button_plates = ttk.Button(text="Plates", style="Default.TButton", command = self.callback_plates)
        self.button_plate_actions = ttk.Button(text="PlateActions", style="Default.TButton", command = self.callback_plate_actions)

        self.button_slots.grid(column=0, row=0, sticky='nsew', ipady=12)
        self.button_plates.grid(column=1, row= 0, sticky='nsew', ipady=12)
        self.button_plate_actions.grid(column=2, row=0, sticky='nsew', ipady=12)

        self.tree_plates = ttk.Treeview(self.root)
        self.tree_plate_actions = ttk.Treeview(self.root)
        self.tree_slots = ttk.Treeview(self.root)

        self.init_tree_plates()
        self.init_tree_plate_actions()
        self.init_tree_slots()
        self.insert_data()
        self.current_tree = self.tree_plates
        self.current_tree.grid()


    def get_root(self)->ttk.Window:
        return self.root

    def init_tree_plates(self):
        columns = self.db.get_columns_from_table(self.tables[1])
        self.tree_plates["columns"] = columns

        self.tree_plates.column("#0", width=0, stretch=False)
        self.tree_plates.heading("#0", text="")

        for i in columns:
            self.tree_plates.column(i, anchor=CENTER)
            self.tree_plates.heading(i, text=i, anchor=CENTER)

        self.tree_plates.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=5)
        self.tree_plates.grid_remove()

    def init_tree_slots(self):
        columns = self.db.get_columns_from_table(self.tables[2])
        self.tree_slots["columns"] = columns

        self.tree_slots.column("#0", width=0, stretch=False)
        self.tree_slots.heading("#0", text="")

        for i in columns:
            self.tree_slots.column(i, anchor=CENTER)
            self.tree_slots.heading(i, text = i, anchor=CENTER)

        self.tree_slots.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=5)
        self.tree_slots.grid_remove()

    def init_tree_plate_actions(self):
        columns = self.db.get_columns_from_table(self.tables[0])
        self.tree_plate_actions["columns"] = columns

        self.tree_plate_actions.column("#0", width=0, stretch=False)
        self.tree_plate_actions.heading("#0", text="")

        for i in columns:
            self.tree_plate_actions.column(i, anchor=CENTER)
            self.tree_plate_actions.heading(i, text=i, anchor=CENTER)

        self.tree_plate_actions.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=5)
        self.tree_plate_actions.grid_remove()


    def insert_data(self):
        table_data_plate_action: list[tuple] = self.db.get_table_data(self.tables[0])
        table_data_plates: list[tuple] = self.db.get_table_data(self.tables[1])
        table_data_slots: list[tuple] = self.db.get_table_data(self.tables[2])

        for i in range(len(table_data_plate_action)):
            self.tree_plates.insert(parent="", index = 'end', iid=i, text="Parent", values=table_data_plate_action[i])

        for i in range(len(table_data_plates)):
            self.tree_plates.insert(parent="", index = 'end', iid=i, text="Parent", values=table_data_plates[i])

        for i in range(len(table_data_slots)):
            self.tree_plates.insert(parent="", index = 'end', iid=i, text="Parent", values=table_data_slots[i])

    def callback_slots(self):
        if self.bool_slot:
            return

        self.bool_plates = False
        self.bool_plate_actions = False
        self.bool_slot = True
        self.current_tree.grid_remove()
        self.current_tree = self.tree_slots
        self.current_tree.grid()

    def callback_plates(self):
        if self.bool_plates:
            return

        self.bool_slot = False
        self.bool_plate_actions = False
        self.bool_plates = True
        self.current_tree.grid_remove()
        self.current_tree = self.tree_plates
        self.current_tree.grid()

    def callback_plate_actions(self):
        if self.bool_plate_actions:
            return

        self.bool_plates = False
        self.bool_slot = False
        self.bool_plate_actions = True
        self.current_tree.grid_remove()
        self.current_tree = self.tree_plate_actions
        self.current_tree.grid()
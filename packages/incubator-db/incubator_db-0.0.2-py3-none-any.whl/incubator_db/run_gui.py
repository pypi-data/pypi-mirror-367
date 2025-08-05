def run_gui():
    from src.incubator_db.db_gui import GUI
    gui = GUI()
    root=gui.get_root()
    root.mainloop()
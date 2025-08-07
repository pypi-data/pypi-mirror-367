import sqlite3
import logging
from .setup_db import create_db, get_db_path

class DB:
    def __init__(self)->None:
        create_db()

        self.conn = sqlite3.connect(get_db_path())
        self.cursor = self.conn.cursor()

    def get_location_from_plate_id(self, plate_id: str) -> int:
        self.cursor.execute("SELECT Location FROM Plates WHERE PlateId = ?", (plate_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_owner_from_plate_id(self, plate_id: str) -> str:
        self.cursor.execute("SELECT Owner FROM Plates WHERE PlateId = ?", (plate_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_all_plate_ids_from_owner(self, owner: str) -> list:
        self.cursor.execute("SELECT PlateId FROM Plates WHERE Owner = ?", (owner,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_plate_ids_from_location(self, location: int) -> list:
        self.cursor.execute("SELECT PlateId FROM Plates WHERE Location = ?", (location,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_role_from_plate_id(self, plate_id: str) -> int:
        self.cursor.execute(
            "SELECT Role FROM Slots WHERE CurrentPlateId = ? OR AssignedPlatePlateId = ?",
            (plate_id, plate_id)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_current_plate_id_from_slot_stacker(self, slot: int, stacker: int) -> str:
        self.cursor.execute(
            "SELECT CurrentPlateId FROM Slots WHERE SlotNumber = ? AND Stacker = ?",
            (slot, stacker)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_assigned_plate_id_from_slot_stacker(self, slot: int, stacker: int) -> str:
        self.cursor.execute(
            "SELECT AssignedPlatePlateId FROM Slots WHERE SlotNumber = ? AND Stacker = ?",
            (slot, stacker)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_slot_stacker_from_assigned_plate_id(self, plate_id: str) -> tuple:
        self.cursor.execute(
            "SELECT SlotNumber, Stacker FROM Slots WHERE AssignedPlatePlateId = ?",
            (plate_id,)
        )
        return self.cursor.fetchone()

    def get_slot_stacker_from_current_plate_id(self, plate_id: str) -> tuple:
        self.cursor.execute(
            "SELECT SlotNumber, Stacker FROM Slots WHERE CurrentPlateId = ?",
            (plate_id,)
        )
        return self.cursor.fetchone()

    def get_tables(self)->list:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def get_columns_from_table(self, table: str)->list:
        self.cursor.execute(f"PRAGMA table_info({table})")
        return [row[1] for row in self.cursor.fetchall()]

    def get_table_data(self, table)->list[tuple[any]]:
        self.cursor.execute(f"SELECT * FROM {table}")
        return self.cursor.fetchall()

    def get_all_slots_from_role_stacker(self, role: int, stacker: int) -> list:
        self.cursor.execute(
            "SELECT SlotNumber FROM Slots WHERE Role = ? AND Stacker = ?",
            (role, stacker)
        )
        return [row[0] for row in self.cursor.fetchall()]

    def set_role_from_plate_id(self, plate_id: str, role: int):
        try:
            self.cursor.execute(
                "UPDATE Slots SET Role = ? WHERE CurrentPlateId = ? OR AssignedPlatePlateId = ?",
                (role, plate_id, plate_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting role for plate {plate_id}: {e}")

    def set_role_from_slot_stacker(self, slot: int, stacker: int, role: int):
        try:
            self.cursor.execute(
                "UPDATE Slots SET Role = ? WHERE SlotNumber = ? AND Stacker = ?",
                (role, slot, stacker)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting role for slot {slot}, stacker {stacker}: {e}")

    def set_current_plate_id_from_slot_stacker(self, slot: int, stacker: int, plate_id: str):
        try:
            self.cursor.execute(
                "UPDATE Slots SET CurrentPlateId = ? WHERE SlotNumber = ? AND Stacker = ?",
                (plate_id, slot, stacker)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting current plate {plate_id} for slot {slot}, stacker {stacker}: {e}")

    def set_assigned_plate_id_from_slot_stacker(self, slot: int, stacker: int, plate_id: str):
        try:
            self.cursor.execute(
                "UPDATE Slots SET AssignedPlatePlateId = ? WHERE SlotNumber = ? AND Stacker = ?",
                (plate_id, slot, stacker)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error assigning plate {plate_id} to slot {slot}, stacker {stacker}: {e}")

    def set_owner_from_plate_id(self, plate_id: str, owner: str):
        try:
            self.cursor.execute(
                "UPDATE Plates SET Owner = ? WHERE PlateId = ?",
                (owner, plate_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting owner {owner} for plate {plate_id}: {e}")

    def set_location_from_plate_id(self, plate_id: str, location: int):
        try:
            self.cursor.execute(
                "UPDATE Plates SET Location = ? WHERE PlateId = ?",
                (location, plate_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting location {location} for plate {plate_id}: {e}")

    def register_slot(self, slot: int, stacker: int, role: int, occupied: int, assigned_id: str, current_id: str):
        try:
            self.cursor.execute(
                """ INSERT INTO Slots (Stacker, SlotNumber, Role, Occupied, AssignedPlatePlateId, CurrentPlateId)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                (stacker, slot, role, occupied, assigned_id, current_id)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.warning(f"Slot ({stacker}, {slot}) already exists – skipping insert.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting slot ({stacker}, {slot}): {e}")

    def register_plate(self, plate_id: str, owner: str, location: int):
        try:
            self.cursor.execute(
                "INSERT INTO Plates (PlateId, Owner, Location) VALUES (?, ?, ?)",
                (plate_id, owner, location)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.warning(f"Plate {plate_id} already exists – skipping insert.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting plate {plate_id}: {e}")

    def write_plate_action(self, time_stamp: str, plate_id: str, action: str):
        try:
            self.cursor.execute(
                "INSERT INTO PlateActions (Timestamp, PlateId, Action) VALUES (?, ?, ?)",
                (time_stamp, plate_id, action)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.warning(f"Action at {time_stamp} already exists – skipping.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting plate action at {time_stamp}: {e}")
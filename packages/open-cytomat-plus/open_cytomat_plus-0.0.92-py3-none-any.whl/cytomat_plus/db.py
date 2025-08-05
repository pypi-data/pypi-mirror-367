import sqlite3
from sqlite3 import IntegrityError
from .scripts.setup_cytomat_plus import get_db_path
from pathlib import Path

class DB():
    def __init__(self):
        db_path: Path = get_db_path()

        self.conn = sqlite3.connect(db_path, timeout=10)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.data_db = self.get_SlotNumber_data()
    """
    getter 
    """
    def get_column_names(self)-> list[str]:
        column_names = ['SlotNumber', 'Role', 'AssignedPlatePlateId']
        return column_names

    def get_SlotNumber_data(self)-> list[tuple]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT SlotNumber, Role, AssignedPlatePlateId, Occupied FROM slots ORDER BY SlotNumber ASC')
        data = cursor.fetchall()
        cursor.close()
        return data
        
    def get_slots(self)-> list[int]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT SlotNumber FROM slots ORDER BY SlotNumber ASC')
        data = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return data

    def get_usable_rows(self, role: int = 0)-> list[tuple]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT SlotNumber, Role, AssignedPlatePlateId, Occupied FROM slots WHERE role = ? AND AssignedPlatePlateId IS NOT NULL ORDER BY SlotNumber ASC', (role, ))
        data = cursor.fetchall()
        cursor.close()
        return data
        
    def get_roled_slots(self)-> list[int]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT SlotNumber FROM slots WHERE NOT role = 0 ORDER BY SlotNumber ASC')
        data = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return data
    
    def get_unroled_slots(self)-> list[int]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT SlotNumber FROM slots WHERE role = 0 ORDER BY SlotNumber ASC')
        data = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return data
    
    #return dict in form of: tuple(bottom, upper): list
    def get_consecutive_slots(self)-> dict[list]:
        used_slots = self.get_unroled_slots()
        consecutive_dict = {}

        if not used_slots:
            return consecutive_dict
        
        bottom = used_slots[0]
        upper = used_slots[0]
        consecutive_slots_list = [bottom]

        for slot_idx in range (1, len(used_slots)):
            slot = used_slots[slot_idx]
            if upper + 1 == slot:
                upper = slot
                consecutive_slots_list.append(upper)
            else:
                consecutive_dict[(bottom, upper)] = consecutive_slots_list
                bottom = slot
                upper = slot
                consecutive_slots_list = [bottom]

        consecutive_dict[(bottom, upper)] = consecutive_slots_list
        return consecutive_dict

    """
    gets all rows, depending on role and converts the list of tupels into a list of dictionarys and returns it
    """
    def get_rows_role_dict(self, role: int = 0)-> list[dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT SlotNumber, Role, AssignedPlatePlateId, Occupied FROM slots WHERE Role = ? ORDER BY SlotNumber ASC', (role, ))
        data_tupels = cursor.fetchall()
        data_dicts = []
        for tupel in data_tupels:
            row_dict = {}
            row_dict['slot'] = tupel[0]
            row_dict['role'] = tupel[1]
            row_dict['plate'] = tupel[2]
            row_dict['occupied'] = tupel[3]
            data_dicts.append(row_dict)

        cursor.close()
        return data_dicts
        
    def slot(self, row_idx: int)->int:
        return self.data_db[row_idx][0]
    
    def role(self, row_idx: int)->int:
        return self.data_db[row_idx][1]
    
    def plate(self, row_idx: int)->str:
        return self.data_db[row_idx][2]

    def occupied(self, row_idx: int)->int:
        return self.data_db[row_idx][3]
    
    """
    setter
    """
    def insert_new_row(self, slot, role: int = 0, plate: str = None, occupied: int = 0, current_plate_id: str = None):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO slots (SlotNumber, Role, AssignedPlatePlateId, Occupied, CurrentPlateId) VALUES (?, ?, ?, ?, ?)', (slot, role, plate, occupied, current_plate_id))
            self.conn.commit()
            
        except IntegrityError as e:
            print(e)

        finally:
            cursor.close()

    def assigne_slot(self, slot: int):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO slots (SotNumber) VALUES (?)',(slot))
            self.conn.commit()
            
        except IntegrityError as e:
            print(e)

        finally:
            cursor.close()
            
    def update_slot(self, new_slot: int, old_slot: int):
        cursor = self.conn.cursor()
        try:
            cursor.execute('UPDATE slots SET SlotNumber = ? WHERE SlotNumber = ?', (new_slot, old_slot))
            self.conn.commit()
            
        except IntegrityError as e:
            print(e)

        finally:
            cursor.close()

    def assigne_plate(self, slot: int, plate_id:str):
        #slot = self.slot(row_idx=row_idx)
        cursor = self.conn.cursor()
        try:    
            cursor.execute('UPDATE slots SET AssignedPlatePlateId = ? WHERE SlotNumber = ?', (plate_id, slot))
            self.conn.commit()
        
        except IntegrityError as e:
            print(e)

        finally:
            cursor.close()
        
    def set_role(self, role: int, slot: int):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE slots SET Role 0 ? WHERE SlotNumber = ?', (role, slot))
        self.conn.commit()
        cursor.close()
            
    def update_occupied(self, slot: int, occupied: int):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE slots SET Occupied = ? WHERE SlotNumber = ?', (occupied, slot))
        self.conn.commit()
        cursor.close()
        
    """
    delete
    """
    def clear_entire_table(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM slots')
        self.conn.commit()
        cursor.close()
        
    def delete_plate(self, slot):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE slots SET AssignedPlatePlateId = NULL WHERE SlotNumber = ?', (slot, ))
        self.conn.commit()
        cursor.close()
    
    def delete_row(self, slot):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM slots WHERE SlotNumber = ?', (slot, ))
        self.conn.commit()
        cursor.close()

    """
    rest
    """
    def is_plate_assigned(self, plate_id)->bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM slots WHERE AssignedPlatePlateId = ?',(plate_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return True
        else:
            return False

    def write_log(self, plate_id: str, action: str, time_stamp):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO PlateActions (TimeStamp, PlateId, Acction) Values (?,?,?),',(time_stamp, plate_id, action,))
        self.conn.commit()
        cursor.close()
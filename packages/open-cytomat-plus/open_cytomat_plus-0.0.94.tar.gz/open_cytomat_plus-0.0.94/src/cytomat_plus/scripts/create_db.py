import sqlite3

class CreateDB():
    def __init__(self, path):
        self.connect = sqlite3.connect(path)

        self.create_table_plate_actions()
        self.create_table_plates()
        self.create_table_slots()
        self.create_index_plate_id()
        self.create_index_assigned_plate_plate_id()
        self.create_index_current_plate_id()

        self.connect.close()

    def create_table_plate_actions(self):
        try:
            self.connect.execute(""" CREATE TABLE "PlateActions" (
                                    "Timestamp" TEXT NOT NULL CONSTRAINT "PK_PlateActions" PRIMARY KEY,
                                    "PlateId" TEXT NULL,
                                    "Action" TEXT NULL,
                                     CONSTRAINT "FK_PlateActions_Plates_PlateId" FOREIGN KEY ("PlateId") REFERENCES "Plates" ("PlateId") ON DELETE RESTRICT)""")
        except sqlite3.OperationalError:
            pass
    
    def create_table_plates(self):
        try:
            self.connect.execute(""" CREATE TABLE "Plates" (
                                    "PlateId" TEXT NOT NULL CONSTRAINT "PK_Plates" PRIMARY KEY,
                                    "Owner" TEXT NULL,
                                    "Location" INTEGER NOT NULL)""")
        except sqlite3.OperationalError:
            pass

    def create_table_slots(self):
        try:
            self.connect.execute(""" CREATE TABLE "Slots" (
                                    "SlotNumber" INTEGER NOT NULL CONSTRAINT "PK_Slots" PRIMARY KEY AUTOINCREMENT,
                                    "Role" INTEGER NOT NULL,
                                    "Occupied" INTEGER NOT NULL,
                                    "AssignedPlatePlateId" TEXT NULL,
                                    "CurrentPlateId" TEXT NULL,
                                    CONSTRAINT "FK_Slots_Plates_AssignedPlatePlateId" FOREIGN KEY ("AssignedPlatePlateId") REFERENCES "Plates" ("PlateId") ON DELETE RESTRICT,
                                    CONSTRAINT "FK_Slots_Plates_CurrentPlateId" FOREIGN KEY ("CurrentPlateId") REFERENCES "Plates" ("PlateId") ON DELETE RESTRICT) """)
        except sqlite3.OperationalError:
            pass

    def create_index_plate_id(self):
        try:
            self.connect.execute("""CREATE INDEX "IX_PlateActions_PlateId" ON "PlateActions" ("PlateId")""")
        except sqlite3.OperationalError:
            pass

    def create_index_assigned_plate_plate_id(self):
        try:
            self.connect.execute("""CREATE UNIQUE INDEX "IX_Slots_AssignedPlatePlateId" ON "Slots" ("AssignedPlatePlateId")""")
        except sqlite3.OperationalError:
            pass

    def create_index_current_plate_id(self):
        try:
            self.connect.execute("""CREATE INDEX "IX_Slots_CurrentPlateId" ON "Slots" ("CurrentPlateId")""")
        except sqlite3.OperationalError:
            pass

def create_db(path):
    CreateDB(path)
import sys
from PyQt5.QtWidgets import QHeaderView,QSizePolicy, QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,QGridLayout, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QCheckBox, QFormLayout, QMessageBox, QInputDialog,QScrollArea, QDialog
from PyQt5.QtCore import Qt
import backend as db_ops

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Manager")
        self.setGeometry(100, 100, 800, 600)
        self.conn = db_ops.connect_to_database()
        db_ops.create_tables_metadata_table(self.conn)

        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create Table Section
        self.create_table_section()

        # Display Tables Section
        self.display_tables_section()

        # Add buttons for combining and searching tables
        self.combine_tables_button = QPushButton("Combine Tables")
        self.combine_tables_button.clicked.connect(self.open_combine_tables_dialog)
        self.layout.addWidget(self.combine_tables_button)

        self.search_tables_button = QPushButton("Search Tables")
        self.search_tables_button.clicked.connect(self.open_search_tables_dialog)
        self.layout.addWidget(self.search_tables_button)


    def open_combine_tables_dialog(self):
        dialog = CombineTablesDialog(self.conn, self)
        dialog.exec_()

    def open_search_tables_dialog(self):
        dialog = SearchTablesDialog(self.conn, self)
        dialog.exec_()



    def create_table_section(self):


        self.table_name_input = QLineEdit()
        self.table_name_input.setPlaceholderText("Enter table name")
        self.layout.addWidget(self.table_name_input)

        self.create_table_button = QPushButton("Create Table")
        self.create_table_button.clicked.connect(self.create_table)
        self.layout.addWidget(self.create_table_button)

    # Inside the MainWindow class
    def display_tables_section(self):
        self.tables_label = QLabel("Existing Tables")
        self.layout.addWidget(self.tables_label)

        # Create a widget to hold the grid layout
        tables_widget = QWidget()
        self.tables_grid = QGridLayout(tables_widget)

        # Add a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(tables_widget)
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        self.load_tables()

    def load_tables(self):
        # Clear the grid layout
        for i in reversed(range(self.tables_grid.count())):
            widget = self.tables_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        tables = db_ops.fetch_all_tables(self.conn)

        for index, table in enumerate(tables):
            row = index // 2  # Determine the row
            col = index % 2   # Determine the column (0 or 1)

            table_name = table[1]
            creation_date = db_ops.get_table_creation_date(self.conn, table_name)

            # Create a container widget for each table entry
            table_entry_widget = QWidget()
            table_entry_layout = QVBoxLayout(table_entry_widget)

            table_name_label = QLabel(f"Table: {table_name}")
            creation_date_label = QLabel(f"Created: {creation_date if creation_date else 'Unknown'}")

            view_button = QPushButton("View")
            view_button.clicked.connect(lambda _, t=table_name: self.view_table(t))

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, t=table_name: self.delete_table(t))

            table_entry_layout.addWidget(table_name_label)
            table_entry_layout.addWidget(creation_date_label)
            table_entry_layout.addWidget(view_button)
            table_entry_layout.addWidget(delete_button)

            # Add the table entry widget to the grid layout
            self.tables_grid.addWidget(table_entry_widget, row, col)

    def delete_table(self, table_name):
        reply = QMessageBox.question(
            self,
            'Delete Table',
            f"Are you sure you want to delete the table '{table_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if db_ops.delete_table(self.conn, table_name):
                QMessageBox.information(self, "Success", f"Table '{table_name}' deleted successfully.")
                self.load_tables()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete table '{table_name}'.")



    def create_table(self):
        table_name = self.table_name_input.text().strip()
        if db_ops.add_table_metadata(self.conn, table_name):
            db_ops.create_table(self.conn, table_name)
            self.load_tables()
            QMessageBox.information(self, "Success", f"Table '{table_name}' created successfully.")
        else:
            QMessageBox.warning(self, "Error", "Invalid table name or table already exists.")

    def view_table(self, table_name):
        dialog = TableDialog(self.conn, table_name, self)
        dialog.exec_()

class TableDialog(QDialog):
    def __init__(self, conn, table_name, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.table_name = table_name
        self.setWindowTitle(f"Table: {table_name}")
        self.setGeometry(150, 150, 1000, 600)
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget(self)
        layout = QVBoxLayout(self.central_widget)

        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(9)
        self.entries_table.setHorizontalHeaderLabels(["Name", "Phone", "Email", "WhatsApp", "Signal", "Telegram", "Relationship", "Notes", "Actions"])
        self.entries_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set resize mode for each column
        self.entries_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.entries_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Name
        self.entries_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Phone
        self.entries_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Email
        self.entries_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # WhatsApp
        self.entries_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Signal
        self.entries_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Telegram
        self.entries_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Relationship
        self.entries_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)           # Notes
        self.entries_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Actions

        self.entries_table.setWordWrap(True)
        self.entries_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.entries_table)

        self.load_entries()

        self.add_entry_button = QPushButton("Add Entry")
        self.add_entry_button.clicked.connect(self.add_entry)
        layout.addWidget(self.add_entry_button)

        self.setLayout(layout)


    def load_entries(self):
        self.entries_table.setRowCount(0)
        entries = db_ops.fetch_entries(self.conn, self.table_name)
        for entry in entries:
            row_position = self.entries_table.rowCount()
            self.entries_table.insertRow(row_position)
            for i, value in enumerate(entry[1:-1]):  # Skip ID and last_modified
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make item non-editable
                self.entries_table.setItem(row_position, i, item)

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda _, e=entry: self.edit_entry(e))
            self.entries_table.setCellWidget(row_position, 8, edit_button)


    def add_entry(self):
        dialog = EntryDialog(self.conn, self.table_name, self)
        dialog.exec_()
        self.load_entries()

    def edit_entry(self, entry):
        row_position = self.entries_table.rowCount()
        for i in range(self.entries_table.columnCount() - 1):  # Exclude the last column with the button
            item = self.entries_table.item(row_position, i)
            if item:
                item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make item editable

        dialog = EntryDialog(self.conn, self.table_name, self, entry)
        dialog.exec_()

        # After editing, make the items non-editable again
        for i in range(self.entries_table.columnCount() - 1):
            item = self.entries_table.item(row_position, i)
            if item:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        self.load_entries()


class EntryDialog(QDialog):
    def __init__(self, conn, table_name, parent=None, entry=None):
        super().__init__(parent)
        self.conn = conn
        self.table_name = table_name
        self.entry = entry
        self.setWindowTitle("Add/Edit Entry")
        self.setGeometry(200, 200, 400, 400)
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setLayout(QFormLayout(self.central_widget))

        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.whatsapp_input = QLineEdit()
        self.signal_input = QLineEdit()
        self.telegram_input = QLineEdit()
        self.relationship_input = QLineEdit()
        self.notes_input = QLineEdit()

        self.layout().addRow("Name:", self.name_input)
        self.layout().addRow("Phone:", self.phone_input)
        self.layout().addRow("Email:", self.email_input)
        self.layout().addRow("WhatsApp:", self.whatsapp_input)
        self.layout().addRow("Signal:", self.signal_input)
        self.layout().addRow("Telegram:", self.telegram_input)
        self.layout().addRow("Relationship:", self.relationship_input)
        self.layout().addRow("Notes:", self.notes_input)

        if self.entry:
            self.name_input.setText(self.entry[1])
            self.phone_input.setText(self.entry[2])
            self.email_input.setText(self.entry[3])
            self.whatsapp_input.setText(self.entry[4])
            self.signal_input.setText(self.entry[5])
            self.telegram_input.setText(self.entry[6])
            self.relationship_input.setText(self.entry[7])
            self.notes_input.setText(self.entry[8])

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_entry)
        self.layout().addWidget(self.save_button)

    def save_entry(self):
        entry_data = (
            self.name_input.text(),
            self.phone_input.text(),
            self.email_input.text(),
            self.whatsapp_input.text(),
            self.signal_input.text(),
            self.telegram_input.text(),
            self.relationship_input.text(),
            self.notes_input.text()
        )

        if self.entry:
            db_ops.edit_entry(self.conn, self.table_name, self.entry[0], entry_data)
        else:
            db_ops.add_entry(self.conn, self.table_name, entry_data)

        self.accept()


class CombineTablesDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Combine Tables")
        self.setGeometry(200, 200, 1000, 600)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.tables_list = QTableWidget()
        self.tables_list.setColumnCount(2)
        self.tables_list.setHorizontalHeaderLabels(["Select", "Table Name"])
        self.tables_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tables_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tables_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.layout.addWidget(self.tables_list)

        self.load_tables()

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all)
        self.layout.addWidget(self.select_all_button)

        self.unselect_all_button = QPushButton("Unselect All")
        self.unselect_all_button.clicked.connect(self.unselect_all)
        self.layout.addWidget(self.unselect_all_button)

        self.combine_button = QPushButton("Combine")
        self.combine_button.clicked.connect(self.combine_tables)
        self.layout.addWidget(self.combine_button)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(10)
        self.results_table.setHorizontalHeaderLabels(["Name", "Phone", "Email", "WhatsApp", "Signal", "Telegram", "Relationship", "Notes", "Last Modified", "Source Table"])
        self.results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set resize mode for each column
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Name
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Phone
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Email
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # WhatsApp
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Signal
        self.results_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Telegram
        self.results_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Relationship
        self.results_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)           # Notes
        self.results_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Last Modified
        self.results_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Source Table

        self.results_table.setWordWrap(True)
        self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.layout.addWidget(self.results_table)


    def load_tables(self):
        self.tables_list.setRowCount(0)
        tables = db_ops.fetch_all_tables(self.conn)
        for table in tables:
            row_position = self.tables_list.rowCount()
            self.tables_list.insertRow(row_position)

            checkbox = QCheckBox()
            self.tables_list.setCellWidget(row_position, 0, checkbox)
            self.tables_list.setItem(row_position, 1, QTableWidgetItem(table[1]))

    def select_all(self):
        for row in range(self.tables_list.rowCount()):
            checkbox = self.tables_list.cellWidget(row, 0)
            checkbox.setChecked(True)

    def unselect_all(self):
        for row in range(self.tables_list.rowCount()):
            checkbox = self.tables_list.cellWidget(row, 0)
            checkbox.setChecked(False)

    def combine_tables(self):
        selected_tables = []
        for row in range(self.tables_list.rowCount()):
            checkbox = self.tables_list.cellWidget(row, 0)
            if checkbox.isChecked():
                table_name = self.tables_list.item(row, 1).text()
                selected_tables.append(table_name)

        combined_data = db_ops.combine_tables(self.conn, selected_tables)
        self.display_combined_data(combined_data)

    def display_combined_data(self, combined_data):
        self.results_table.setRowCount(0)
        for entry in combined_data:
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            # Skip the serial ID (entry[0]) and align data with headers
            self.results_table.setItem(row_position, 0, QTableWidgetItem(str(entry[1])))  # Name
            self.results_table.setItem(row_position, 1, QTableWidgetItem(str(entry[2])))  # Phone
            self.results_table.setItem(row_position, 2, QTableWidgetItem(str(entry[3])))  # Email
            self.results_table.setItem(row_position, 3, QTableWidgetItem(str(entry[4])))  # WhatsApp
            self.results_table.setItem(row_position, 4, QTableWidgetItem(str(entry[5])))  # Signal
            self.results_table.setItem(row_position, 5, QTableWidgetItem(str(entry[6])))  # Telegram
            self.results_table.setItem(row_position, 6, QTableWidgetItem(str(entry[7])))  # Relationship
            self.results_table.setItem(row_position, 7, QTableWidgetItem(str(entry[8])))  # Notes
            self.results_table.setItem(row_position, 8, QTableWidgetItem(str(entry[10]))) # Last Modified
            self.results_table.setItem(row_position, 9, QTableWidgetItem(str(entry[11]))) # Source Table


class SearchTablesDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Search Tables")
        self.setGeometry(200, 200, 1000, 600)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term")
        self.layout.addWidget(self.search_input)

        self.tables_list = QTableWidget()
        self.tables_list.setColumnCount(2)
        self.tables_list.setHorizontalHeaderLabels(["Select", "Table Name"])
        self.tables_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tables_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tables_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.layout.addWidget(self.tables_list)

        self.load_tables()

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all)
        self.layout.addWidget(self.select_all_button)

        self.unselect_all_button = QPushButton("Unselect All")
        self.unselect_all_button.clicked.connect(self.unselect_all)
        self.layout.addWidget(self.unselect_all_button)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_tables)
        self.layout.addWidget(self.search_button)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(10)
        self.results_table.setHorizontalHeaderLabels(["Name", "Phone", "Email", "WhatsApp", "Signal", "Telegram", "Relationship", "Notes", "Last Modified", "Source Table"])
        self.results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set resize mode for each column
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Name
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Phone
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Email
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # WhatsApp
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Signal
        self.results_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Telegram
        self.results_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Relationship
        self.results_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)           # Notes
        self.results_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Last Modified
        self.results_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Source Table

        self.results_table.setWordWrap(True)
        self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.layout.addWidget(self.results_table)




    def load_tables(self):
        self.tables_list.setRowCount(0)
        tables = db_ops.fetch_all_tables(self.conn)
        for table in tables:
            row_position = self.tables_list.rowCount()
            self.tables_list.insertRow(row_position)

            checkbox = QCheckBox()
            self.tables_list.setCellWidget(row_position, 0, checkbox)
            self.tables_list.setItem(row_position, 1, QTableWidgetItem(table[1]))

    def select_all(self):
        for row in range(self.tables_list.rowCount()):
            checkbox = self.tables_list.cellWidget(row, 0)
            checkbox.setChecked(True)

    def unselect_all(self):
        for row in range(self.tables_list.rowCount()):
            checkbox = self.tables_list.cellWidget(row, 0)
            checkbox.setChecked(False)

    def search_tables(self):
        search_term = self.search_input.text().strip()
        selected_tables = []
        for row in range(self.tables_list.rowCount()):
            checkbox = self.tables_list.cellWidget(row, 0)
            if checkbox.isChecked():
                table_name = self.tables_list.item(row, 1).text()
                selected_tables.append(table_name)

        search_results = db_ops.search_tables(self.conn, search_term, selected_tables)
        self.display_search_results(search_results)

    def display_search_results(self, search_results):
        self.results_table.setRowCount(0)
        for entry in search_results:
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            # Skip the serial ID (entry[0]) and align data with headers
            self.results_table.setItem(row_position, 0, QTableWidgetItem(str(entry[1])))  # Name
            self.results_table.setItem(row_position, 1, QTableWidgetItem(str(entry[2])))  # Phone
            self.results_table.setItem(row_position, 2, QTableWidgetItem(str(entry[3])))  # Email
            self.results_table.setItem(row_position, 3, QTableWidgetItem(str(entry[4])))  # WhatsApp
            self.results_table.setItem(row_position, 4, QTableWidgetItem(str(entry[5])))  # Signal
            self.results_table.setItem(row_position, 5, QTableWidgetItem(str(entry[6])))  # Telegram
            self.results_table.setItem(row_position, 6, QTableWidgetItem(str(entry[7])))  # Relationship
            self.results_table.setItem(row_position, 7, QTableWidgetItem(str(entry[8])))  # Notes
            self.results_table.setItem(row_position, 8, QTableWidgetItem(str(entry[10]))) # Last Modified
            self.results_table.setItem(row_position, 9, QTableWidgetItem(str(entry[11]))) # Source Table




if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


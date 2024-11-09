import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 QTableWidget with Buttons Example")
        self.setGeometry(100, 100, 600, 400)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout
        layout = QVBoxLayout()

        # Create a QTableWidget
        table_widget = QTableWidget(4, 3)  # 4 rows and 3 columns
        for row in range(4):
            for col in range(3):
                button = QPushButton(f"Button {row},{col}")
                button.clicked.connect(lambda _, r=row, c=col: self.button_clicked(r, c))
                table_widget.setCellWidget(row, col, button)

            # Add the table widget to the layout
        layout.addWidget(table_widget)

        # Set the layout to the central widget
        central_widget.setLayout(layout)


def button_clicked(self, row, col):
    print(f"Button at row {row}, column {col} clicked")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
        # Add buttons to each cell
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QVBoxLayout, QCheckBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QGridLayout, QRadioButton
from PyQt5.QtWidgets import QFileDialog, QWidget, QPushButton, QTableView,QFrame, QMessageBox, QDialog
from PyQt5.QtWidgets import QButtonGroup, QTextEdit, QGroupBox, QSizePolicy

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem,QTableWidget,QTableWidgetItem
from PyQt5.Qt import QStandardItem, Qt, QImage, QPixmap,QStandardItemModel,QTextOption
from PyQt5.QtGui import QFont, QColor, QIcon

from IEC_load import Test_JLPT, LoadExcel
from MiseEnFormeData import TransformInPutData

class StandardItem(QStandardItem):

    def __init__(self, txt='', font_size=18, set_bold=True, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)  # Permet l'édition de la cellule.
        self.setForeground(color)  # test 5
        self.setFont(fnt)
        self.setText(txt)
        self.layoutMainView = None
        self.Formatdata

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create a QGridLayout
        self.gridLayout = QGridLayout()

        # Create 10 rows of QGroupBox with 4 buttons each
        self.buttonGroups = []
        for row in range(10):
            groupBox = QGroupBox('')
            groupBox = QGroupBox(f'Group Box {row + 1}')
            groupBoxLayout = QHBoxLayout()

            buttonGroup = QButtonGroup()
            self.buttonGroups.append(buttonGroup)

            for i in range(1,7):
                button = QRadioButton(f'Button {i + 1}')
                buttonGroup.addButton(button, i)
                groupBoxLayout.addWidget(button)

                groupBox.setLayout(groupBoxLayout)
                self.gridLayout.addWidget(groupBox, row, 0)

        # Add a button to read the state of the buttons
        self.readButton = QPushButton('Read Button States')
        self.readButton.clicked.connect(self.readButtonStates)
        self.gridLayout.addWidget(self.readButton, 10, 0)

        # Set the layout to the main widget
        self.setLayout(self.gridLayout)

        self.setWindowTitle('PyQt5 GroupBox with Buttons Example')
        self.setGeometry(300, 300, 400, 600)
        self.show()

    def readButtonStates(self):
        for row, buttonGroup in enumerate(self.buttonGroups):
            for button in buttonGroup.buttons():
                if button.isChecked():
                    print(f'Group Box {row + 1}, Button {buttonGroup.id(button) + 1} is checked')

if __name__ == '__main__':
    with LoadExcel("JLPT_3_ESSAI_2003.xls", True, False) as (JLPT_TestSet):
        print("Chargement SCL ok")  # str(self.T_LoadSCL))

    Test = Test_JLPT(JLPT_TestSet)
    JLPT_DATA = Test.TestPart()
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())


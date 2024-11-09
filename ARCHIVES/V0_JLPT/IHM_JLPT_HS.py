#
# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
#
# This file is part of [R#SPACE], [IEC61850 Digital Control System testing.
#
# IMPORT EXTERNES
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


## \b StandardItem:  met en forme une chaine de caractère (texte, taille, gras, couleur).
#
#
class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=20, set_bold=True, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)  # Permet l'édition de la cellule.
        self.setForeground(color)  # test 5
        self.setFont(fnt)
        self.setText(txt)
        self.layoutMainView = None
        self.Formatdata
## \b ButtonText:  créer un bouton et met en forme le texte taille, gras, couleur ).
#
#
class ButtonText(QPushButton):
    def __init__(self, txt='', font_size=11, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setFont(fnt)
        self.setText(txt)
        self.setFixedHeight(font_size * 5)
        self.layoutMainView = None

## \b MainWindow:  Fenêtre principale de l'application
#
#
class MainWindow(QMainWindow):
    def __init__(self,  _DataJLPT, parent=None):
        QMainWindow.__init__(self, parent)

    ## \b AppDemo:  Application dans la fenêtre
    #
    #
    class AppDemo(QWidget):

        def __init__(self, _DataJLPT):
            super().__init__()
            self.setWindowTitle('JLPT TEST')
            self.setMinimumSize(1200,  800)  # Largeur minimale: 600, Hauteur minimale: 400
            self.setMaximumSize(1400,  800)
            self.DataJLPT = _DataJLPT
            self.TranformData = TransformInPutData()

            self.line = 0
            self.dataKey = ''

            qr = self.frameGeometry()  # geometry of the main window
            cp = QDesktopWidget().availableGeometry().center()  # center point of screen
            qr.moveCenter(cp)  # move rectangle's center point to screen's center point
            self.move(qr.topLeft())  # move to top left eft of window centering it

            self.winLayout = QVBoxLayout()  # Most the HMI is vertical
            self.winLayout.setSpacing(10)

            self.winLayout.addLayout(self.LoadingButtons())  # Top application button (TEMPLATE, SELECT FILE)


            self.tableView = QTableWidget()
            self.tableView.setColumnCount(7)
            self.model = QStandardItemModel(4, 8)
            self.tableView.setHorizontalHeaderLabels(('Topic', 'Kanji','Choix 1', 'Choix 2', 'Choix 3', 'Choix 4', 'Choix 5', 'Choix 5', 'Choix6'))
            Answer_size = 150
            Kanji_size  = 50
            self.tableView.setColumnWidth(0, 400)
            self.tableView.setColumnWidth(1, Kanji_size)
            self.tableView.setColumnWidth(2, Answer_size)
            self.tableView.setColumnWidth(3, Answer_size)
            self.tableView.setColumnWidth(4, Answer_size)
            self.tableView.setColumnWidth(5, Answer_size)
            self.tableView.setColumnWidth(6, Answer_size)
            self.tableView.setColumnWidth(7, Answer_size)
 #           self.tableView.setColumnWidth(8, Answer_size)
            self.tableView.setRowCount(40)
            self.winLayout.addWidget(self.tableView)
            self.GroupeButton = []
            self.PresentationDesTest(_DataJLPT)


        def PresentationDesTest(self, _DataJLPT):
            Ligne = 0
            I     =  0
            for data in JLPT_DATA:

                for Question in _DataJLPT:
                    print('Question:' + Question.reponse)
                    #                    ReponsePossible = reponse.split(' ')
                    Lst = []
                    Reponse = []
                    for subQuest in Question.subQuestion:

                        if self.TranformData.is_number(subQuest):
                            continue
                        X = subQuest.split('．') # espace Unicode
                        X.append('')
                        Kanji = X[1][0]

                        Choix = TransformInPutData.Transform0(subQuest,Kanji)  # Présenter les données pour l'IHM
                        NbProposition = len(Choix)
                        Reponse.append (Choix)
                        I= I +1
                self.affiche_test(Ligne, Question.reponse, Kanji, Reponse)
                Ligne = Ligne + 1
                NbQuestion = len(Question.subQuestion)

        def affiche_test(self, Ligne, Topic, Kanji, Reponse) :

            self.setLayout(self.winLayout)
            self.show()
            self.tableView.setSpan(Ligne, 0, 5, 1)

            _Kanji       = QTextEdit(Kanji)
            _Topic       =  QTextEdit(Topic)   ## _Topic
            buttonLayout = QVBoxLayout()
#            Topic           = phrase

            self.setStyleSheet("""
                        QTextEdit {
                            background-color: #f0f0f0;
                            border: 1px solid #ccc;
                            padding: 2px;
                            font-size: 16px;
                            font-family: Arial;
                            font-weight: bold
                        }
 
                        QRadioButton {
                            background-color: #f0f0f0;
                            border: 1px solid #ccc;
                            padding: 6px;
                            font-family: Arial;
                            font-size: 16px;
                            font-weight: bold
                        }
                    """)
#_Kanji.setWordWrapMode(QTextOption.WordWrap)  # Activer le word wrap pour le QTextEdit

            # Définir la mise en page
            phrase = QTextEdit(str(Reponse))
            font = QFont()
            font.setFamily("Arial")
            font.setPointSize(16)
            font.setBold(True)
            Kanji0 = QTextEdit(str(Kanji))
            Kanji0.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            Kanji0.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            Kanji0.setFont(font)

            NbReponse= len(Reponse)

            STR = []
            for i in [0..NbReponse]:
                STR.append(STR[i])


            try:
               str4 = str(Reponse[3])[2:-2]
            except Exception as e:
                # Code to run if no exceptions were raised
                str4=''
                print(f"The result of the division is {e}")
            finally:
                # Code to run regardless of whether an exception was raised or not
                print("Processing complete.")

#            str5 = str(Reponse[4])[2:-2]
#            Reponse1 = QRadioButton(str(Choix[0])[2:-2])        # Supprime '[' et ']'
            Reponse1 = QRadioButton(str1)
            Reponse2 = QRadioButton(str2)
            Reponse3 = QRadioButton(str3)
            Reponse4 = QRadioButton(str4)
#            Reponse5 = QRadioButton(str5)

            buttonGroup = QButtonGroup()
            buttonGroup.addButton(Reponse1)
            buttonGroup.addButton(Reponse2)
            buttonGroup.addButton(Reponse3)
 #           buttonGroup.addButton(Reponse4)
#            buttonGroup.addButton(Reponse5)

            self.GroupeButton.append(buttonGroup)
            buttonLayout.addWidget(phrase)
            buttonLayout.addWidget(Kanji0)
            buttonLayout.addWidget(Reponse1)
            buttonLayout.addWidget(Reponse2)
            buttonLayout.addWidget(Reponse3)
#            buttonLayout.addWidget(Reponse4)
#            buttonLayout.addWidget(Reponse5)

            # Column count
            #            self.tableView.setCellWidget(Ligne, 0, phrase)
            self.tableView.setCellWidget(Ligne, 0, phrase)
            self.tableView.setCellWidget(Ligne, 1, Kanji0)
            self.tableView.setCellWidget(Ligne, 2, Reponse1)
            self.tableView.setCellWidget(Ligne, 3, Reponse2)
            self.tableView.setCellWidget(Ligne, 4, Reponse3)
#            self.tableView.setCellWidget(Ligne, 5, Reponse4)

            self.setLayout(self.winLayout)
            self.show()

        ## Chargement SCL, Campagne, Lancement Test
        def LoadingButtons(self) -> QHBoxLayout:
            ## Layout for the set of action buttons
            hLayout = QHBoxLayout()
            hLayout.setAlignment(Qt.AlignLeft)

            # Bouton Création de campagne ==> chargement d'une SCL
            Part1 = ButtonText("     問題Ⅰ    \n ＿＿＿のことばはどうよみますか。") #\n １２３４からいちばんいいものをひとつ からいちばんいいものをひとつ えらびなさい。")
            Part1.setToolTip("１２３４からいちばんいいものをひとつ からいちばんいいものをひとつ えらびなさい。")

            Part1.clicked.connect(self.TestPart1)
            hLayout.addWidget(Part1)

            # Bouton chargement d'une campagne de test (créer initialement via "Création campagne')
            Part2 = ButtonText("      問題Ⅱ    \n＿＿＿のことばはどうかきますか。")
            Part2.setToolTip("\n１２３４からいちばんいいものをひと からいちばんいいものをひと つえらびなさい。")
            Part2.clicked.connect(self.TestPart2)
            hLayout.addWidget(Part2)

            #  Bouton de lancement des tests sur la base de la campagne affichée.
            Part3 = ButtonText("      問題Ⅲ  \n______のところになにをいれますか。")
            Part3.setToolTip("１２３４からいちばんいいものをひ からいちばんいいものをひ とつえらびなさい")
            Part3.clicked.connect(self.TestPart3)
            hLayout.addWidget(Part3)

            ## Add horizontal layout of buttons to the grid layout.
            return hLayout
        def TestPart1(self):
            print('Accès partie1')

        def TestPart2(self):
            print('Accès partie2')

        def TestPart3(self):
            print('Accès partie3')





if __name__ == '__main__':
    with LoadExcel("JLPT_3_ESSAI_2003.xls", True, False) as (JLPT_TestSet):
        print("Chargement SCL ok")  # str(self.T_LoadSCL))

    Test = Test_JLPT(JLPT_TestSet)
    JLPT_DATA = Test.TestPart()

    print('xxxxxxxx')
    app = QApplication(sys.argv)
    Win = MainWindow(app)
    demo = Win.AppDemo(JLPT_DATA)
    demo.show()
    sys.exit(app.exec_())





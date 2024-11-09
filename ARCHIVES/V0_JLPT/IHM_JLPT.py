#
# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
#
# This file is part of [R#SPACE], [IEC61850 Digital Control System testing.
#
# IMPORT EXTERNES
import sys, os
import time
import xml.etree.ElementTree as ET
import logging


from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QVBoxLayout, QCheckBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QGridLayout, QRadioButton
from PyQt5.QtWidgets import QFileDialog, QWidget, QPushButton, QFrame, QMessageBox, QDialog
from PyQt5.QtWidgets import QButtonGroup
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem,QTableWidget,QTableWidgetItem
from PyQt5.Qt import QStandardItem, Qt, QImage, QPixmap,QStandardItemModel
from PyQt5.QtGui import QFont, QColor, QIcon

from IEC_load import Test_JLPT, LoadExcel

from MiseEnFormeData import TransformInPutData


## \b StandardItem:  met en forme une chaine de caractère (texte, taille, gras, couleur).
#
#
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
            self.DataJLPT = _DataJLPT
            self.TranformData = TransformInPutData('')
            for Question in _DataJLPT:
#                print('Question:' + Question.)
                for subQuestion in Question.subQuestion:
                    print('subQuestion:' + str(subQuestion))

#            RteIcon = QImage('images/rteLogo.png')
#            self.setWindowIcon(QIcon(QPixmap.fromImage(RteIcon)))

            self.line = 0
            self.dataKey = ''

            self.fCampaign = ''

            self.StationName = None  # Nom du poste dans le SCL
            self.Voltage = ''  # Sera mis à jour lors d'un chargement SCL

            self.Name = None  # Nome du poste de la campagne chargée
            self.initial = True

            qr = self.frameGeometry()  # geometry of the main window
            cp = QDesktopWidget().availableGeometry().center()  # center point of screen
            qr.moveCenter(cp)  # move rectangle's center point to screen's center point
            self.move(qr.topLeft())  # move to top left eft of window centering it

            self.winLayout = QVBoxLayout()  # Most the HMI is vertical
            self.winLayout.setSpacing(10)

            self.winLayout.addLayout(self.LoadingButtons())  # Top application button (TEMPLATE, SELECT FILE)

            self.descLayout, self.descBox = self.DescriptionBox()
            self.winLayout.addLayout(self.descLayout)

            self.tableView = QTableWidget()
            self.tableView.setColumnCount(6)
            self.tableView.setHorizontalHeaderLabels(('Topic', 'Choix 1', 'Choix 2', 'Choix 3', 'Choix 4s', 'Result'))
            Answer_size = 80

            self.tableView.setColumnWidth(0, 250)
            self.tableView.setColumnWidth(1, Answer_size)
            self.tableView.setColumnWidth(2, Answer_size)
            self.tableView.setColumnWidth(3, Answer_size)
            self.tableView.setColumnWidth(4, Answer_size)
            self.tableView.setColumnWidth(5, Answer_size)
            self.tableView.setColumnWidth(6, Answer_size)
            self.tableView.setRowCount(4)
            self.winLayout.addWidget(self.tableView)

            self.PresentationDesTest(_DataJLPT)
#           for data in JLPT_DATA:
#                for Question in _DataJLPT:
#                    print('Question:' + Question.answer)
#                    print('Question:' + Question.question)
#                    print('Question:' + Question.hint)
#                    print('Question:' + Question.reponse)
#                    reponse = Question.reponse
#
#
#            self.lstButton = []
#            X1 = self.affiche_test(1, self.lstButton, " １．しゃ", "２．くるま", "３．ちゃ", "４．くろま")
#            X2 = self.affiche_test(2, self.lstButton, "１．しゃxx", "２．くるま", "３．ちゃ", "４．くろま")
#            X3 = self.affiche_test(3, self.lstButton, "１．しゃyy", "２．くるま", "３．ちゃ", "４．くろま")
#            TestSet = [X2, X2, X3]
#*/
        def PresentationDesTest(self, _DataJLPT):

            for data in JLPT_DATA:
                for Question in _DataJLPT:
                    print('Question:' + Question.answer)
                    print('Question:' + Question.question)
                    print('Question:' + Question.hint)
                    print('Question:' + Question.reponse)
                    reponse = Question.reponse

                    #                    ReponsePossible = reponse.split(' ')
                    Lst = []
                    for subQuest in Question.subQuestion:
                        if self.TranformData.is_number(subQuest):
                            continue
                        Choix = self.TranformData.Transform(subQuest)  # Présenter les données pour l'IHM

                        self.affiche_test(Choix[0], Choix[1], Choix[2], Choix[2],Choix[4])


                    NbQuestion = len(Question.subQuestion)

        def affiche_test(self, ligne, Choix1, Choix2, Choix3, Choix4):
            buttonLayout = QHBoxLayout()
            Reponse1 = QRadioButton(Choix1)
            Reponse2 = QRadioButton(Choix2)
            Reponse3 = QRadioButton(Choix3)
            Reponse4 = QRadioButton(Choix4)

            buttonGroup = QButtonGroup()
            buttonGroup.addButton(Reponse1)
            buttonGroup.addButton(Reponse2)
            buttonGroup.addButton(Reponse3)
            buttonGroup.addButton(Reponse4)
            buttonLayout.addWidget(Reponse1)
            buttonLayout.addWidget(Reponse2)
            buttonLayout.addWidget(Reponse3)
            buttonLayout.addWidget(Reponse4)
            # Row count
            # Column count
            self.tableView.setCellWidget(ligne, 1, Reponse1)
            self.tableView.setCellWidget(ligne, 2, Reponse2)
            self.tableView.setCellWidget(ligne, 3, Reponse3)
            self.tableView.setCellWidget(ligne, 4, Reponse4)
#            self.winLayout.addLayout(self.containerLayout)
#            １．しゃ ２．くるま ３．ちゃ ４．くろま
            self.setLayout(self.winLayout)
            self.show()
#            lstButton.append(buttonGroup)
#            return lstButton

        ## Chargement SCL, Campagne, Lancement Test
        def LoadingButtons(self) -> QHBoxLayout:
            ## Layout for the set of action buttons
            hLayout = QHBoxLayout()
            hLayout.setAlignment(Qt.AlignLeft)

            # Ajout du logo Rte.
            RteTitle = QLabel(self)
            RteIcon = QPixmap('images/rteLogo.png')
            scale1 = RteIcon.scaled(60, 60, Qt.KeepAspectRatio)
            RteTitle.setPixmap(scale1)
            hLayout.addWidget(RteTitle)

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

        # Boit de dialogue pour décrire l'objet de la campagne, ces caractéristiques.
        def DescriptionBox(self) -> (QHBoxLayout, QLineEdit):
            hLayout = QHBoxLayout()
            textbox = QLineEdit(self)
            textbox.move(20, 20)
            textbox.resize(280, 40)
            textbox.setPlaceholderText('Décrire la campagne de test, tranche / IED')
            textbox.setClearButtonEnabled(True)
            textbox.setFixedHeight(80)
            hLayout.addWidget(textbox)
            return hLayout, textbox

        # Mise en place des boutons du bas de la fenêtre 'enregistrer campagne', 'genration template':
        # Ultérieurement il faut prévoir:
        #   * l'enregistrement des résultats
        #   * la gestion éventuelle de 'branche' pour chaque poste'.
        #   * la création des anomalies, pour les tests échouées...
        def BottomButtons(self): # -> QHBoxLayout, QFrame:

            return




        def DialogueTestStep(self):
            logging.info("DialogueTestStep")
            self.dialog = QDialog()
            self.dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

            self.dialog.setWindowTitle('Ajout / Suppression de step')
            layoutDialogue = QVBoxLayout()

            #        app.setApplicationDisplayName("Saisie d'une étape de test")
            label1 = QLabel("Nom de l'étape de test: ")
            label1.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            label1.setFont(QFont('Arial', 10))

            label2 = QLabel("A Tester              : ")
            label2.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            label2.setFont(QFont('Arial', 10))

            label3 = QLabel("Description du test   : ")
            label3.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            label3.setFont(QFont('Arial', 10))

            self.NomTest = QLineEdit('nom du test')
            self.Atester = QLineEdit('True/False')
            self.Description = QLineEdit("décrire l'objectif du test")

            self.Confirmation = QPushButton()
            self.Confirmation.setText(" Confirmation ")
            self.Confirmation.clicked.connect(self.Confirm)

            self.Annulation = QPushButton()
            self.Annulation.setText(" Annulation ")
            self.Annulation.clicked.connect(self.Abort)

            dialLayout = QGridLayout()
            dialLayout.addWidget(label1, 0, 0)
            dialLayout.addWidget(label2, 1, 0)
            dialLayout.addWidget(label3, 2, 0)
            dialLayout.addWidget(self.NomTest, 0, 1)

            hRadioLayout = QHBoxLayout()

            dualRadioButtons = QWidget()
            self.ActiveTest = QRadioButton(" Actif ")
            hRadioLayout.addWidget(self.ActiveTest)

            self.InactiveTest = QRadioButton(" Ignore ")
            hRadioLayout.addWidget(self.InactiveTest)

            dualRadioButtons.setLayout(hRadioLayout)
            dialLayout.addWidget(dualRadioButtons, 1, 1)

            dialLayout.addWidget(self.Description, 2, 1)
            dialLayout.addWidget(QLabel(), 3, 0)

            dialLayout.addWidget(self.Confirmation, 4, 0)
            dialLayout.addWidget(self.Annulation, 4, 1)

            dialLayout.setRowStretch(4, 1)
            dialLayout.setColumnMinimumWidth(1, 200)
            layoutDialogue.addLayout(dialLayout)
            layoutDialogue.activate()
            self.dialog.setLayout(layoutDialogue)
            self.dialog.exec()
            #            self.dialog.show()
            return (self.Nom, self.Active, self.Description)

            #        sys.exit(app.exec_())

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


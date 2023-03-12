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
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.Qt import QStandardItem, Qt, QImage, QPixmap
from PyQt5.QtGui import QFont, QColor, QIcon

from IEC_load import Test_JLPT, LoadExcel

IED_LD, TYPE, VALUE, DESC, DESC2 = range(5)

# TODO : faire une classe pour l'accès au fichier SCL (nom du poste, répertoire, nom du SCL...
# TODO : faire une classe pour le fichier XML de campagne de test (nom de la campagne, répertoire, nom du XML...)


# Test case pas défauts
DefaultSteps = [['PreCondition', 'Vérifications préalables'],
                ['Présence LN et DO', 'Analyse des LN présents'],
                ['TestNominal', 'Test fonctionnel nominal'],
                ['TestPerformance', 'Vérification des temps critiques'],
                ['ProductionRapport', 'Création rapport du test']]


## \b SCL_FileName:  classe pour définir l'accès au SCL.
#
class SCL_FileName:
    def __init__(self, _FileName: str, _repertoire: str, ):  # repertoire relatif à Lot9/Lot9_outils
        self.SCL_FileName = _FileName
        self.SCL_repertoire = _repertoire


## \b CampagneFileName:  classe pour définir l'accès au fichier XML  qui décrit la campagne.
#
class CampagneFileName:

    def __init__(self, _FileName: str, _repertoire: str, ):
        self.CampagneFileName = _FileName
        self.CampagneRepertoire = _repertoire




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

        self.DataJLPT= _DataJLPT

    ## \b AppDemo:  Application dans la fenêtre
    #
    #
    class AppDemo(QWidget):

        def __init__(self, _TestMode: bool = False):
            super().__init__()
            self.setWindowTitle('JLPT TEST')

#            RteIcon = QImage('images/rteLogo.png')
#            self.setWindowIcon(QIcon(QPixmap.fromImage(RteIcon)))

            self.line = 0
            self.dataKey = ''
            self.TestMode = _TestMode

            self.fCampaign = ''

            self.StationName = None  # Nom du poste dans le SCL
            self.Voltage = ''  # Sera mis à jour lors d'un chargement SCL

            self.Name = None  # Nome du poste de la campagne chargée
            self.initial = True
            self.SCL_charge = False
            self.Poste = []             # Container de l'arborescence des widget Station/Bay/IED../test step
            self.tStation = []
            self.tGraphicalBay = []
            self.SCL_loaded = ''

            qr = self.frameGeometry()  # geometry of the main window
            cp = QDesktopWidget().availableGeometry().center()  # center point of screen
            qr.moveCenter(cp)  # move rectangle's center point to screen's center point
            self.move(qr.topLeft())  # move to top left eft of window centering it

            self.winLayout = QVBoxLayout()  # Most the HMI is vertical
            self.winLayout.setSpacing(10)

            self.winLayout.addLayout(self.LoadingButtons())  # Top application button (TEMPLATE, SELECT FILE)

            with LoadExcel("JLPT_3_ESSAI_2003.xls", True, False) as (JLPT_TestSet):  # , self.T_LoadSCL):
                print("Chargement SCL ok")  # str(self.T_LoadSCL))

            self.descLayout, self.descBox = self.DescriptionBox()
            self.winLayout.addLayout(self.descLayout)

#            self.containerLayout = QHBoxLayout()  # Container for 2 vertical layout
#            self.containerLayout.addLayout(self.ButtonSection)  # Set of buttons on the LEFT
#            self.containerLayout.addWidget(self.frameBottom)  # Set the frame
#            self.setLayout(self.winLayout)

            self.treeView = QTreeWidget()
            # self.treeView.setHeaderLabels(['    Bay       IED    LD    Steps ', 'Simu', 'Description', 'IP/ldName'])
            self.treeView.headerItem().setText(0, "Question")
            self.treeView.headerItem().setText(1, "-- A -- ")
            self.treeView.headerItem().setText(2, "-- B -- ")
            self.treeView.headerItem().setText(3, "-- C -- ")
            self.treeView.headerItem().setText(4, "-- D -- ")
            self.treeView.headerItem().setText(5, " Choice ")
            self.treeView.headerItem().setText(6, " Result ")

            Answer_size = 80
            
            self.treeView.setColumnWidth(0, 250)
            self.treeView.setColumnWidth(1, Answer_size)
            self.treeView.setColumnWidth(2, Answer_size)
            self.treeView.setColumnWidth(3, Answer_size)
            self.treeView.setColumnWidth(4, Answer_size)
            self.treeView.setColumnWidth(5, Answer_size)
            self.treeView.setColumnWidth(6, Answer_size)
            self.winLayout.addWidget(self.treeView)

#            self.winLayout.addLayout(self.containerLayout)
            self.setLayout(self.winLayout)
            self.show()


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


       # détermine le chemein dans l'arbre Tranche/IED/LD/Steps pour faire les modifications.
        def getPath(self, indexes):

            if indexes is None or len(indexes) == 0:
                return
            index = indexes[0]

            path = ''
            while index.parent().isValid():
                item = index.data()
                _item = item.split(',')
                IECitem = _item[0]
                path = IECitem + '.' + path
                index = index.parent()

            path = index.data() + '.' + path  # Ins
            return path

        # \b EnregistrerCampagne:  Génère le fichier XML correspondant à l'affichage et la sélection courrantte
        #
        # Le principe est de lire les valeurs portées par l'IHM
        def EnregistrerCampagne(self, Mode: bool):
            logging.info('EnregistrerCampagne Button')



        def LanceCampagne(self):
            logging.info('Sauvegarde et lancer la campagne')

        # \b addStation:  Ajoute le niveau SubStation dans l'arborescence de la campagne.
        #
        # @param poste: Objet graphique du plus haut niveau de l'arbre
        # @param posteName: Nom du poste dans la balise du XML de campagne
        # @param Voltage:  Niveau de tension du poste

        def addStation(self, poste: QTreeWidgetItem, posteName: str, Voltage: str):
            Station = QTreeWidgetItem(poste)
            Station.setText(0, posteName + ' (' + Voltage + ')')
            return Station

        # \b addStation:  Ajoute une tranche à la sous-station dans l'arborescence de la campagne.
        #
        # @param Station: Objet graphique qui décrit la sous-station (héritage arborescent)
        # @param bayName: Nom de la tranche (issu du SCL)
        # @param bayTest:  Booléen pour activer ou désactiver le test de la tranche (héritage en cascade)
        def addBay(self, Station: QTreeWidgetItem, bayName: str, bayTest: str):
            Bay = QTreeWidgetItem(Station)
            Bay.setText(0, bayName)
            Bay.setFlags(Bay.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            if bayTest == 'True':
                Bay.setCheckState(0, Qt.Checked)
            else:
                Bay.setCheckState(0, Qt.Unchecked)

            self.tGraphicalBay.append(Bay)
            setattr(Bay, 'tIED', [])
            return Bay

        # \b addIED:  Ajoute un IED à la tranche dans l'arborescence de la campagne.
        #
        # @param Bay: Objet graphique qui décrit la tranche (héritage arborescent)
        # @param iedName: Nom de l'IED (issu du SCL)
        # @param simulated:  Booléen pour activer ou désactiver la simulation de l'IED

        def addIED(self, Bay: QTreeWidgetItem, iedName: str, simulated: str):
            IP_Adresse, AP_Name = self.sclMgr.get_IP_Adr(iedName)

            IED = QTreeWidgetItem(Bay)
            IED.setText(0, iedName)
            IED.setFlags(Bay.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)

            hLayout = QHBoxLayout()
            button = QCheckBox("Simulé")
            hLayout.addWidget(button)
            SimuButton = QWidget()
            SimuButton.setLayout(hLayout)
            self.treeView.setItemWidget(IED, 1, SimuButton)

            setattr(IED, 'Simu', button)
            IED.setText(2, "")
            IED.setText(3, IP_Adresse)

            setattr(IED, 'tLD', [])
            return IED

        # \b addLD:  Ajoute un LD à l'IED dans l'arborescence de la campagne.
        #
        # @param Bay: Objet graphique qui décrit la tranche (héritage arborescent)
        # @param inst: Nom du LD (issu du SCL, pour le LD c'est l'attribut 'inst' qui donne le nom...)
        # @param desc: Description du LD, issu du SCL
        # @param test:  Booléen pour activer ou désactiver le test du LD
        def addLD(self, IED: QTreeWidgetItem, inst: str, desc: str, test: str = 'True'):
            LD = QTreeWidgetItem(IED)
            LD.setFlags(IED.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            if test == 'True':
                LD.setCheckState(0, Qt.Checked)  #
            else:
                LD.setCheckState(0, Qt.Unchecked)  #

            LD.setText(0, inst)
            LD.setText(1, '')
            LD.setText(2, desc)
            IED.tLD.append(LD)
            return LD

        # \b addStep:  Ajoute un Step de test au LD dans l'arborescence de la campagne.
        #
        # @param LD: Objet graphique qui décrit le Logical Device (héritage arborescent)
        # @param numStep: indice du Step de 1  à totalStep
        # @param totalStep: nombre total de pas de test.
        # @param toTest:  Booléen pour activer ou désactiver le test.


        def addStep(self, LD: QTreeWidgetItem, numStep: int, totalStep: int, toTest: bool, stepName: str, stepDesc: str):
            Step = QTreeWidgetItem(LD)

            Step.setFlags(LD.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            if toTest is True:
                Step.setCheckState(0, Qt.Checked)  #
            else:
                Step.setCheckState(0, Qt.Unchecked)  #
            Step.setText(0, stepName)
            Step.setText(1, '')
            Step.setText(2, stepDesc)
            self.dualPushButtons = QWidget()
            # LAYOUT DES BOUTONS
            self.hLayout = QHBoxLayout()
            self.addButton = QPushButton(" + ")
            self.addButton.clicked.connect(self.ajouteStep)
            self.hLayout.addWidget(self.addButton)

            if numStep > 0 and numStep < (totalStep - 1):
                self.removeButton = QPushButton(" - ")
                self.removeButton.clicked.connect(self.retireStep)
                self.hLayout.addWidget(self.removeButton)

            self.dualPushButtons.setLayout(self.hLayout)
            #                            self.dualPushButtons.
            self.treeView.setItemWidget(Step, 1, self.dualPushButtons)

        ## \b CreationCampagne:  Affiche graphique du SCL limité à POSTE / Tranche /IED / LD/ Steps.
        #                        permet la sélection des objets à tester et l'enregistrement d'une campange "instanciée".
        #                        Les IED ne sont pas chargés en mémoire pour éviter des temps de traitement importants.
        #
        #
        def CreationCampagne(self, initial=True):



            self.treeView.clear()



            logging.info('Fin Chargement graphique.')
            self.treeView.expandAll()
            self.treeView.show()

        ## \b DialogueTestStep:  Affiche le dialogue pour ajouter un pas de test.
        #

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
    Test.TestPart()


    print('xxxxxxxx')
    app = QApplication(sys.argv)
    Win = MainWindow(JLPT_TestSet)
    demo = Win.AppDemo(False)
    demo.show()
    sys.exit(app.exec_())

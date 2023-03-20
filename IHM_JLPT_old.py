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

from IEC_load import Test_JLPT, LoadExcel

from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QVBoxLayout, QCheckBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QGridLayout, QRadioButton
from PyQt5.QtWidgets import QFileDialog, QWidget, QPushButton, QFrame, QMessageBox, QDialog
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.Qt import QStandardItem, Qt, QImage, QPixmap
from PyQt5.QtGui import QFont, QColor, QIcon



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


## \b LoadCampagne:  chargement du fichier XML qui décrit une campagne de test.
# cette classe s'utilise avec le mot clef 'with'.
#
# @param fname  : nom du fichier précédé d'un chemin relatif (../../CampagneDeTest/CampagneExemple.xml

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
            self.setWindowTitle('CREATION / EDITION CAMPAGNE DE TEST')

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

            self.descLayout, self.descBox = self.DescriptionBox()
            self.winLayout.addLayout(self.descLayout)

            self.ButtonSection, self.frameBottom = self.BottomButtons()

            self.containerLayout = QHBoxLayout()  # Container for 2 vertical layout
            self.containerLayout.addLayout(self.ButtonSection)  # Set of buttons on the LEFT
            self.containerLayout.addWidget(self.frameBottom)  # Set the frame
            self.setLayout(self.winLayout)

            self.treeView = QTreeWidget()
            # self.treeView.setHeaderLabels(['    Bay       IED    LD    Steps ', 'Simu', 'Description', 'IP/ldName'])
            self.treeView.headerItem().setText(0, "Station / Bay / IED / LD / Test")
            self.treeView.headerItem().setText(1, "Simulé")
            self.treeView.headerItem().setText(2, "Description")
            self.treeView.headerItem().setText(3, "IP")

            self.treeView.setColumnWidth(0, 250)
            self.treeView.setColumnWidth(1, 100)
            self.treeView.setColumnWidth(2, 100)
            self.treeView.setColumnWidth(3, 50)
            self.winLayout.addWidget(self.treeView)

            self.winLayout.addLayout(self.containerLayout)
            self.setLayout(self.winLayout)
            self.show()
            if _TestMode:
                self.CreationCampagne(True)

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
            ChargerSCL = ButtonText(" Création campagne\n Chargement SCL ")
            ChargerSCL.clicked.connect(self.CreationInitiale)
            hLayout.addWidget(ChargerSCL)

            # Bouton chargement d'une campagne de test (créer initialement via "Création campagne')
            ChargeCampagne = ButtonText(" Chargement / Modification\n de campagne ")
            ChargeCampagne.clicked.connect(self.ChargerCampagne)
            hLayout.addWidget(ChargeCampagne)

            #  Bouton de lancement des tests sur la base de la campagne affichée.
            LanceCampagne = ButtonText(" Lancer une campagne de test ")
            LanceCampagne.clicked.connect(self.LanceCampagne)
            hLayout.addWidget(LanceCampagne)

            ## Add horizontal layout of buttons to the grid layout.
            return hLayout

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

            Left_frame = QFrame(self)
            Left_frame.setLineWidth(4)
            Left_frame.setStyleSheet("background-color: rgb(200, 255, 255)")
            Left_frame.setStyleSheet("foreground-color: blue;\n")
            Left_frame.setFrameStyle(QFrame.Box | QFrame.Sunken)

            LeftButtons = QHBoxLayout(Left_frame)
            LeftButtons.addWidget(Left_frame)

            ## Check Value Button
            DataModel = ButtonText(' Enregister Campagne ')
            DataModel.clicked.connect(self.EnregistrerCampagne)
            LeftButtons.addWidget(DataModel)

            ##  Template Generation Button
            TbD1 = ButtonText(' à définir (commit?) ')
            TbD1.clicked.connect(self.GenerateTemplate)
            LeftButtons.addWidget(TbD1)

            ##  Open File  Button
            TbD2 = ButtonText(' à définir (résultats ?) ')
            TbD2.clicked.connect(self.Adefinir2)
            LeftButtons.addWidget(TbD2)

            return LeftButtons, Left_frame

        #   Chargement d'un fichier pour créer une campagne initiale,
        #   et enregistrement de la campagne en question.
        #
        #  @param: modeTest, permet d'exploiter UnitTest:
        #
        def CreationInitiale(self, modeTest=False):
            logging.info("Création Campagne (==> Chargement SCL ")
            self.initial = True

            time1 = time.time()

            if modeTest:  # Pour permettre à la suite de test (py_test) de tester IHM_campagne.
                self.fname = ('Lot9_outils/SCL_files/SCD_SITE_20200928.scd', "")
            else:
                self.fname = QFileDialog.getOpenFileName(self, 'Open file', 'SCL_files\*.*', " IEC61850 files")

            with LoadSCL("JLPT_3_ESSAI_2003.xls", False ,True) as (self.SCL_DATA):  # Les données des IED ne sont pas chargé
                logging.info("Chargement SCL initial:")  # Seul les IED concernés par la campagne seront chargés.

            pathSplit = self.fname[0].split(os.sep)  #
            NbRepertoire = len(pathSplit)  #

            self.SCL_loaded = SCL_FileName(pathSplit[NbRepertoire - 1], pathSplit[NbRepertoire - 2])

            time2 = time.time()
            delta1 = time2 - time1
            logging.info((' Temps pour charger le fichier SCL', delta1))

            self.sclMgr = self.SCL_DATA.sclMgr
            self.DataTypes = self.SCL_DATA.DataType
            self.tComm = self.SCL_DATA.tComm
            self.Utils = IEC_Utils(self.SCL_DATA)
            self.tIEDnames = self.sclMgr.get_IED_names_list()

            time3 = time.time()
            delta2 = time3 - time2
            logging.info((' Temps pour charger le fichier SCL hors IED', delta2))

            time4 = time.time()
            delta3 = time4 - time3
            logging.info((' Temps pour charger le fichier SCL hors IED', delta3))

            self.SCL_charge = True
            self.CreationCampagne()

        # \b ChargerCampagne:  Charge un fichier XML de description de campagne existant, permet de modifier
        #                   la campagne et de "l'exécuter".
        #  Le nom du fichier SCL de référence est dans la campagne.
        # TODO :
        def ChargerCampagne(self, _fileName=None, modeTest=False):
            logging.info("ChargerCampagne")

            with Load_Excel("JLPT_3_ESSAI_2003.xls", True, False) as (JLPT_TestSet):  # , self.T_LoadSCL):
                print("Chargement SCL ok")  # str(self.T_LoadSCL))


            #  TODO traiter le cas d'échec           if xmlCampagne is not None:
            #                self.Campagne_charge = True

            idxStation = 0
            self.treeView.clear()
            stationNameSet = False
            for item in list(xmlCampagne):

                if item.tag == 'ConfigFiles':
                    for File in list(item):
                        fType = File.get('type')
                        if fType == "SCL" and self.SCL_charge == False:
                            _SCLpath = File.get('path')
                            SCLpath = FileSupport.encodeName(_SCLpath)     # convert '/' ==> '\' or '\' ==> '/'
                            SCLsha = File.get('sha')

                            with LoadSCL(SCLpath, True, True) as (
                                    self.SCL_DATA):  # Les données des IED ne sont pas chargé
                                logging.info(
                                    "Chargement du SCL via le chargement de la campagne:")  # Seul les IED concernés par la campagne seront chargés.

                            self.sclMgr = self.SCL_DATA.sclMgr

                        if fType == 'u-test-bench':
                            UTESTpath = File.get('path')
                            TESTsha = File.get('sha')
# TODO affiché la description
                if item.tag == 'Description':
                    self.descBox.setPlaceholderText(item.get('text'))

                if item.tag == 'Substation':
                    name = item.get('name')
                    voltage = item.get('Voltage')
                    if stationNameSet == False:     ## Le nom du répertoire et du fichier est le nom de la première 'Substation'
                        stationNameSet = True
                        self.StationName = name

                    self.Station = QTreeWidgetItem(self.treeView)
                    self.Station.setText(0, name + '( ' + voltage + ' )')
                    self.Poste.append(self.Station)  # = self.addStation(self.Station, name, voltage)

                    for bay in list(item):
                        Bay = self.addBay(self.Poste[idxStation], bay.get('name'), bay.get('test'))
                        for ied in list(bay):
                            IED = self.addIED(Bay, ied.get('name'), ied.get('simulated'))

                            if ied.get('test') == 'True':
                                IED.setCheckState(0, Qt.Checked)
                            else:
                                IED.setCheckState(0, Qt.Unchecked)

                            if ied.get('simulated') == 'True':
                                IED.setCheckState(1, Qt.Checked)
                            else:
                                IED.setCheckState(1, Qt.Unchecked)

                            for iLD in list(ied):
                                LD = self.addLD(IED, iLD.get('inst'), iLD.get('test'), iLD.get('desc'))

                                LastSteps = len(list(iLD))
                                numStep = 0
                                for iStep in list(iLD):
                                    toTest = (iStep.get('test') == 'True')
                                    self.addStep(LD, numStep, len(list(iLD)), toTest, iStep.get('name'), iStep.get(
                                        'desc'))  # iLD.attrib['test'], iStep.attrib['name'], iStep.attrib['desc'])

                                    numStep = numStep + 1

                    idxStation = idxStation +1


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


            self.tStation = self.Utils.SCL_getStation()
            self.treeView.clear()

            mainStation = self.tStation[0]
            self.StationName = mainStation[0]

            for iStation in self.tStation:
                name     = iStation[0]
                voltage  = iStation[1]
                self.tBay = self.Utils.XML_getBayList(name)  # Récupère les Tranches et leurs IED
                if self.tBay is None:
                    msg = QMessageBox()
                    msg.setWindowTitle("Erreur de dans le SCL")
                    msg.setText(" La section Substation est absente")
                    return

                self.Station = QTreeWidgetItem(self.treeView)
                self.Station.setText(0, name + '( ' + voltage + ' )')
                self.Poste.append(self.Station) # = self.addStation(self.Station, name, voltage)

                logging.info("Création de la campagne par défaut")

                for iBay in self.tBay:
                    Bay = self.addBay(self.Station, iBay.name, 'True')
                    logging.info((' Chargement graphique BAY', iBay.name))

                    for iedName in self.tIEDnames:  # iBay.iedList:
                        #                        logging.info((' IED TG', iBay.name, iedName))
                        if iedName.endswith(iBay.name):
                            IED = self.addIED(Bay, iedName, "True")
                        elif (iBay.name == 'SITE1') and (iedName in ['TG', 'TOPO', 'GRP']):
                            IED = self.addIED(Bay, iedName, "True")
                        else:
                            continue

                        iIED = self.sclMgr.get_IED_by_name(iedName)
                        if iIED is None:
                            logging.info((' IED non trouvé: BayName', iBay.name, 'IedName:', iedName))
                            continue
                        Srv = self.Utils.getServer(iIED)
                        if Srv is None:
                            logging.info((' IED non trouvé: BayName', iBay.name, 'IedName:', iedName))
                            continue
                        for iLD in Srv.get_children('LDevice'):
                            LD = self.addLD(IED, iLD.inst, iLD.desc, 'True')  # par defaut un LD doit être testé.
                            numStep = 0
                            for iStep in DefaultSteps:
                                Step = self.addStep(LD, numStep, len(DefaultSteps), True, iStep[0], iStep[1])
                                numStep = numStep + 1

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

        ## \b Confirm:  Enregistre/confirme la création du pas de test
        #
        def Confirm(self):
            logging.info("Confirm")
            self.Nom = self.NomTest.text()
            self.Description = self.Description.text()
            if self.ActiveTest.isChecked():
                self.Active = 'True'
            else:
                self.Active = 'False'

            logging.info('Nom:' + self.Nom + ' Active:' + self.Active + ' description: ' + self.Description)
            self.dialog.close()

        ## \b Confirm:  Annulle la création du pas de test
        #
        def Abort(self):
            logging.info("Confirm")
            return None, None, None

        def Adefinir1(self):
            logging.info('bouton à définir 1')
            return

        def Adefinir2(self):
            logging.info('bouton à définir 2')
            return

        def checkStatus(self, item, column: int) -> None:
            logging.info("checkStatus", item, column)

            if column == 0:

                for bay in self.tGraphicalBay:
                    if bay == item:
                        if item.checkState(0) == Qt.Checked:  # Bay selectionné ?
                            for ied in bay.tIED:
                                ied.setCheckState(0, Qt.Checked)
                                for iLD in ied.tLD:
                                    iLD.setCheckState(0, Qt.Checked)
                        else:
                            for ied in bay.tIED:
                                ied.setCheckState(0, Qt.Unchecked)
                                for iLD in ied.tLD:
                                    iLD.setCheckState(0, Qt.Unchecked)
                        return

                    for ied in bay.tIED:
                        if ied == item:
                            for iLD in ied.tLD:
                                iLD.setCheckState(0, item.checkState(0))
                            return
            else:
                logging.info("Some field edited...")

        def indexOfItem(self, item: QTreeWidgetItem) -> int:
            index = 0
            parent = item.parent()
            if parent is not None:
                index = index + parent.indexOfChild(item) + 1 + self.indexOfItem(parent)
            return index

        # \b ajouteStep:  gère l'ajout d'un step de test (boite de dialogue)
        def ajouteStep(self):

            indexes = self.treeView.selectedIndexes()
            if indexes is None or len(indexes) == 0:
                return

            path = self.getPath(indexes)
            stepName, stepActive, stepDesc = self.DialogueTestStep()
            self.InsertStep(path, stepName, stepActive, stepDesc)

        # \b retireStep:  gère la supression d'un step de test (boite de dialogue)
        def retireStep(self):

            currNode = self.treeView.currentItem()
            parent1 = currNode.parent()
            parent1.removeChild(currNode)

        # \b InsertStep:  insertion des objets Qt qui représente un step de test.
        def InsertStep(self, path: str, stepName: str, stepActive: str, stepDesc: str):

            logging.info("InsertStep: " + path + stepName + stepActive + stepDesc)

            bayIEDld = path.split('.')
            StationName=bayIEDld[0]    # Sous Station
            bayName = bayIEDld[1]
            iedName = bayIEDld[2]
            ldName = bayIEDld[3]
            stepInsertName = bayIEDld[4]

            idxStation = 0
            for Station in self.Poste:

                if Station.text(0) == StationName:
                    bay = Station.child(idxStation)

                    for i in range(0,Station.childCount()):       # Looking The bay
                        iBay = Station.child(i)
                        if iBay.text(0) != bayName:
                            continue
                        else:
                            for j in range(0, iBay.childCount()):
                                iIED = iBay.child(j)
                                if iIED.text(0)!= iedName:
                                    continue
                                else:
                                    for k in range(0,iIED.childCount()):
                                        iLD = iIED.child(k)
                                        if iLD.text(0) != ldName:
                                            continue
                                        else:
                                            for l in range(0, iLD.childCount()):
                                                iStep = iLD.child(l)
                                                if iStep.text(0) != stepInsertName:
                                                    continue
                                                else:
                                                    logging.info('Step:' + iStep.text(0)  + iStep.text(0)  + iStep.text(0)  )
                                                    self.AddStep(iLD,  stepName, stepActive, stepDesc)
                                                    return
                                                    break


        def AddStep(self, childLD: QTreeWidgetItem, name: str, desc: str, test: str):
            logging.info("AddStep: " + name + " ," + desc + " ," + test)
            x = self.treeView.currentItem()
            y = self.treeView.currentIndex()
            Y2 = y.row()  # rangée courrante

            childStep = QTreeWidgetItem()  # (Pas d'héritage) !!!Item pour les cases à cocher
            childStep.setFlags(childLD.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            childLD.insertChild(Y2 + 1, childStep)

            self.dualPushButtons = QWidget()

            childStep.setText(0, name)
            childStep.setText(2, test)
            childStep.setText(3, desc)
            # Bouton pour ajouter et retirer des Steps de tests:
            self.hLayout = QHBoxLayout()

            self.addButton = QPushButton(" + ")
            self.hLayout.addWidget(self.addButton)
            self.addButton.clicked.connect(self.ajouteStep)

            self.hLayout.addWidget(self.removeButton)
            self.removeButton = QPushButton(" - ")
            self.removeButton.clicked.connect(self.retireStep)
            self.dualPushButtons.setLayout(self.hLayout)
            if test == 'True':
                childStep.setCheckState(0, Qt.Checked)  #
            else:
                childStep.setCheckState(0, Qt.Unchecked)  #

            self.treeView.setItemWidget(childStep, 1, self.dualPushButtons)
            #            self.treeView.setItemWidget(childStep, 1, dualPushButtons)
            X = self.treeView.currentItem()

        def retireStep(self):

            x = self.treeView.currentItem()
            y = self.treeView.currentIndex()
            Y2 = y.row()  # rangée courranted

            currNode = self.treeView.currentItem()
            parent1 = currNode.parent()
            parent1.removeChild(currNode)

        def GenerateTemplate(self):
            print('GenerateTemplate')



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

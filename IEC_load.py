#
# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
#
#
# This file is part of [R#SPACE], [IEC61850 Digital Control System testing.
#

import logging
#import pandas as XLRD
import xlrd as XLRD


## \b encodeFileName:  encode un chemin de fichier selon l'OS (Windows/Linux)
#
# Cette adapte le chemin des fichiers à l'OS, utile surtour pour __Main__ et tests.
#
# @param fName      : Nom du fichier ou chemin, utilisant '/' ou '\'. Encodage final pour l'OS utilisé.
# @param FileName   : Délai d'attente maximal en ms
#
#class Question:
#    def __init__(self, question_text, correct_answer='', hint=''):
#        self.question = question_text
#        self.correct_answer = correct_answer
#        self.hint = hint
#        self.Proposition = Proposition('', '')

class Proposition:
    def __init__(self, answer='', hint=''):
        self.reponse = []
        self.answer = answer
        self.hint = hint

class Answers:
    def __init__(self, _Ans1, _Ans2, _Ans3, _Ans4):
        self.Ans1 = _Ans1
        self.Ans2 = _Ans2
        self.Ans3 = _Ans3
        self.Ans4 = _Ans4

class question_topic:
    def __init__(self, _title):
        self.title = _title
        self.subQuestion = []
"""
 Définition du modèle de donnée d'un test JLPT
"""
class JLPT:
    def __init__(self, _year, _level):
        self.year  = _year
        self.level = _level

    class partie_1:
        def __init__(self,_text):
            self.text = _text
            self.question_topic = []

    class partie_2:
        def __init__(self, _text):
            self.text = _text
            self.question_topic = []

    class partie_3:
        def __init__(self, _text):
            self.text = _text
            self.question_topic = []

## \b LoadSCL:  classe générique pour charger un fichier SCL au niveau fichier et au niveau.
# Le code permet de s'abstraire des problèmes liés à des OS spécifiques
#
# @param fname      : le nom du fichier SCL
# @return sclMgr    : Point d'accès aux services de la librairie 'scl_loader'
# @return data      : Image de la section DataTypeTemplates du SCL.
# @return tComm     : Image de la section Communication du SCL

class Question:
    def __init__(self, question_text, correct_answer='', hint='' ):
        self.question = question_text
        self.correct_answer = correct_answer
        self.hint   = hint
        self.Proposition = []      # List de SubQuestion

class Proposition:
    def __init__(self,  answer='', hint=''):
        self.reponse = []
        self.answer  = answer
        self.hint    = hint

class LoadExcel(object):
    def __init__(self, _name: str, _load_excel:bool = False, _fullpath=False):
        self.file_name  = _name
        self.full_path   = _fullpath
        self.load_excel = _load_excel

    def __enter__(self):

        Test_Set = XLRD.open_workbook(self.file_name)
        sheet = Test_Set.sheet_by_index(0)              #Accès au premier onglet du tableau Excel
        return sheet

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Chargement fichier JLPT:" + str(self.file_name[0]) + "réussi.")
        
class Test_JLPT:
    def __init__(self, sheet):
        self.sheet = sheet
        self.line_index = 1
        self.TEST = JLPT(1991, 'Level4')
        self.parts =['Ⅰ','ⅠⅠ','Ⅲ']
        self.NumTitre = [ '1' , '2' ,'3']


    def TestPart(self):
        for i in range(self.line_index, self.sheet.nrows): 
            Title = self.sheet.cell_value(i, 0)

    # Détection d'un grand chapître
            if Title.startswith('問題'): 
                num_titre = Title[2]               
                num_titre = self.parts.index(num_titre)

                if num_titre == 0:
                    self.line_index = self.line_index + 1
                    self.TEST.partie_1.text = Title
                    print('self.TEST.partie1.text :' + self.TEST.partie_1.text )
                    self.ParseTest()
                    num_titre = num_titre + 1
                elif num_titre == 1: 
                    self.TEST.partie_2.text = Title
                    print('self.TEST.partie1.text :' + self.TEST.partie_2.text )
                    self.ParseTest()
                    num_titre = num_titre + 1
                elif num_titre == 2:
                    self.TEST.partie_3.text = Title
                    print('self.TEST.partie1.text :' + self.TEST.partie_3.text )

                    print("Chapitre de question:" + '問題' + ':' + Title[2])
                    # TODO récupérer le numéro de chapître
                    print('Chapitre de question' + Title)

                QUESTION = []       ## Exemple 問1・ 車の中に男の子が何人いますか。

    def ParseTest(self):

        try:
            QuestionText = self.sheet.cell_value(self.line_index, 1)  # Exemple:
        except IndexError:
            print('Fin de fichier')
            exit(1)

        if QuestionText.startswith('問'):      # Détection d'une phrase qui fera l'objet de question
            self.line_index = self.line_index + 1
            question = question_topic(QuestionText)  # exemple: 問1・ 車の中に男の子が何人いますか。'
            while(True):
                print("question" + question.title)
                Choix = self.GetProposition(question, self.sheet, self.line_index)
                if Choix is not None:
                    question.subQuestion.append(Choix)
                    print('Question text.... choix:' + Choix[0].reponse[0])
                    self.line_index = self.line_index + 1
                else:
                    break
        else:
            self.line_index = self.line_index + 1
            print('XXX')
            #
            ### Ajouter l'objet graphique avec les choix et cases à cocher.
            #
        print('############')


    def GetProposition(self, question:Question, sheet, line_index:int):
        try:
            question = str(sheet.cell_value(line_index, 2))
            print("Sub Question" + question)
        except IndexError:
            print('fin du fichier..')
            return None

        subQuestion = []
        if question.startswith('(') or question.startswith('（'):    # ASCII et UTF8 pour '('
            liste_choix = question.split('．')
            num_question  = liste_choix[0]
            topic        = liste_choix[1].split(' ')
            print('Choix' + num_question + topic[1] + topic[0])
            proposition = Proposition()
            proposition.hint   = ''
            proposition.answer = ''
            for i in range(1,len(liste_choix)):
                proposition.reponse.append(liste_choix[i])
            subQuestion.append(proposition)
            return subQuestion
        else:
            return None





if __name__ == '__main__':

    with LoadExcel("JLPT_3_ESSAI_2003.xls", True, False) as (JLPT_TestSet): 
        print("Chargement SCL ok")  # str(self.T_LoadSCL))

    Test = Test_JLPT(JLPT_TestSet)
    Test.TestPart()




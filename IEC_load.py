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


"""
 Définition du modèle de donnée d'un test JLPT
"""
class JLPT:
    def __init__(self, _year, _level):
        self.year  = _year
        self.level = _level

class Question:
    def __init__(self, _text, _answer): # 問1・ 車の中に男の子が何人いますか。
        self.text   = _text
        self.answer = _answer
        self.subQuestion = []

class SubQuestion:          # （1）．車 １．しゃ ２．くるま ３．ちゃ ４．くろま
    def __init__(self, _choix, _answer, _result):
        self.choix  = _choix
        self.answer = _answer
        self.result = False
 
class Proposition:
    def __init__(self, _text ):
        self.text = _text
        self.reponse = []
        self.hint    = []
        self.answer  = []     # IHM answer

class Test_JLPT:
    def __init__(self, sheet):
        self.sheet = sheet
        self.TEST = JLPT(1991, 'Level4')
        self.Chapitre = [ '問題Ⅰ' , '問題ⅠⅠ', '問題Ⅲ' ]
        self.Section  = [ 1 , 2 , 3]
        self.Consigne = ""         # " 問題Ⅰ＿＿＿のことばはどうよみますか"
        self.Part1 = [] # QuestionX()
        self.Part2 = [] #QuestionX()
        self.lineIndex = 1

        self.TestSection     = 0        # Colonne 0 Titre 問題Ⅰ＿＿＿のことばはどうよみますか
        self.TestQuestion    = 1        # Colonne 1     問1・ 車の中に男の子が何人いますか。
        self.TestProposition = 2        # Colonne 2     （1）．車 １．しゃ ２．くるま ３．ちゃ ４．くろま

    def TestPart(self):
        num_titre = 1
        self.lineIndex  = 1
        T1 = self.sheet.cell_value(self.lineIndex ,   self.TestSection)       # Titre 問題Ⅰ＿＿＿のことばはどうよみますか
        if not T1.startswith('問題'):
            print('Manque 問題 sur première ligne' )

        Q1 = self.sheet.cell_value(self.lineIndex+1 , self.TestQuestion)      # 問1・ 車の中に男の子が何人いますか。
        if not Q1.startswith('問'):
            print('Manque 問 sur deuxième ligne' )

        P1 = self.sheet.cell_value(self.lineIndex+2 , self.TestProposition)   #（1）．車 １．しゃ ２．くるま ３．ちゃ ４．くろま
        if not P1.startswith('（1）'):
            print('Manque （1） sur troisième ligne' )

 
        T1 = self.sheet.cell_value(self.lineIndex , 0)

        for Chapitre, Numero in zip (self.Chapitre,self.Section):
            Chapitre_1 = JLPT(1991,'Level 4')
            self.Part = self.ParseTest()

#            self.Part2,line_index = self.ParseTest(line_index)
#            self.Part3,line_index = self.ParseTest(line_index)
            num_titre = num_titre + 1
        return self.TEST

    def ParseTest(self):
        self.lineIndex = 2
        _question = self.sheet.cell_value(self.lineIndex , self.TestQuestion)  # Exemple:
        question = []  #Liste des questions
        while _question.startswith('問'):      # Détection d'une phrase qui fera l'objet de question
            print('Question:' + _question)
            question = Question(_question,[])
            self.lineIndex =  self.lineIndex + 1

            while(True):
                Choix,line_index = self.GetProposition(self.sheet)
                if Choix is not None:
                    question.answer.append(Choix)
                else:                           
                    QuestionText = self.sheet.cell_value( self.lineIndex, 1)
                    if QuestionText.startswith('問'):
                        question.subQuestion.append(QuestionText)
                        self.lineIndex = self.lineIndex + 1
                        break
                self.lineIndex = self.lineIndex + 1
            
            print('-------------')
        return question



    def GetProposition(self, sheet):
        TxtQuestion =  sheet.cell_value(self.lineIndex, 2)
        print("Sub Question" + TxtQuestion)

        proposition = Proposition(TxtQuestion)
        if TxtQuestion.startswith('(') or TxtQuestion.startswith('（'):    # ASCII et UTF8 pour '('
            liste_choix = TxtQuestion.split('．')
            num_question  = liste_choix[0]
            topic        = liste_choix[1].split(' ')
            for i in range(1,len(liste_choix)):
                proposition.reponse.append(liste_choix[i])

            return proposition, self.lineIndex
        return None, self.lineIndex

## \b LoadSCL:  classe générique pour charger un fichier SCL au niveau fichier et au niveau.
# Le code permet de s'abstraire des problèmes liés à des OS spécifiques
#
# @param fname      : le nom du fichier SCL
# @return sclMgr    : Point d'accès aux services de la librairie 'scl_loader'
# @return data      : Image de la section DataTypeTemplates du SCL.
# @return tComm     : Image de la section Communication du SCL

class LoadExcel(object):
    def __init__(self, _name: str, _load_excel: bool = False, _fullpath=False):
        self.file_name = _name
        self.full_path = _fullpath
        self.load_excel = _load_excel

    def __enter__(self):
        self.Test_Set = XLRD.open_workbook(self.file_name)
        sheet = self.Test_Set.sheet_by_index(0)  # Accès au premier onglet du tableau Excel
        return sheet
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("__exit__")
        self.Test_Set.release_resources()
        del(self.Test_Set)


if __name__ == '__main__':

    with LoadExcel("JLPT_3_ESSAI_2003.xls", True, False) as (JLPT_TestSet): 
        print("Chargement SCL ok")  # str(self.T_LoadSCL))

    Test = Test_JLPT(JLPT_TestSet)
    Test.TestPart()




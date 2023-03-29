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


"""
 Définition du modèle de donnée d'un test JLPT
"""
class JLPT_Section:
    def __init__(self, _part, _year, _level):
        self.Part        = _part
        self.year        = _year
        self.level       = _level
        self.QuestionSet = [] # list[JLPT_Section.Question]       # liste de Question

    class Question: # 
        def __init__(self, _text, _answer: list[str]): # 問1・ 車の中に男の子が何人いますか。
            self.text        = _text        # 問1・ 車の中に男の子が何人いますか。
            self.answer      = _answer      # Choix de l'utilisateur
            self.subQuestion  = [] #: list[JLPT_Section.Question.Proposition]

        class Proposition:
            def __init__(self, _question, _reponse ):
                self.question = []    # （1）．雨 １．かぜ ２．あめ ３．ゆき ４．くも
                self.reponse =  _reponse                        
                self.hint    = ''
                self.answer  = ''            # IHM answer

class Test_JLPT:
    def __init__(self, sheet):
        self.sheet = sheet
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
            exit(-1)
        else:
            JLPT_Part1 = JLPT_Section(T1, 1991, 'Level4')
            self.Part1, self.lineIndex = self.ParseTest(JLPT_Part1, self.lineIndex)

#            JLPT_Part2 = JLPT_Section(T1, 1991, 'Level4')
#            self.Part2, self.lineIndex = self.ParseTest(JLPT_Part1, self.lineIndex)

#            JLPT_Part3 = JLPT_Section(T1, 1991, 'Level4')
#            self.Part3, self.lineIndex = self.ParseTest(JLPT_Part1, self.lineIndex)

            print('Manque 問題 sur première ligne' )
            exit(-1)

    def ParseTest(self,JLPT_Part1:JLPT_Section, lineIndex:int):
        lineIndex = lineIndex+1 # Sinon pointe sur '問題'
        _question = self.sheet.cell_value(self.lineIndex , self.TestQuestion)  # '問1・ 車の中に男の子が何人いますか。'
        JLP_question = JLPT_Section.Question(_question, [])
        JLPT_Part1.QuestionSet.append(JLP_question)
        _SubQuestion=''
      # '（1）．車 １．しゃ ２．くるま ３．ちゃ ４．くろま'
        while True:
            _question = self.sheet.cell_value(lineIndex , self.TestQuestion)
            if _question.startswith('問'):
                    JLP_question =JLPT_Section.Question(_question, [])
                    JLPT_Part1.QuestionSet.append(JLP_question)
                    print('****** Question : ' , _question  + ' ' + str(self.lineIndex))
                    lineIndex = lineIndex +1
                    _SubQuestion = self.sheet.cell_value(lineIndex , self.TestProposition)
            else:
                _Proposition = JLPT_Section.Question.Proposition(_SubQuestion, []) # '問1・ 車の中に男の子が何人いますか。'
                while _SubQuestion.startswith('（'):
                    _Proposition.reponse.append(_SubQuestion)
#                    _Proposition = JLPT_Section.Question.Proposition(_SubQuestion, []) # '問1・ 車の中に男の子が何人いますか。'
#                    X = JLPT_Section.Question.Proposition. .uestion.append(_Proposition)

                    print('SubQuestion : ' , _SubQuestion + ' ' + str(lineIndex))
                    lineIndex = lineIndex + 1
                    _SubQuestion = self.sheet.cell_value(lineIndex , self.TestProposition)
                
                _question = self.sheet.cell_value(lineIndex , self.TestQuestion)
                if _question.startswith('問'):
                    continue
                _Chapitre = self.sheet.cell_value(lineIndex , 0)
                if _Chapitre.startswith('問題'):
                    print('fin')
                    break
            continue
        return JLP_question, lineIndex

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




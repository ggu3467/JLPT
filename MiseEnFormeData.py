
## Module pour mettre en forme les données du JLPT

import re

class  TransformInPutData:
#  Data  s = "（1）．魚 １．こめ ２．さかな ３．にく ４．やさい"      Pattern entrante
#    def __init__(self):
#        # Use regex to extract the main number (1)

    def Transform0( _Data, Kanji):
        items = re.findall(r'\d+．[^\d]*', _Data)

        # Manually handle the last item by removing the trailing '3'
        last_item = re.sub(r' 3$', '', items[-1]).strip()

        # Build the result list with the custom structure for the last part
        result = [[Kanji]] + [[item.strip()] for item in items[:-1]] + [[last_item]]

        # Output the final result
        print(result)
        return result


    def is_number(self,number):
        return type(number) is (int);


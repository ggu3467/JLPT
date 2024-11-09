
## Module pour mettre en forme les données du JLPT

import re

class  TransformInPutData:
#  Data  s = "（1）．魚 １．こめ ２．さかな ３．にく ４．やさい"      Pattern entrante
    def __init__(self, _Data):
        # Use regex to extract the main number (1)
        self.Data = _Data

    def Transform(self,_Data):
        main_number = re.search(r'（(\d+)）', _Data).group(1)

        # Split the string by spaces to separate the items
        items = _Data.split(' ')[1:]  # Skip the first part as it is the main number

        # Clean the first item to remove unwanted characters
        items[0] = items[0].replace('．', '')  # Remove the '．' from the first item

        # Create the desired list format
        result = [int(main_number)] + [item.strip() for item in items]
        return result

    def is_number(self,number):
        return type(number) is (int);


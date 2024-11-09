
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Créer un layout principal
        self.layout = QVBoxLayout()

        # Créer un layout de grille pour organiser les boutons
        self.grid_layout = QGridLayout()

        # Ajouter le layout de grille au layout principal
        self.layout.addLayout(self.grid_layout)

        # Ajouter des boutons au layout de grille
        self.add_buttons()

        # Définir le layout principal pour le widget
        self.setLayout(self.layout)

    def add_buttons(self):
        # Exemple de boutons à ajouter
        buttons = [
            ("Button 1", 0, 0),
            ("Button 2", 0, 1),
            ("Button 3", 1, 0),
            ("Button 4", 1, 1),
            ("Button 5", 2, 0),
            ("Button 6", 2, 1),
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            self.grid_layout.addWidget(button, row, col)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())


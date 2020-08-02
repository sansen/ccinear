# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  https://launchpad.net/encuentro
#
# Copyright 2019-2020 Santiago Torres Batan

import sys
from PySide2 import QtWidgets, QtCore


class Window(QtWidgets.QMainWindow):
    search_signal = QtCore.Signal()
    action_signal = QtCore.Signal()
    section_selection_signal = QtCore.Signal()

    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)

        self.play_icon = '\u25B6'
        self.download_icon = '\u2193'
        self.stop_icon = '\u25a0'

        width = 460
        height = 640

        title = "CineAR - ¿Que queres ver?"
        self.setWindowTitle(title)

        self.setMinimumSize(QtCore.QSize(width, height))
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.widget1 = QtWidgets.QWidget()
        self.layout.addWidget(self.widget1)

        self.layout1 = QtWidgets.QHBoxLayout()
        self.widget1.setFixedHeight(50)
        self.widget1.setLayout(self.layout1)

        self.layout1.addWidget(QtWidgets.QLabel("Buscar:"))
        self.searchInput = QtWidgets.QTextEdit()
        self.layout1.addWidget(self.searchInput)

        self.ok_button = QtWidgets.QPushButton()
        self.ok_button.setFixedWidth(50)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.search_signal)

        self.layout1.addWidget(self.ok_button)

        self.cb = QtWidgets.QComboBox()
        self.cb.currentIndexChanged.connect(self.section_selection_signal)
        self.layout.addWidget(self.cb)

        self.treewidget = QtWidgets.QTreeWidget()
        self.treewidget.setColumnCount(6)
        self.treewidget.setHeaderLabels(
            ['SID', 'Titulo', 'DUR [min]', 'AÑO', '', '']
        )
        self.treewidget.itemClicked.connect(self.on_item_clicked)
        self.treewidget.itemClicked.connect(self.action_signal)

        self.layout.addWidget(self.treewidget)

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
        )
        self.tray_icon.activated.connect(self.system_icon)

        menu = QtWidgets.QMenu()
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(sys.exit)
        self.tray_icon.setContextMenu(menu)

        self.tray_icon.show()
        self.show()

    def on_item_clicked(self, it, col):
        self.currentItem = it
        self.action = []
        if col == 4 and it.text(4) == self.play_icon:
            self.action = [it.text(0), 'play']
            it.setText(4, self.stop_icon)
        elif col == 5 and it.text(5) == self.download_icon:
            self.action = [it.text(0), 'down']
            it.setText(5, self.stop_icon)

    def set_items(self, items):
        self.cb.addItems([i.capitalize() for i in items.values()])

    def build_tree(self, productions, reset=False):
        if reset:
            self.treewidget.clear()

        for prod in productions:
            item = QtWidgets.QTreeWidgetItem(self.treewidget)
            item.setText(0, f"{prod['sid']}")
            item.setText(1, f"{prod['titulo']}")
            item.setText(2, f"{prod['dura']}")
            item.setText(3, f"{prod['anio']}")

            asociados = prod.get('subitems', [])
            if asociados == []:
                item.setText(4, self.play_icon)
                item.setText(5, self.download_icon)

            # Sinopsis y Valoracion
            sino = ".\n".join(prod['sino'].strip().split('. '))
            rate = float(prod.get('rate', 3))
            i_part, d_part = divmod(rate, 1)
            ci_part, di_part = divmod(5-rate, 1)
            stars = ''
            for i in range(int(i_part)):
                stars += '\u2605'
            if d_part > 0.0:
                stars += '\u272C'  # '\u2BE8' # '\u002A'# '\u2B50'
            for i in range(int(ci_part)):
                stars += '\u2606'

            item.setToolTip(1, f"Sinopsis :: {sino}\n\nValoracion: {stars} ({rate})")
            self.build_sub_tree(item, asociados)

        header = self.treewidget.header()
        self.treewidget.setColumnWidth(0, 75)
        self.treewidget.setColumnWidth(2, 50)
        self.treewidget.setColumnWidth(3, 50)
        self.treewidget.setColumnWidth(4, 25)
        self.treewidget.setColumnWidth(5, 25)

        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Fixed)
        header.setStretchLastSection(False)

    def build_sub_tree(self, parent_item, productions, reset=False):
        if reset:
            self.treewidget.clear()

        for prod in productions:
            item = QtWidgets.QTreeWidgetItem(parent_item)
            item.setText(0, f"{prod['sid']}")
            item.setText(1, f"{prod['titulo']}")
            item.setText(2, f"{prod['temp']}")
            item.setText(3, f"{prod['capi']}")
            item.setText(4, '\u25B6')
            item.setText(5, '\u2193')

            item.setToolTip(2, f"Temporada")
            item.setToolTip(3, f"Capitulo")

    def system_icon(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.show()

    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def closeEvent(self, event):
        event.ignore()
        self.hide()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = Window()
    window.show()
    app.exec_()

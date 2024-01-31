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
# Copyright 2019-2023 Santiago Torres Batan

import sys
from PySide2 import QtWidgets, QtCore, QtGui
from datetime import datetime as datetime_, timedelta


class Window(QtWidgets.QMainWindow):
    """
    Clase de la ventana principal 
    """
    search_signal = QtCore.Signal()
    action_signal = QtCore.Signal()
    section_selection_signal = QtCore.Signal()
    preferences_signal = QtCore.Signal()

    def __init__(self, config, parent=None):
        super(Window, self).__init__(parent=parent)

        self.play_icon = '\u25B6'
        self.download_icon = '\u2193'
        self.stop_icon = '\u25a0'
        self.pause_icon = '\u23F8'
        self.pref_icon = '\u2699'

        self.preferences_config = config

        width = 540
        height = 720

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
        self.searchInput = QtWidgets.QLineEdit()
        self.layout1.addWidget(self.searchInput)

        self.ok_button = QtWidgets.QPushButton()
        self.ok_button.setFixedWidth(50)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.search_signal)

        self.pref_button = QtWidgets.QPushButton()
        self.pref_button.setFixedWidth(50)
        self.pref_button.setText(self.pref_icon)
        self.pref_button.clicked.connect(self.open_preferences_dialog)

        self.layout1.addWidget(self.ok_button)
        self.layout1.addWidget(self.pref_button)

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
            self.action = [it.text(0), 'play', it]
            it.setText(4, self.stop_icon)
            it.setToolTip(4, f"Reproduciendo")
        elif col == 5 and it.text(5) == self.download_icon:
            self.action = [it.text(0), 'down', it]
            it.setText(5, self.pause_icon)
            it.setToolTip(5, f"Descargando")
        elif col == 5 and it.text(5) == self.pause_icon:
            self.action = [it.text(0), 'stop', it]
            it.setText(5, self.download_icon)
            it.setToolTip(5, f"")

    def set_items(self, items):
        self.cb.addItems([i['titulo'].capitalize() for i in items])

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
                item.setToolTip(4, f"Reproducir")
                item.setText(5, self.download_icon)
                item.setToolTip(5, f"Descargar")

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

            item.setToolTip(
                1,
                f"Sinopsis :: {sino}\n\nValoracion: {stars} ({rate})"
            )
            self.build_sub_tree(item, asociados)

        header = self.treewidget.header()
        self.treewidget.setColumnWidth(0, 85)
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

        self.treewidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.treewidget.setSortingEnabled(True)

    def build_sub_tree(self, parent_item, productions, reset=False):
        if reset:
            self.treewidget.clear()

        for prod in productions:
            item = QtWidgets.QTreeWidgetItem(parent_item)
            item.setText(0, f"{prod['sid']}")
            item.setText(1, f"{prod['titulo']}")
            item.setText(2, f"S{prod['temp']:02}")
            item.setText(3, f"E{prod['capi']:02}")
            item.setText(4, '\u25B6')
            item.setText(5, '\u2193')

            item.setToolTip(2, f"Temporada")
            item.setToolTip(3, f"Capitulo")

    def system_icon(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.show()

    def update_progress(self, item, current_download):
        gradient = QtGui.QLinearGradient(0, 0, 1, 0)
        gradient.setCoordinateMode(QtGui.QLinearGradient.StretchToDeviceMode)
        gradient.setColorAt(0, QtGui.QColor('Green'))
        gradient.setColorAt(current_download, QtGui.QColor('White'))
        brush = QtGui.QBrush(gradient)

        item.setBackground(0, QtGui.QBrush(brush))

    def open_preferences_dialog(self):
        pf = PreferencesDialog(self)
        pf.exec()

    def qWait(self, t):
        end = datetime_.now() + timedelta(milliseconds=t)
        while datetime_.now() < end:
            QtGui.QGuiApplication.processEvents()

    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def closeEvent(self, event):
        event.ignore()
        self.hide()



class PreferencesDialog(QtWidgets.QDialog):
    """
    Clase de la ventana de dialogo de prefenrencias 
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.setWindowTitle("Preferencias")

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.accepted.connect(self.accept_preferences)
        # self.buttonBox.rejected.connect(self.reject_preferences)

        self.dir_button = QtWidgets.QPushButton()
        self.dir_button.setFixedWidth(80)
        self.dir_button.setText('Browse')
        self.dir_button.clicked.connect(self.browse_clicked)

        self.vLayout = QtWidgets.QVBoxLayout()
        # self.hLayout = QtWidgets.QHBoxLayout()

        message = QtWidgets.QLabel("Directorio de Descarga")
        self.fileConfig = QtWidgets.QLineEdit()
        self.fileConfig.setText(self.parent.preferences_config.get("download_dir"))

        message2 = QtWidgets.QLabel("Calidad de Video")
        self.cb = QtWidgets.QComboBox()
        # Valores Harcodeados:
        # Correspoden a las calidades de Cinear
        qaValues = ["360p", "480p", "720p", "1080p"]
        self.cb.addItems(qaValues)

        cvq = qaValues.index(self.parent.preferences_config.get('prefered_video_quality'))
        self.cb.setCurrentIndex(cvq)

        self.vLayout.addWidget(message)
        self.vLayout.addWidget(self.fileConfig)
        self.vLayout.addWidget(self.dir_button)
        self.vLayout.addWidget(message2)
        self.vLayout.addWidget(self.cb)

        # self.vLayout.addWidget(self.hLayout)
        self.vLayout.addWidget(self.buttonBox)
        self.setLayout(self.vLayout)

    def browse_clicked(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setDirectory(self.parent.preferences_config.get("download_dir"))
        filepath = dialog.getExistingDirectory(self, 'Select Folder')

        if filepath:
            self.fileConfig.setText(filepath)

    def accept_preferences(self):
        config = self.parent.preferences_config
        fpath = self.fileConfig.text()
        pQuality = self.cb.currentText()

        if fpath:
            config['download_dir'] = fpath
            changed = True
        if pQuality:
            config['prefered_video_quality'] = pQuality
            changed = True

        if changed:
            self.parent.preferences_signal.emit()

        self.close()

    def reject_preferences(self):
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = Window()
    window.show()
    app.exec_()

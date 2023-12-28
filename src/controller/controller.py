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
# Copyright 2019-2020 Santiago Torres Batan

import threading
from datetime import datetime as datetime_, timedelta
from PySide2 import QtGui

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.init()

    def init(self):
        self.model.auth_login()
        self.model.user_pid()
        self.model.user_home()

        self.view.set_items(self.model.cm.TIRAS)
        self.view.search_signal.connect(self.search)
        self.view.action_signal.connect(self.action)
        self.view.preferences_signal.connect(self.update_config)
        self.download_thread = None

        # Seteo Novedades
        items = self.model.set_tira(0)
        self.view.build_tree(items, reset=True)

    def section_selection(self):
        tira = self.view.cb.currentIndex()
        items = self.model.set_tira(tira)
        self.view.build_tree(items, reset=True)

    def search(self):
        search_key = self.view.searchInput.text()
        if search_key:
            items = self.model.search(search_key)
            self.view.build_tree(items, reset=True)

    def update_config(self):
        self.model.update_config(self.view.preferences_config)   


    def qWait(self, t):
        end = datetime_.now() + timedelta(milliseconds=t)
        while datetime_.now() < end:
            QtGui.QGuiApplication.processEvents()

    def action(self):
        if self.view.action == []:
            return

        sid = self.view.action[0]
        item = self.view.action[2]

        data, digest_clave = self.model.production_id(
            self.view.action[0], source='INCAA'
        )

        if self.view.action[1] == 'stop':
            self.model.dm.pause_download(sid)
            return

        if self.view.action[1] == 'play':
            self.download_thread = threading.Thread(
                target=self.model.production_chuncks,
                args=(data, digest_clave, sid)
            )
        else:
            self.download_thread = threading.Thread(
                target=self.model.production_chuncks,
                args=(data, digest_clave, sid, False)
            )
        self.download_thread.start()

        # while True:
        #     if sid in self.model.dm.current_downloads:
        #         if self.model.dm.current_downloads[sid]['completed'] == False:
        #             self.view.update_progress(item, self.model.dm.current_downloads[sid]['progress'])
        #             self.qWait(2000)
        #         else:
        #             break
            
        #self.download_thread.join()

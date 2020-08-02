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

import threading


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.init()

    def init(self):
        self.model.auth_login()
        self.model.user_pid()

        self.view.set_items(self.model.TIRAS)
        self.view.section_selection_signal.connect(self.section_selection)
        self.view.search_signal.connect(self.search)
        self.view.action_signal.connect(self.action)
        self.download_thread = None

        # Seteo Novedades
        items = self.model.user_home(tipotira='novedades')
        self.view.build_tree(items, reset=True)

    def section_selection(self):
        tira = list(self.model.TIRAS.keys())[self.view.cb.currentIndex()]
        items = self.model.user_home(tira)
        self.view.build_tree(items, reset=True)

    def search(self):
        items = self.model.search(self.view.searchInput.toPlainText())
        self.view.build_tree(items, reset=True)

    def action(self):
        if self.view.action == []:
            return

        data, digest_clave = self.model.production_id(
            self.view.action[0], source='INCAA'
        )
        if self.view.action[1] == 'play':
            self.download_thread = threading.Thread(
                target=self.model.production_chuncks,
                args=(data, digest_clave)
            )
        else:
            self.download_thread = threading.Thread(
                target=self.model.production_chuncks,
                args=(data, digest_clave, False)
            )
        self.download_thread.start()

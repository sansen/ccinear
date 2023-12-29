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


import datetime
import pickle


class CinearCache:
    """
    Mantiene un cache con los resultados de request a la api,
    para mejorar el rendimiento de la aplicacion
    """
    def __init__(self):
        self.cache_path = 'cinearcache.pkl'
        self.values = {}
        try:
            with open(self.cache_path, 'rb') as f:
                self.values = pickle.load(f)
                # Si pasa mas de 1 dia
                if (self.values['timestamp'] + datetime.timedelta(days=1)) > datetime.datetime.now():
                    self.values = {}
        except FileNotFoundError:
            # print('The file does not exist.')
            pass

    def get(self, key):
        return self.values.get(key, '')

    def set(self, key, value):
        self.values[key] = value
        self.values['timestamp'] = datetime.datetime.now()
        with open(self.cache_path, 'wb') as f:
            pickle.dump(self.values, f)

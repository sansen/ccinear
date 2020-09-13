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

"""
Console CineAR
Version con Interfaz Grafica

Maneja la interfaz de cine.ar desde la consola,
realiza backups de tus peliculas favoritas, miralas offline.

Usage:
  cinear-qt.py [--user=<user>] [--passw]
  cinear-qt.py (-h | --help)
  cinear-qt.py --version

Options:
  -h --help   Show this screen.
  version     Show version.
"""


import sys
import yaml
import base64

from gui import gui
from gui import controller
from src import ccinear

from getpass import getpass
from docopt import docopt
from PySide2 import QtWidgets


def main(email, passw):
    credentials = {'email': email, 'password': passw}

    app = QtWidgets.QApplication([])
    view = gui.Window()

    model = ccinear.CineAR(
        credentials=credentials,
        config=config
    )
    c = controller.Controller(model=model, view=view)
    sys.exit(app.exec_())


if __name__ == '__main__':
    args = docopt(__doc__, version='ccinear-qt v0.1')

    try:
        with open('config.yaml', 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    except Exception:
        config = None

    # Setting User
    if args['--user']:
        email = args['--user']
        if config:
            config['user'] = args['--user']
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f)
    else:
        try:
            email = config['user']
        except Exception:
            print('No se ha podido establecer el usuario.')
            print('Setee sus credenciales de Cine.ar usando --user')
            exit()

    # Setting Password
    if args['--passw']:
        passw = getpass()
        if config:
            config['passw'] = base64.b64encode(str.encode(passw))
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f)
    else:
        try:
            passw = base64.b64decode(config['passw']).decode('utf-8')
        except Exception:
            passw = getpass()
            if config:
                config['passw'] = base64.b64encode(str.encode(passw))
                with open('config.yaml', 'w') as f:
                    yaml.dump(config, f)

    main(email, passw)

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
Maneja la interfaz de cine.ar desde la consola o GUI.
Realiza backups de tus peliculas favoritas, miralas offline.

No dejes de utilizar cine.ar y apoyar
el desarrollo del cine argentino.

No infringas el copyright

Usage:
  cinear-all.py [--user=<user>] [--passw] gui
  cinear-all.py [--user=<user>] [--passw] play SID
  cinear-all.py [--user=<user>] [--passw] [--path=/path/to/downloaddir/] download SID
  cinear-all.py [--user=<user>] [--passw] home [<tira>]
  cinear-all.py [--user=<user>] [--passw] search <string>
  cinear-all.py (-h | --help)
  cinear-all.py (-v | --version)

Options:
  -h --help     Show this screen.
  -v --version  Show version.
  SID           INCAA, Produccion ID
  <string>      String to search for
  <tira>        El numero de tira presentado. Ejecutar primero cineae-all.py -H

  E.g: ccinear-all.py -H
"""

import os
import sys
import yaml
import base64

from controller.controller import Controller
from gui.gui import Window
from  model.cinear import CineAR

from getpass import getpass
from docopt import docopt
from PySide2 import QtWidgets


def mainGui(email, passw, config):
    credentials = {'email': email, 'password': passw}

    app = QtWidgets.QApplication([])
    view = Window(config)

    model = CineAR(
        credentials=credentials,
        config=config
    )
    c = Controller(model=model, view=view)
    sys.exit(app.exec_())


def mainTui(email, passw, config, args):
    cinear = CineAR(
        credentials={'email': email, 'password': passw},
        config=config,
        TUI=True
    )
    # User Auth
    cinear.auth_login()
    cinear.user_pid()

    # Parsing args
    if args['search']:
        cinear.search(args['<string>'])

    elif args['play']:
        SID = args['SID']
        data, digest_clave = cinear.production_id(SID, source='INCAA')
        cinear.production_chuncks(data, digest_clave, SID)

    elif args['download']:
        play = False
        SID = args['SID']
        data, digest_clave = cinear.production_id(SID, source='INCAA')
        cinear.production_chuncks(data, digest_clave, SID, play)

    elif args['home']:
        cinear.user_home()
        if not args['<tira>']:
            tira = False
        else:
            tira = int(args['<tira>'])
        cinear.display_tiras(tira)


if __name__ == '__main__':
    args = docopt(__doc__, version='ccinear v0.2')

    try:
        with open('config/config.yaml', 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    except Exception:
        config = None

    # Setting User
    if args['--user']:
        email = args['--user']
        config['user'] = args['--user']
        if config:
            with open('config/config.yaml', 'w') as f:
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
        config['passw'] = base64.b64encode(str.encode(passw))
        if config:
            with open('config/config.yaml', 'w') as f:
                yaml.dump(config, f)
    else:
        try:
            passw = base64.b64decode(config['passw']).decode('utf-8')
            config['passw'] = base64.b64encode(str.encode(passw))
        except Exception:
            passw = getpass()
            config['passw'] = base64.b64encode(str.encode(passw))
            with open('config/config.yaml', 'w') as f:
                yaml.dump(config, f)

    if args['gui']:
        mainGui(email, passw, config)
    else:
        mainTui(email, passw, config, args)

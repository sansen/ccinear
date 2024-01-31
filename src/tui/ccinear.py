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

"""
Console CineAR
Maneja la interfaz de cine.ar desde la consola,
realiza backups de tus peliculas favoritas, miralas offline.

No dejes de utilizar cine.ar y apoyar
el desarrollo del cine argentino.

No infringas el copyright

Usage:
  ccinear.py [--user=<user>] [--passw] (play | -p) SID
  ccinear.py [--user=<user>] [--passw] [--path=/path/to/downloaddir/] (download | -d) SID
  ccinear.py [--user=<user>] [--passw] (home | -H) [<tira>]
  ccinear.py [--user=<user>] [--passw] (search | -s) <string>
  ccinear.py (-h | --help)
  ccinear.py --version

Options:
  -h --help   Show this screen.
  version     Show version.
  SID         INCAA, Produccion ID
  <string>    String to search for
  <tira>      El numero de tira presentado, luego de tirar el comando
              cinear.py -H
  E.g: ccinear.py -H
"""
import os
import sys
import yaml
import base64

from docopt import docopt
from getpass import getpass
from subprocess import Popen

# relative imports
sys.path.append(os.getcwd() + "/model")
import cinear

if __name__ == '__main__':
    args = docopt(__doc__, version='Cine.ar en consola v0.2')

    try:
        with open('config/config.yaml', 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    except Exception:
        config = None

    # Setting User
    if args['--user']:
        email = args['--user']
        if config:
            config['user'] = args['--user']
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
        if config:
            config['passw'] = base64.b64encode(str.encode(passw))
            with open('config/config.yaml', 'w') as f:
                yaml.dump(config, f)
    else:
        try:
            passw = base64.b64decode(config['passw']).decode('utf-8')
        except Exception:
            passw = getpass()
            if config:
                config['passw'] = base64.b64encode(str.encode(passw))
                with open('config/config.yaml', 'w') as f:
                    yaml.dump(config, f)

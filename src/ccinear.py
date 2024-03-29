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
import re
import yaml
import base64
import hashlib
import requests
import urllib.request

from docopt import docopt
from getpass import getpass
from subprocess import Popen


class CineAR:
    """
    Clase principal del programa utilizada para manejar la autenticacion
    y demas request al sitio cinear.com.ar.
    Ademas contiene la funcionalidad para reproducir un o descargar un
    contenido.
    """
    def __init__(self, credentials, config, TUI=False):
        self.credentials = credentials
        self.config = config
        self.ID_URI = "https://id.cine.ar/v1.5"
        self.API_URI = "https://play.cine.ar/api/v1.7"
        self.PLAYER_URL = "https://player.cine.ar/odeon/"

        self.TOKEN = None
        self.auth = None
        self.perfil = None

        self.TUI = TUI

        self.session = requests.Session()
        self.items = 0

    def get_headers(self, token=None, auth=None):
        """Genera los headers para los request HTTP."""
        header = {
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json, text/plain',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Referer': 'https://play.cine.ar/bienvenida'
        }
        if self.TOKEN:
            header.update({'Authorization': 'Bearer ' + self.TOKEN})
        if self.auth:
            header.update({'x-auth-key': self.auth})
        return header

    def auth_login(self):
        """
        Autenticacion de usuario.
        Obtener el TOKEN de sesion.
        """
        if not self.credentials['email'] or not self.credentials['password'] \
           or self.credentials['email'] == '' or self.credentials['password'] == '':
            print(
                "Setee sus credenciales de Cine.ar usando --user y --passw"
            )
            exit()
        self.session.headers.update(self.get_headers())
        auth_url = '{0}/auth/login'.format(self.ID_URI)

        try:
            r = self.session.post(
                auth_url,
                json=self.credentials
            )
            self.TOKEN = r.json()['token']
            self.session.headers.update(self.get_headers())

        except Exception:
            print('Fallo la autenticacion')
            exit()

    def search(self, term):
        """Buscar termnio en cinear."""
        search_url = "{0}/search/{1}?cant=24&orden=rele&pag=1&perfil={2}".format(
            self.API_URI, term, self.perfil
        )
        r = self.session.get(search_url)

        items = []
        for prod in r.json()['prods']:
            subitems = []
            self.display_production(prod)
            if prod.get('capitulo', '') is None:
                subitems = self.search_subproductions(prod)
            items.append(
                {
                    'sid': prod['id']['sid'],
                    'titulo': prod['tit'],
                    'sino': prod['sino'],
                    'dura': prod.get('dura', ''),
                    'foto': prod.get('foto', ''),
                    'anio': prod.get('an', ''),
                    'rate': prod.get('rProme', 3),
                    'subitems': subitems,
                }
            )
        return items

    def user_home(self, tipotira='all'):
        """Request a la Portada de cinear."""
        home_url = "{0}/home?perfil={1}".format(self.API_URI, self.perfil)
        r = self.session.get(home_url)
        jsonResponse = r.json()
        self.TIRAS = list(filter(lambda x: x['titulo'] != 'Estrenos', jsonResponse['tiras']))
        self.PRODS = jsonResponse['prods']

    def get_tiras(self, data, tipotira='all'):
        """
        Obtiene el contenido de una tira (seccion de la pagina principal)
        o varias.
        https://play.cine.ar/api/v1.7/home?perfil=5ad12b35189ad4579d2a881e&prods=30
        """
        prods = data['prods']
        if tipotira == 'all':
            tiras = list(
                filter(
                    lambda x: x['titulo'] != 'Estrenos en simultáneo al cine',
                    data['tiras']
                )
            )
        else:
            tiras = []
            for tira in tipotira.split(','):
                if not tira.strip() in self.TIRAS.keys():
                    print('El nombre de tira ingresado es incorrecto:', tira)
                    exit()

                tmp = list(filter(
                    lambda x: x['titulo'] != 'Estrenos en simultáneo al cine'
                    and x['titulo'] == self.TIRAS[tira.strip()], data['tiras']
                ))
                tiras.extend(tmp)

        items = []
        for tira in tiras:
            for conte in tira['conte']:
                subitems = []
                self.display_production(prods[conte], tira)
                if prods[conte].get('capitulo', '') is None:
                    subitems = self.search_subproductions(prods[conte])
                items.append(
                    {
                        'sid': prods[conte]['id']['sid'],
                        'titulo': prods[conte]['tit'],
                        'sino': prods[conte]['sino'],
                        'dura': prods[conte].get('dura', ''),
                        'foto': prods[conte].get('foto', ''),
                        'anio': prods[conte].get('an', ''),
                        'rate': prods[conte].get('rProme', 3),
                        'subitems': subitems,
                    }
                )

        return items

    def set_tira(self,tira_index):
        """
        Setea la tira a desplegar segun el indice pasado por parametro.
        """
        prods = self.PRODS

        items = []
        for conte in self.TIRAS[tira_index]['conte']:
            subitems = []
            if prods[conte].get('capitulo', '') is None:
                subitems = self.search_subproductions(prods[conte])
            items.append(
                {
                    'sid': prods[conte]['id']['sid'],
                    'titulo': prods[conte]['tit'],
                    'sino': prods[conte]['sino'],
                    'dura': prods[conte].get('dura', ''),
                    'foto': prods[conte].get('foto', ''),
                    'anio': prods[conte].get('an', ''),
                    'rate': prods[conte].get('rProme', 3),
                    'subitems': subitems,
                }
            )

        return items

    def user_info(self):
        """Informacion del Usuario."""
        user_info_url = '{0}/auth/user_info'.format(self.ID_URI)
        r = self.session.get(user_info_url)
        return r

    def user_pid(self):
        """Obtener el perfil del Usuario."""
        user_url = "{0}/user".format(self.API_URI)
        r = self.session.get(user_url)
        user = r.json()
        self.perfil = user['perfiles'][0]['id']

    def production_id(self, sid, source="INCAA"):
        """
        Obtener URL de produccion  con la info necesaria:
        source = "INCAA"
        sid = "xxxx"
        PID = perfil
        token = token
        """
        url = '{0}?s={1}&i={2}&p={3}&t={4}'.format(
            self.PLAYER_URL, source, sid, self.perfil, self.TOKEN
        )

        clave = source + sid + self.perfil + self.TOKEN + 'ARSAT'
        clave = clave.encode('utf-8')

        digest = hashlib.md5(clave).digest()
        digest_clave = base64.b64encode(digest)

        self.auth = digest_clave
        self.session.headers.update(self.get_headers())

        r = self.session.get(url)
        return r.json(), digest_clave

    def display_tiras(self, tira=None):
        if tira:
            for conte in self.TIRAS[tira]['conte']:
                self.display_production(self.PRODS[conte], self.TIRAS[tira]['titulo'])
        else:
            for i, tira in enumerate(self.TIRAS):
                print(":: {0} :: {1}".format(i, tira['titulo']))

    def display_production(self, prod, tira=None):
        """ Desplegar informacion de una produccion (contenido)."""
        if not self.TUI:
            return

        try:
            print(":: {0} :: {1}".format(prod['tit'].upper(), tira['titulo']))
        except Exception:
            print("{0} ".format(prod['tit'].upper()))

        print("{0} ".format(prod['sino']))

        try:
            print("SID: {0} - Duracion: {1} min - Fecha: {2}".format(
                prod['id']['sid'], prod['dura'], prod['an'])
            )
        except Exception:
            try:
                print("SID: {0} - Fecha: {1}".format(
                    prod['id']['sid'], prod['an'])
                )
            except Exception:
                print("SID: {0}".format(prod['id']['sid']))
        print("-"*80)

    def get_asociado(self, asociado):
        """Desplegar informacion de episodios de una serie."""
        item = {
            'titulo': asociado['tit'].capitalize(),
            'sid': asociado['sid'],
            'temp': asociado['tempo'],
            'capi': asociado['capi'],
        }
        if self.TUI:
            print("- S{2}E{3} - Titulo: {0} - SID: {1}".format(
                asociado['tit'].upper(),
                asociado['sid'],
                asociado['tempo'],
                asociado['capi'],
            ))
            print("-"*80)
        return item

    def parse_qualities(self, qualities_options):
        """Parsear la calidad de videos disponibles en la produccion."""
        qualities = {}
        state = 'quality'
        for qline in qualities_options:
            r = re.search(r',NAME="(\d+p)', qline)
            if r and state == 'quality':
                quality = r.group(1)
                state = 'pass'

            elif state == 'pass':
                state = 'read_chunk'

            elif state == 'read_chunk':
                qualities[quality] = qline.strip()
                state = 'quality'
        return qualities

    def get_video_quality(self, qualities, default_quality='720p'):
        """Funcion para elegir la calidad de video"""
        if self.config:
            default_quality = self.config['prefered_video_quality']
            for k, v in qualities.items():
                if k == default_quality:
                    return v
        return list(qualities.values())[0]

    def search_subproductions(self, prods):
        """
        Obtiene informacion de subproducciones.
        EJ: Capitulos de una serie.
        """
        serie_url = "{0}/INCAA/prod/{1}?perfil={2}".format(
            self.API_URI, prods['id']['sid'], self.perfil
        )
        r = self.session.get(
            serie_url
        )
        items = []
        try:
            for prod in r.json()['items']:
                items.append(self.get_asociado(prod))
        except Exception:
            pass
        return items

    def production_chuncks(self, data, digest_clave, play=True):
        """Obtener fragmentos de videos de la produccion."""
        self.items = []
        chuncks = data["url"].split('/')[2:9]
        chuncks_url = 'https://' + '/'.join(chuncks)

        r = self.session.get(data["url"])
        if r.status_code == 403 or r.status_code == 404:
            # Check if it is a serie ?
            prod = data['url'].split('/INCAA/')[1].split('/')[0]
            serie_url = "{0}/INCAA/prod/{1}?perfil={2}".format(
                self.API_URI, prod, self.perfil
            )
            r = self.session.get(
                serie_url
            )

            if r.status_code == 403 or r.status_code == 404:
                print(
                    "Fallo la busqueda de la produccion, o la misma es inexistente"
                )
                exit()

            items = []
            for prod in r.json()['items']:
                items.append(self.get_asociado(prod))
            self.items = items

        elif r.text:
            qualities_options = r.text.split()
            qualities_options = self.parse_qualities(qualities_options)
            video_quality = self.get_video_quality(qualities_options)

            data_url = chuncks_url + '/' + video_quality

            r = self.session.get(data_url)
            lines = r.text.split()

            title = data['title'] + ' ' + data.get('subtitle', '')
            self.download_chuncks(title, chuncks_url, lines, play)
            self.items = 0
        else:
            print("Fallo la busqueda de la produccion, o la misma es inexistente")
            exit(0)

    def download_chuncks(self, title, chuncks_url, chuncks, play=True):
        """Descarga de fragmentos de pelicula."""
        # file = open("movie.txt","w")
        name = title.lower().replace(' ', '_')+'.avi'

        if self.config and 'download_dir' in self.config:
            video_path = self.config['download_dir']
            name = os.path.join(video_path, name)
        else:
            name = os.path.join('', name)

        has_started = False

        i = 0
        for chunck in chuncks:
            if chunck.startswith("media_"):
                i = i+1

                urllib.request.urlretrieve(
                    "{0}/{1}\n".format(chuncks_url, chunck),
                    name+'.part'+str(i)
                )
                if not has_started:
                    has_started = True
                    with open(name, "ab") as myfile, \
                         open(name+'.part'+str(i), "rb") as file2:
                        myfile.write(file2.read())
                        os.remove(name+'.part'+str(i))

                    if play:
                        pprocess = self.start_playing(name)
                else:
                    with open(name, "ab") as myfile, \
                         open(name+'.part'+str(i), "rb") as file2:
                        myfile.write(file2.read())
                        os.remove(name+'.part'+str(i))
        try:
            pprocess.wait()
        except Exception:
            pass

    def start_playing(self, title):
        """Reproducir, llamando a proceso externo."""
        p = Popen(["xdg-open", title])
        return p


if __name__ == '__main__':
    args = docopt(__doc__, version='Cine.ar en consola v0.2')

    try:
        with open('../config.yaml', 'r') as ymlfile:
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

    cinear = CineAR(
        credentials={'email': email, 'password': passw},
        config=config,
        TUI=True
    )
    # User Auth
    cinear.auth_login()
    cinear.user_pid()

    # Parsing args
    if args['search'] or args['-s']:
        cinear.search(args['<string>'])

    elif args['play'] or args['-p']:
        SID = args['SID']
        data, digest_clave = cinear.production_id(SID, source='INCAA')
        cinear.production_chuncks(data, digest_clave)

    elif args['download'] or args['-d']:
        play = False
        SID = args['SID']
        data, digest_clave = cinear.production_id(SID, source='INCAA')
        cinear.production_chuncks(data, digest_clave, play)

    elif args['home'] or args['-H']:
        cinear.user_home()
        if not args['<tira>']:
            tira = ''
        else:
            tira = int(args['<tira>'])
        if cinear.TUI:
            cinear.display_tiras(tira)

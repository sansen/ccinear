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

from model.download import DownloadManager
from model.contents import ContentManager
from model.cache import CinearCache


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
        self.cm = ContentManager(self.TUI)
        self.dm = DownloadManager(self.config)
        self.cc = CinearCache()

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
        t = self.cc.get('token')
        h = self.cc.get('headers')
        if t and h:
            self.TOKEN = t
            self.session.headers.update(h)
            return

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

            # set to cache
            self.cc.set('token', self.TOKEN)
            self.cc.set('headers', self.get_headers())

        except Exception:
            print('Fallo la autenticacion')
            exit()

    def user_home(self, tipotira='all'):
        """Request a la Portada de cinear."""
        jsonResponse = self.cc.get('user_home')
        if not jsonResponse:
            home_url = "{0}/home?perfil={1}".format(self.API_URI, self.perfil)
            r = self.session.get(home_url)
            jsonResponse = r.json()
            # set to cache
            self.cc.set('user_home', jsonResponse)

        self.cm.set_content(jsonResponse)

    def user_info(self):
        """Informacion del Usuario."""
        user_info_url = '{0}/auth/user_info'.format(self.ID_URI)
        r = self.session.get(user_info_url)
        return r

    def user_pid(self):
        """Obtener el perfil del Usuario."""
        perfil = self.cc.get('perfil')
        if perfil:
            self.perfil = perfil
            return

        user_url = "{0}/user".format(self.API_URI)
        r = self.session.get(user_url)
        user = r.json()
        self.perfil = user['perfiles'][0]['id']
        # set to cache
        self.cc.set('perfil', self.perfil)

    def search_subproductions(self, API_URI, prods, session, perfil):
        """
        Obtiene informacion de subproducciones.
        EJ: Capitulos de una serie.
        """
        serie_url = "{0}/INCAA/prod/{1}?perfil={2}".format(
            API_URI, prods['id']['sid'], perfil
        )
        r = session.get(
            serie_url
        )
        return r.json()['items']

    def set_tira(self,tira_index):
        """
        Setea la tira a desplegar segun el indice pasado por parametro.
        """
        prods = self.cm.get_prods()
        tira = self.cm.get_tira_content(tira_index)

        items = []
        for conte in tira:
            subitems = []
            if prods[conte].get('capitulo', '') is None:
                subitems = []
                resp = self.search_subproductions(
                    self.API_URI, prods[conte],
                    self.session, self.perfil)
                try:
                    for prod in resp:
                        subitems.append(self.cm.get_asociado(prod))
                except Exception:
                    pass

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

    def search(self, term):
        """Buscar termino en cinear."""
        search_url = "{0}/search/{1}?cant=24&orden=rele&pag=1&perfil={2}".format(
            self.API_URI, term, self.perfil
        )
        r = self.session.get(search_url)

        items = []
        for prod in r.json()['prods']:
            subitems = []
            self.cm.display_production(prod)
            if prod.get('capitulo', '') is None:
                resp = self.search_subproductions(
                    self.API_URI, prod,
                    self.session, self.perfil)
                try:
                    for r in resp:
                        subitems.append(self.cm.get_asociado(r))
                except Exception:
                    pass

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

    def production_chuncks(self, data, digest_clave, sid, play=True):
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
                items.append(self.cm.get_asociado(prod))
            self.items = items

        elif r.text:
            qualities_options = r.text.split()
            qualities_options = self.dm.parse_qualities(qualities_options)
            video_quality = self.dm.get_video_quality(qualities_options)

            data_url = chuncks_url + '/' + video_quality

            r = self.session.get(data_url)
            lines = r.text.split()

            title = data['title'] + ' ' + data.get('subtitle', '')
            self.dm.download_chuncks(title, chuncks_url, lines, sid, play)
            self.items = 0
        else:
            print("Fallo la busqueda de la produccion, o la misma es inexistente")
            exit(0)

    def display_tiras(self, tira=False):
        self.cm.display_tiras(tira)

    def update_config(self, current_config):
        self.config.update(current_config)
        with open('config/config.yaml', 'w') as f:
            yaml.dump(self.config, f)

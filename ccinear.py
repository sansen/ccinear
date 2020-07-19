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
# Copyright 2019 Santiago Torres Batan

"""Console CineAR
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
  <tira>      Lista de tiras, respetando la siguiente designacion
      - tendencias: Tendencias,
      - novedades: Novedades de esta semana,
      - recomendadas: Películas recomendadas,
      - amor: Por amor,
      - mdq: MDQ Film Festival,
      - series_maraton: Maratón de series,
      - series_web: Series Web,
      - clasicos: Clásicos exclusivos,
      - animacion: Animación,
      - cortos: Cortos imperdibles,
      - musica: Música,
      - biopics: Biopics,
      - familia: Para ver en familia,
  E.g: ccinear.py -H 'tendencias, amor, mdq'
"""

import os
import re
import yaml
import base64
import hashlib
import requests
import urllib.request

from getpass import getpass
from docopt import docopt
from subprocess import Popen


class CineAR:
    def __init__(self, credentials, config):
        self.credentials = credentials
        self.config = config
        self.ID_URI = "https://id.cine.ar/v1.5"
        self.API_URI = "https://play.cine.ar/api/v1.7"
        self.PLAYER_URL = "https://player.cine.ar/odeon/"

        self.TOKEN = None
        self.auth = None

        self.TIRAS = {
            'tendencias': 'Tendencias',
            'novedades': 'Novedades de esta semana',
            'recomendadas': 'Películas recomendadas',
            'amor': 'Por amor',
            'mdq': 'MDQ Film Festival',
            'series_maraton': 'Maratón de series',
            'series_web': 'Series Web',
            'clasicos': 'Clásicos exclusivos',
            'animacion': 'Animación',
            'cortos': 'Cortos imperdibles',
            'musica': 'Música',
            'biopics': 'Biopics',
            'familia': 'Para ver en familia',
        }

        self.session = requests.Session()

    def get_headers(self, token=None, auth=None):
        """Obtener header para request http"""
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
                #headers=get_headers()
            )
            self.TOKEN = r.json()['token']
            self.session.headers.update(self.get_headers())

        except Exception:
            print('Fallo la autenticacion')
            exit()


    def search(self, term, perfil):
        """Buscar termnio en cinear"""
        search_url = "{0}/search/{1}?cant=24&orden=rele&pag=1&perfil={2}".format(
            self.API_URI, term, perfil
        )
        r = self.session.get(search_url)

        for prod in r.json()['prods']:
            self.display_production(prod)
            print("-"*80)


    def user_home(self, perfil, tipotira='all'):
        """HOME: Portada de cinear"""
        home_url = "{0}/home?perfil={1}".format(self.API_URI, perfil)
        r = self.session.get(home_url)
        self.get_tiras(r.json(), tipotira)


    def get_tiras(self, data, tipotira='all'):
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

            for tira in tiras:
                print(tira['titulo'].upper())
                print("="*80)
                for conte in tira['conte']:
                    self.display_production(prods[conte], tira)
                    print("-"*80)


    def user_info(self):
        """Informacion del Usuario."""
        user_info_url = '{0}/auth/user_info'.format(self.ID_URI)
        r = self.session.get(user_info_url)
            
        return perfil


    def user_pid(self):
        """Obtener el perfil del Usuario."""
        user_url = "{0}/user".format(self.API_URI)
        r = self.session.get(user_url)
        user = r.json()
        perfil = user['perfiles'][0]['id']

        return perfil


    def production_id(self, sid, perfil, source="INCAA"):
        """
        Obtener URL de produccion  con la info necesaria:
        source = "INCAA"
        sid = "xxxx"
        PID = perfil
        token = token
        """
        url = '{0}?s={1}&i={2}&p={3}&t={4}'.format(
            self.PLAYER_URL, source, sid, perfil, self.TOKEN
        )

        clave = source + sid + perfil + self.TOKEN + 'ARSAT'
        clave = clave.encode('utf-8')

        digest = hashlib.md5(clave).digest()
        digest_clave = base64.b64encode(digest)

        self.auth = digest_clave
        self.session.headers.update(self.get_headers())

        r = self.session.get(url)
        return r.json(), digest_clave


    def display_production(self, prod, tira=None):
        """ Desplegar informacion de produccion"""
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


    def display_asociado(self, asociado):
        """Desplegar informacion de episodios de una serie."""
        print("- S{2}E{3} - Titulo: {0} - SID: {1}".format(
            asociado['tit'].upper(),
            asociado['sid'],
            asociado['tempo'],
            asociado['capi'],
        ))


    def parse_qualities(self, qualities_options):
        """Parsear la calidad de videos disponibles en la produccion"""
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


    def production_chuncks(self, data, digest_clave, play=True):
        """Obtener fragmentos de videos de la produccion"""
        chuncks = data["url"].split('/')[2:9]
        chuncks_url = 'https://' + '/'.join(chuncks)

        r = self.session.get(data["url"])

        if r.status_code == 403 or r.status_code == 404:
            # Check if it is a serie ?
            prod = data['url'].split('/INCAA/')[1].split('/')[0]
            serie_url = "{0}/INCAA/prod/{1}?perfil={2}".format(
                self.API_URI, prod, perfil
            )
            r = session.get(
                serie_url
            )

            if r.status_code == 403 or r.status_code == 404:
                print(
                    "Fallo la busqueda de la produccion, o la misma es inexistente"
                )
                exit()

            for prod in r.json()['items']:
                self.display_asociado(prod)

        elif r.text:
            qualities_options = r.text.split()
            qualities_options = self.parse_qualities(qualities_options)

            video_quality = self.get_video_quality(qualities_options)

            data_url = chuncks_url + '/' + video_quality

            r = self.session.get(data_url)
            lines = r.text.split()

            self.download_chuncks(data["title"], chuncks_url, lines, play)

        else:
            print("Fallo la busqueda de la produccion, o la misma es inexistente")
            exit(0)


    def download_chuncks(self, title, chuncks_url, chuncks, play=True):
        """Descarga de fragmentos de pelicula."""
        # file = open("movie.txt","w")
        name = title.lower().replace(' ','_')+'.avi'
    
        if self.config:
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
                    "{0}/{1}\n".format(chuncks_url, chunck), name+'.part'+str(i)
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

    def start_playing(title):
        """Reproducir, llamando a proceso externo."""
        p = Popen(["mpv", title])
        return p


if __name__ == '__main__':
    args = docopt(__doc__, version='Cine.ar en consola v0.1')

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


    cinear = CineAR(
        credentials={'email':email, 'password': passw},
        config=config
    )
    # User Auth
    cinear.auth_login()
    perfil = cinear.user_pid()

    # Parsing args
    if args['search'] or args['-s']:
        cinear.search(args['<string>'], perfil)

    elif args['play'] or args['-p']:
        SID = args['SID']
        data, digest_clave = cinear.production_id(SID, perfil, source='INCAA')
        cinear.production_chuncks(data, digest_clave)

    elif args['download'] or args['-d']:
        play = False
        SID = args['SID']
        data, digest_clave = cinear.production_id(SID, perfil, source='INCAA')
        cinear.production_chuncks(data, digest_clave, play)

    elif args['home'] or args['-H']:
        if not args['<tira>']:
            tira = 'all'
        else:
            tira = args['<tira>']
        cinear.user_home(perfil, tira)

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


class ContentManager:
    """
    Clase que maneja los contenidos, es decir las secciones
    las producciones, su metadata y las producciones asociadas
    """

    def __init__(self, tui):
        self.TUI = tui

    def set_content(self, jsonResponse):
        self.TIRAS = list(filter(
            lambda x: x['titulo'] != 'Estrenos', jsonResponse['tiras']
        ))
        self.PRODS = jsonResponse['prods']

    def get_prods(self):
        return self.PRODS

    def get_tira_content(self, tira_index):
        return self.TIRAS[tira_index]['conte']

    def display_tiras(self, tira):
        if tira is not False:
            for conte in self.TIRAS[tira]['conte']:
                self.display_production(
                    self.PRODS[conte], self.TIRAS[tira]['titulo']
                )
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
            try:                print("SID: {0} - Fecha: {1}".format(
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

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
from PySide2 import QtWidgets, QtCore


class DownloadManager:
    """
    Clase que maneja las descargas efectivas de los contenidos.
    Ademas selecciona la calidad que mejor aplique para la descarga
    """

    def __init__(self, config):
        self.config = config
        self.current_downloads = {}

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
        if self.config and 'prefered_video_quality' in self.config:
            default_quality = self.config['prefered_video_quality']

        # print(qualities.items())
        for k, v in qualities.items():
            if k == default_quality:
                return v
        return list(qualities.values())[0]

    def download_chuncks(self, title, chuncks_url, chuncks, sid, play=True):
        """Descarga de fragmentos de pelicula."""
        # file = open("movie.txt","w")
        name = title.lower().replace(' ', '_')+'.avi'

        if self.config and 'download_dir' in self.config:
            video_path = self.config['download_dir']
            name = os.path.join(video_path, name)
        else:
            name = os.path.join('', name)

        # check current downloads:
        if sid not in self.current_downloads:
            self.current_downloads[sid] = {
                'initial_chunck': 0,
                'has_started': False,
                'paused': False,
                'downloading': False,
                'progress': 0,
                'completed': False
            }

        if play and self.current_downloads[sid]['downloading'] \
           and not self.current_downloads[sid]['paused']:
            pprocess = self.start_playing(name)

        self.current_downloads[sid]['paused'] = False
        initial_chunck = self.current_downloads[sid]['initial_chunck']
        has_started = self.current_downloads[sid]['has_started']
        i = initial_chunck
        total = len(chuncks)

        for chunck in chuncks[initial_chunck:]:
            i = i+1
            self.current_downloads[sid]['initial_chunck'] = i
            self.current_downloads[sid]['downloading'] = True
            self.current_downloads[sid]['progress'] = i/total

            if chunck.startswith("media_"):
                urllib.request.urlretrieve(
                    "{0}/{1}".format(chuncks_url, chunck),
                    name+'.part'
                )
                if not has_started:
                    has_started = True
                    self.current_downloads[sid]['has_started'] = has_started

                    with open(name, "ab") as myfile, \
                         open(name+'.part', "rb") as file2:
                        myfile.write(file2.read())
                        os.remove(name+'.part')

                    if play:
                        pprocess = self.start_playing(name)
                else:
                    with open(name, "ab") as myfile, \
                         open(name+'.part', "rb") as file2:
                        myfile.write(file2.read())
                        os.remove(name+'.part')

                if self.current_downloads[sid]['paused'] == True:
                    break

        self.current_downloads[sid]['completed'] = True
        try:
            pprocess.wait()
        except Exception:
            pass

    def start_playing(self, title):
        """Reproducir, llamando a proceso externo."""
        p = Popen(["xdg-open", title])
        return p

    def pause_download(self, sid):
        self.current_downloads[sid]['paused'] = True

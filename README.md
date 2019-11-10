
# Table of Contents

1.  [INFORMACION GENERAL](#orgc2acf3c)
2.  [INSTALACION](#org6169e9a)
3.  [CONFIGURACION](#org707eebd)
4.  [USO](#org19a6af0)



<a id="orgc2acf3c"></a>

# INFORMACION GENERAL

Maneja la interfaz de cine.ar desde la consola,
realiza backups de tus peliculas favoritas, miralas offline.

**Disclaimer**: No dejes de utilizar cine.ar y apoyar
el desarrollo del cine argentino.


<a id="org6169e9a"></a>

# INSTALACION

Crear un entorno virtual, instala las dependencias con pip y usalo

    $ virtualenv --python=python3 cinear
    $ cd cinear
    $ source bin/activate
    $ pip install -r requeriments.txt
    $ python ./ccinear.py -H

Dependencias adicionales:

-   Utiliza mpv para reproducir los videos.


<a id="org707eebd"></a>

# CONFIGURACION

Se puede definir un archivo de configuracion:

'config.yaml'

en el mismo directorio donde se encuentra el script, con el siguiente contenido:

    email: mail@servider.com
    prefered_video_quality: '480p'
    download_directory: /ruta/de/descarga/

-   donde 'email' es el mail del usuario de cinear,
-   donde 'download\_directory', es el path absoluto donde descargar los archivos. Por defecto sera en el mismo directorio del script.
-   donde 'prefered\_video\_quality' la calidad preferida para las descargas o visualizaciones. Los posibles valores son: 240p, 360p, 480p, 720p, etc. Por defecto sera 720p

Si no existe el archivo de configuracion se tomaran valores por defecto y sera necesario especificar las credenciales de cine.ar en cada consulta.


<a id="org19a6af0"></a>

# USO

Cada pelicula tiene un SID, con el cual la podes referenciar.
El SID se muestra en la informacion desplegada en consola cuando busca la pelicula o cuando ejecutas con -H.

    Usage:
      ccinear.py [--user=<user>] [--passw] (play | -p) SID
      ccinear.py [--user=<user>] [--passw] (download | -d) SID
      ccinear.py [--user=<user>] [--passw] (home | -H) [<tira>]
      ccinear.py [--user=<user>] [--passw] (search | -s) <string>
      ccinear.py (-h | --help)
      ccinear.py --version
    
    Options:
      -h --help   Show this screen.
      version   Show version.
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

Ejemplo de uso:

Ver portada de cinear (Informacion de contenido separados por seccion)

    python ccinear.py -H 'Series Web'

Buscar un pelicula en partiular, serie o actor|actriz, mejorando el output
con colores.

    python ccinear.py -s 'Cetaceos' | grep -E --color=auto '^|^SID:[ 0-9]+|^[A-Z ,:.]*$'

    python ccinear.py -H 'Novedades de esta semana' | grep -E --color=auto '^|^SID:[ 0-9]+|^::[A-Z :,.]*::'

-   TODO: Agregar colores y paginacion.


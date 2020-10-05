
# Contenidos

1.  [Informacion general](#org8bad059)
2.  [Instalacion](#org6f494c9)
3.  [Configuracion](#org320a85b)
4.  [Uso](#org81bb7e4)



<a id="org8bad059"></a>

# Informacion general

Maneja la interfaz de cine.ar desde la consola,
realiza backups de tus peliculas favoritas, miralas offline.

**Disclaimer**: No dejes de utilizar cine.ar y apoyar
el desarrollo del cine argentino.


<a id="org6f494c9"></a>

# Instalacion

Crear un entorno virtual, instala las dependencias con pip y usalo

Clonar el repositorio:

    $ git clone https://github.com/sansen/ccinear.git

Creacion de Virtualenv:

    $ virtualenv --python=python3 cinear
    $ cd cinear
    $ source bin/activate
    $ pip install -r requeriments.txt
    $ python ./ccinear.py --user=<email>@<server>.com -H

Dependencias adicionales:

-   Utiliza mpv para reproducir los videos.


<a id="org320a85b"></a>

# Configuracion

Se puede definir un archivo de configuracion:

'../config.yaml'

en directorio raiz de donde se encuentra el script, con el siguiente contenido:

    email: mail@servider.com
    prefered\_video\_quality: '480p'
    download\_directory: /ruta/de/descarga/

-   donde 'email' es el mail del usuario de cinear,
-   donde 'download\_dir', es el path absoluto donde descargar los archivos. Por defecto sera en el mismo directorio del script.
-   donde 'prefered\_video\_quality' la calidad preferida para las descargas o visualizaciones. Los posibles valores son: 240p, 360p, 480p, 720p, etc. Por defecto sera 720p

Si no existe el archivo de configuracion se tomaran valores por defecto y sera necesario especificar las credenciales de cine.ar en cada consulta.


<a id="org81bb7e4"></a>

# Uso

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
       - novedades: Novedades de la semana,
       - juventudes: Juventudes en Movimiento,
       - estrenos: Jueves Estreno,
       - ficmp: Especial Festival Internacional de Cine de Mar del Plata,
       - recomendadas: Películas recomendadas,
       - lomasvisto: Lo más visto,
       - series: Series imperdibles,
       - cortos: Los cortos más populares,
       - documentales: Documentales,
       - biopics: Biopics,
       - mayores: Apto para mayores,
       - clasicos: Clásicos exclusivos,
       - breves: Historias Breves,
       - diversidad: Cine, diversidad y géneros
      E.g: ccinear.py -H 'novedades, documentales'

Ejemplo de uso:

Ver pelicula

    python ccinear.py -p 5717

Descarga pelicula

    python ccinear.py -d 5717

Ver portada de cinear (Informacion de contenido separados por seccion)

    python ccinear.py -H 'Series Web'

Buscar un pelicula en partiular, serie o actor|actriz, mejorando el output
con colores.

    python ccinear.py -s 'Cetaceos' | grep -E --color=auto '^|^SID:[ 0-9]+|^[A-Z ,:.]*$'

    python ccinear.py -H 'novedades' | grep -E --color=auto '^|^SID:[ 0-9]+|^::[A-Z :,.]*::'


# Table of Contents

1.  [INFORMACION GENERAL](#org937142a)
2.  [INSTALACION](#org80e7521)
3.  [CONFIGURACION](#orgcbbd2b0)
4.  [USO:](#org76aecb7)



<a id="org937142a"></a>

# INFORMACION GENERAL

Maneja la interfaz de cine.ar desde la consola,
realiza backups de tus peliculas favoritas, miralas offline.

**Disclaimer**: No dejes de utilizar cine.ar y apoyar
el desarrollo del cine argentino.

Cada pelicula tiene un SID, con el cual la podes referenciar.
El SID se muestra en la informacion desplegada en consola cuando 
busca la pelicula o cuando ejecutas con -H.


<a id="org80e7521"></a>

# INSTALACION

Crear un entorno virtual, instala las dependencias con pip y usalo

    $ virtualenv --python=python3 cinear
    $ cd cinear
    $ source bin/activate
    $ pip install -r requeriment.txt
    $ python ./ccinear.py -H

Dependencias adicionales:

-   Utiliza mpv para reproducir los videos.


<a id="orgcbbd2b0"></a>

# CONFIGURACION

Se puede definir un archivo de configuracion:
'config.yaml'
en el mismo directorio donde se encuentra el script, con el siguiente
contenido:

email: mail@servider.com
prefered<sub>video</sub><sub>quality</sub>: '480p'
download<sub>directory</sub>: *ruta/de/descarga*

-   donde 'email' es el mail del usuario de cinear,
-   donde 'download<sub>directory</sub>', es el path absoluto donde descargar

los archivos. Por defecto sera en el mismo directorio del 
script. 

-   donde 'prefered<sub>video</sub><sub>quality</sub>' la calidad preferida para las descargas

o visualizaciones. Los posibles valores son:
240p, 360p, 480p, 720p, etc. Por defecto sera 720p

Si no existe el archivo de configuracion se tomaran valores por defecto
y sera necesario especificar las credenciales de cine.ar en cada consulta.


<a id="org76aecb7"></a>

# USO:

No te olvides de agregar tus credenciales de cine.ar al script.
-TODO: Credenciales por medio de configuracion.

      cinear.py (play | -p) SID
      cinear.py (download | -d) SID
      cinear.py (home | -H) [<tira>] Ejemplo: python ccinear.py -H 'Series Web'
      cinear.py (search | -s) <string>
      cinear.py (-h | --help)
      cinear.py --version
    
    Options:
      -h --help   Show this screen.
      --version   Show version.
      SID         INCAA, Produccion ID
      <string>    String to search for
      <tira>      Nombre de la Tira

Ejemplo de uso:

---

Ver portada de cinear (Informacion de contenido separados por seccion)

    python ccinear.py -H 'Series Web'

Buscar un pelicula en partiular, serie o actor|actriz, mejorando el output
con colores.

    python ccinear.py -s 'Cetaceos' | grep -E --color=auto '^|^SID:[ 0-9]+|^[A-Z ,:.]*$'

    python ccinear.py -H 'Novedades de esta semana' | grep -E --color=auto '^|^SID:[ 0-9]+|^::[A-Z :,.]*::'

-   TODO: Agregar colores y paginacion.


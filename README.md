
# Table of Contents

1.  [Informacion general](#orgd520ae8)
2.  [Instalacion](#org5133f8e)
3.  [Configuracion](#orgd00ef8b)



<a id="orgd520ae8"></a>

# Informacion general

Maneja la interfaz de cine.ar desde la consola,
realiza backups de tus peliculas favoritas, miralas offline.

**Ahora tambien con Interfaz Grafica.**

**Disclaimer**: No dejes de utilizar cine.ar y apoyar
el desarrollo del cine argentino.


<a id="org5133f8e"></a>

# Instalacion

Crear un entorno virtual, instala las dependencias con pip y usalo.

Clonar el repositorio:

    $ git clone https://github.com/sansen/ccinear.git

Creacion de Virtualenv:

    $ virtualenv --python=python3 cinear
    $ cd cinear
    $ source bin/activate
    $ pip install -r requeriments.txt
    $ python ./cinear-qt.py --user=<email>@<server>.com

Dependencias adicionales:

-   Utiliza xdg-open para abrir el reproductor de video que tengas instalado.

(Se recomienda mpv)


<a id="orgd00ef8b"></a>

# Configuracion

Se puede definir un archivo de configuracion:

'config.yaml'

en el mismo directorio donde se encuentra el script, con el siguiente contenido:

    email: mail@servider.com
    prefered_video_quality: '480p'
    download_dir: /ruta/de/descarga/

-   donde 'email' es el mail del usuario de cinear,
-   donde 'download\\<sub>directory</sub>', es el path absoluto donde descargar los archivos. Por defecto sera en el mismo directorio del script.
-   donde 'prefered\\<sub>video</sub>\\<sub>quality</sub>' la calidad preferida para las descargas o visualizaciones. Los posibles valores son: 240p, 360p, 480p, 720p, etc. Por defecto sera 720p

Si no existe el archivo de configuracion se tomaran valores por defecto.


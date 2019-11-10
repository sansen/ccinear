
# Table of Contents

1.  [INFORMACION GENERAL](#orgda6cef6)
2.  [INSTALACION](#orgdef2834)
3.  [USO:](#org3c6715a)



<a id="orgda6cef6"></a>

# INFORMACION GENERAL

Maneja la interfaz de cine.ar en desde la consola,
realiza backups de tus peliculas favoritas, miralas offline.

**Disclaimer**: No dejes de utilizar cine.ar y apoyar
el desarrollo del cine argentino.

Cada pelicula tiene un SID, con el cual la podes referenciar.
El SID se muestra en la informacion desplegada en consola cuando 
busca la pelicula o cuando ejecutas con -H.

Recomienda mpv para reproducir los videos 


<a id="orgdef2834"></a>

# INSTALACION

Crear un entorno virtual, instala las dependencias con pip y usalo

    $ virtualenv --python=python3 cinear
    $ cd cinear
    $ source bin/activate
    $ pip install -r requeriment.txt
    $ python ./ccinear.py -H


<a id="org3c6715a"></a>

# USO:

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

    python ccinear.py -H 'Series Web'

Para mejorar el oputput colores:

    python ccinear.py -H 'Novedades de esta semana' | grep -E --color=auto '^|^SID:[ 0-9]+|^[A-Z ]*'

-   TODO: Agregar colores y paginacion.


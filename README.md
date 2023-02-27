# HashTable API
HashTable es una API que permite cifrar valores y buscarlos según tres tipos de formato diferentes. Dado que descifrar un valor de estos es casi imposible, también es cierto que puede tener vulnerabilidades, etc. El objetivo de la API es guardar palabras cifradas en los tres formatos de cifrado elementales (MD5, SHA1, SHA256), de tal modo que cuando un usuario busque un valor a descifrar, ya estaría descifrado. De forma inversa, cuando un usuario quiere cifrar un valor, la propia API aprovecha para alimentarse, alojando el dato si no existe. Cuando se construye la base, se puede importar unas palabras iniciales, pero con el paso del tiempo la tabla va cogiendo forma.

En lo que se refiere a MD5, se puede considerar que es el cifrado inicial, aunque haya otros, pero este es el más conocido. Sin embargo, unos estudios demostraron que existían posibilidades de vulnerabilidad, tanto de choque (posible repetición de datos diferentes) como de obtención (descifrado de la palabra). Por eso, surgió SHA1 y SHA2, cuyos bits eran muchos mayores que los de MD5. Algunas alternativas para la vulnerabilidad de MD5 en cuestiones de descifrado es cifrar en dos ocasiones la clave. En la lista siguiente se observa la cantidad de caracteres que se compone cada clave:

 - MD5: 32 caracteres
 - SHA1: 40 caracteres
 - SHA2: para el formato 256, 64 caracteres

En definitiva, esto es un resumen acerca de los tipos de cifrado. Detrás de todo esto existe una gran historia y controversia sobre cuál es el tipo de cifrado más seguro.


## Creación de la base de datos (MySQL)

1. Abrir el archivo _Instalación.sql_
2. Abrir una consola de MySQL
3. Copiar el contenido del archivo y pasarlo a la consola


## Instalación

1. Creación del entorno virtual, con el nombre de *env*:
```bash
python -m venv env
```

2. Activar el entorno virtual:
```bash
call env/scripts/activate
```

3. Tras haber activado el entorno virtual, instalar las librerías:
```bash
pip install -r requirements.txt
```

4. Ejecución de la API en modo de depuración:
```bash
flask --app application.py --debug run
```

## Librerías
- flask: creación de la API
- flask_cors: permitir llamadas desde accesos desconocidos, configuración de las políticas
- requests: gestionar datos pasados como argumentos por el POST, PUT, DELETE o el GET
- pymysql: conexión con la base, ejecución de consultas, llamadas, etc.
- qrcode: utilizado para generar QR

## Establecer la terminal por defecto la de CMD
 1. CTRL + SHIFT + P y escribir "Terminal: Select Default Profile"
 2. Seleccionar la opción de Command Prompt


## Ejecución
Abrir CMD y ejecutar el archivo _run.bat_:
```bash
call run
```
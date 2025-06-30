import requests
import time
import mysql.connector

# Conexión a la base de datos MySQL
db = mysql.connector.connect(
    host= 'localhost',
    user= 'root',
    password= '',
    database= 'github_info'
)

cursor = db.cursor() # Crea un cursor para ejecutar consultas SQL

# Solicita al usuario el nombre de GitHub a escanear inicialmente
user = input("Ingrese el nombre del usuario GIT: ")

# Verifica si un usuario ya existe en la tabla 'usuarios_leidos' de la base de datos
def existeUsuarioDB(user, conexion_cursor):
    conexion_cursor.execute("SELECT nombre_usuario FROM usuarios_leidos WHERE nombre_usuario = %s", (user,))
    dato = conexion_cursor.fetchone() # Obtiene el primer resultado
    return dato is not None # Retorna True si el usuario existe, False si no

# Obtiene repositorios y seguidores de un usuario de GitHub y los guarda en la base de datos
def ingresarDatosDB(user, conexion_cursor):
    url = f"https://api.github.com/users/{user}" # URL base para la API de GitHub
    
    # Obtiene y guarda los repositorios del usuario
    parametros = {"sort": "created", "direction": "desc"} # Parámetros para ordenar repositorios
    res_repos = requests.get(url+"/repos", params=parametros) # Realiza la solicitud
    if res_repos.status_code == 200: # Si la solicitud fue exitosa
        repositorios = res_repos.json() # Parsea la respuesta JSON

        for repo in repositorios:
            datos = (repo['owner']['login'], repo['name'], repo['html_url'], repo['created_at'])
            conexion_cursor.execute("INSERT INTO datos_repo (usuario, repo_nombre, repo_url, fecha_creacion) VALUES (%s, %s, %s, %s)", datos) # Inserta en la DB
            db.commit() # Guarda los cambios
    else:
        print(f"Error al obtener repositorios: {res_repos.status_code}") # Muestra error HTTP

    # Obtiene y guarda los seguidores del usuario
    res_followers = requests.get(url+"/followers") # Realiza la solicitud
    if res_followers.status_code == 200: # Si la solicitud fue exitosa
        seguidores = res_followers.json() # Parsea la respuesta JSON

        for seguidor in seguidores:
            datos = (user, seguidor['login'], seguidor['type'], seguidor['html_url'])
            conexion_cursor.execute("INSERT INTO datos_followers (usuario, seguidor, tipo, html_url) VALUES (%s, %s, %s, %s)", datos) # Inserta en la DB
            db.commit() # Guarda los cambios
    else:
        print(f"Error al obtener seguidores: {res_followers.status_code}") # Muestra error HTTP

# Gestiona el proceso de escanear o re-escanear un usuario de GitHub
def gestionarUsuarioGit():
    global user # Permite usar y modificar la variable 'user'
    while True:
        if user.strip() != '': # Si el nombre de usuario no está vacío
            if not existeUsuarioDB(user, cursor): # Si el usuario NO existe en la DB
                cursor.execute("INSERT INTO usuarios_leidos (nombre_usuario) VALUES (%s)", (user,)) # Inserta el usuario
                db.commit()
                ingresarDatosDB(user, cursor) # Ingresa sus datos de GitHub
                print(f"Datos de GitHub cargados exitosamente para: {user}.")
                break
            else: # Si exite el usuario es por que ya fue escaneardo, escanearlo nuevamente creara duplicados de los datos
                # Lo ideal seria comparar todos valores de la base de datos con los obtenidos de la consulta de API y agregar los nuevos si exitieran, sin embargo la no es e objetivo de esta Actividad. en este caso solo se eliminan y luego se vuelven a cargar
                print("Este usuario ya fue escaneado con anterioridad.")
                select= input("¿Quieres re-escanear? (s/n)\nLos datos existentes para este usuario serán eliminados.\n> ")
                while True:
                    if select.lower() == "s": # Si el usuario quiere re-escanear
                        # Elimina los datos existentes del usuario en todas las tablas
                        cursor.execute("DELETE FROM usuarios_leidos WHERE nombre_usuario = %s", (user,))
                        db.commit()
                        cursor.execute("DELETE FROM datos_repo WHERE usuario = %s", (user,))
                        db.commit()
                        cursor.execute("DELETE FROM datos_followers WHERE usuario = %s", (user,))
                        db.commit()
                        ingresarDatosDB(user, cursor) # Vuelve a ingresar los datos
                        print("Se cargaron los nuevos datos.")
                        break
                    elif select.lower() == "n": # Si el usuario no quiere re-escanear
                        print("Operación cancelada. Puedes continuar.")
                        break
                    else: # Si la respuesta es inválida
                        select= input("Respuesta no válida. ¿Quieres re-escanear? s/n\n> ")
                break
        else:
            print("¡Ingrese un nombre de usuario válido!")
            user = input("Ingrese el nombre del usuario GIT: ") # Pide un nombre no vacío

# Llama a la función principal para gestionar el usuario inicial
gestionarUsuarioGit() 

# Bucle principal del menú de opciones
while True:
    select = input("\n¿Qué deseas mirar? -> (repos/followers)\nCambiar Usuario -> user\tPara salir -> salir\n\nIngrese valor: ")

    if select.lower() == "repos": # Muestra los repositorios del usuario
        print("\nResultado de repositorios:\n")
        cursor.execute("SELECT repo_nombre, repo_url, fecha_creacion FROM datos_repo WHERE usuario = %s", (user,))
        for fila in cursor.fetchall():
            print(f"  {fila[0]}\n   Fecha de Creación:\t{fila[2]}\n   URL de Repositorio:\t{fila[1]}\n")
        
    elif select.lower() == "followers": # Muestra los seguidores del usuario
        print("\nResultado de seguidores:\n")
        cursor.execute("SELECT seguidor, tipo, html_url FROM datos_followers WHERE usuario = %s", (user,))
        print(f"{'Nombre':<16}{'Cuenta tipo':<12}\tURL de Usuario\n")
        for fila in cursor.fetchall():
            print(f"{fila[0]:<15} {fila[1]:<12}\t{fila[2]}")

    elif select.lower() == "user": # Permite cambiar de usuario de GitHub
        user = input("\nIngrese el nombre del nuevo usuario GIT: ")   
        gestionarUsuarioGit() # Vuelve a ejecutar la gestión de usuario para el nuevo nombre
        
    elif select.lower() == "salir": # Sale del programa
        print("Saliendo...")
        break
    else:
        print("\n-> Ingrese un valor válido (repos - followers - user - salir)")

# Cierra la conexión a la base de datos antes de finalizar
cursor.close()
db.close()

# Mensaje de despedida con temporizador
for x in range(3):
    time.sleep(0.5)
    print(f"Saliendo.. {3-x}")
print("¡Adiós! :D")
time.sleep(0.5)
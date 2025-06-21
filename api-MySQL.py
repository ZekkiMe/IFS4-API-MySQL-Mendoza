import requests
import time
import mysql.connector

# SE CONECTA A LA BASE DE DATOS
db = mysql.connector.connect(
    host= 'localhost',
    user= 'root',
    password= '',
    database= 'github_info'
)

cursor = db.cursor() # Se define el cursor, el cual se utilizará para ejecutar las sentencias SQL 

user = input("Ingrese el nombre del usuario GIT: ") # Se define por primera vez el Usuario a escanear

# Esta funcion pregunta "este usuario exite en la tabla usuarios_leidos de la base de datos?"  devuelve True en casi de que exita y False en caso de que no
def existeUsuarioDB(user, conexion_cursor):
    conexion_cursor.execute("SELECT nombre_usuario FROM usuarios_leidos")
    datos = conexion_cursor.fetchall()
    if len(datos) != 0:
        for dato in datos:
            if user in dato:
                return True
            else:
                return False
    else:
        return False

# Esta funcion Obtiene los repositorios y seguidores de un usuario de GitHub y los inserta en la base de datos. 
def ingresarDatosDB(user, conexion_cursor):
    # se setea la URL que se utilizará para la consulta de API
    url = f"https://api.github.com/users/{user}" 
    #--------Se obtiene los repositorios del Usuario ingresado
    parametros = {"sort": "created", "direction": "desc"}
    res_repos = requests.get(url+"/repos", params=parametros)
    if res_repos.status_code == 200:
        repositorios = res_repos.json()
        
        for repo in repositorios:
            datos = (repo['owner']['login'], repo['name'], repo['html_url'], repo['created_at'])
            conexion_cursor.execute("INSERT INTO datos_repo (usuario, repo_nombre, repo_url, fecha_creacion) VALUES (%s, %s, %s, %s)", datos)
            db.commit()

    else:
        print(f"Error: {res_repos.status_code}")

    #--------Se obtiene los seguidores del Usuario ingresado
    res_followers = requests.get(url+"/followers")
    if res_followers.status_code == 200:
        seguidores = res_followers.json()

        for seguidor in seguidores:
            datos = (user, seguidor['login'], seguidor['type'], seguidor['html_url'])
            conexion_cursor.execute("INSERT INTO datos_followers (usuario, seguidor, tipo, html_url) VALUES (%s, %s, %s, %s)", datos)
            db.commit()
    else:
        print(f"Error: {res_followers.status_code}")


# Esta funcion estiona el flujo de trabajo para escanear o re-escanear un usuario de GitHub.
def gestionarUsuarioGit():
    global user
    while True:
        # En este if se busca que el valor ingresado no sea vacio, sino vuelve a preguntar por el nombre
        if user != '':

            # Se intenta verificar si el usuario existe o no exite en la base de datos
            if not existeUsuarioDB(user, cursor):
                cursor.execute("INSERT INTO usuarios_leidos (nombre_usuario) VALUES (%s)", (user,))
                db.commit()

                ingresarDatosDB(user, cursor)
                break
            # Si exite el usuario es por que ya fue escaneardo, escanearlo nuevamente creara duplicados de los datos
            else: 
                # Lo ideal seria comparar todos valores de la base de datos con los obtenidos de la consulta de API y agregar los nuevos si exitieran, sin embargo la no es e objetivo de esta Actividad. en este caso solo se deletean y luego se vuelven a cargar
                print("Este usuario ya fue escaneado con anterioridad")
                select= input("Quieres re-escanear? (s/n)\ndatos borrados de git, tambien se borraran de la base de datos\n> ")
                while True:
                    if select.lower() == "s":
                        cursor.execute("DELETE FROM usuarios_leidos WHERE usuario = %s", (user,))
                        db.commit()
                        cursor.execute("DELETE FROM datos_repo WHERE usuario = %s", (user,))
                        db.commit()
                        cursor.execute("DELETE FROM datos_followers WHERE usuario = %s", (user,))
                        db.commit()

                        ingresarDatosDB(user, cursor)
                        print("se cargaron los nuevos Datos")
                        break
                    elif select.lower() == "n":
                        break
                    else:
                        select= input("Respuesta no valida! Quieres re-escanear? s/n")

                break
        else:
            print("Ingrese un nombre!")
            user = input("Ingrese el nombre del usuario GIT: ") # Reintena obtener un valor no vacio en user

# Se llama pro primera vez a la funcion de verificacion y obtencion de datos
gestionarUsuarioGit() 

# Se ingresa al bucle de MENU
while True:
    select = input("\nQue deseas mirar? -> (repos/followers)\nCambiar Usuario -> user\tPara salir -> salir\n\nIngrese valor: ")

    if select.lower() == "repos":
        print(f"\nResultado:\n")
        cursor.execute("SELECT repo_nombre, repo_url, fecha_creacion FROM datos_repo WHERE usuario = %s", (user,))
        for fila in cursor.fetchall():
            print(f"{fila[0]}\n   Fecha de Creacion:\t{fila[2]}\n   URL de Repositorio:\t{fila[1]}\n")
        
    elif select.lower() == "followers":
        print("\nResultado:\n")
        cursor.execute("SELECT seguidor, tipo, html_url FROM datos_followers WHERE usuario = %s", (user,))
        print(f"{'Nombre':<16}{'Cuenta tipo':<12}\tURL de Usuario\n")
        for fila in cursor.fetchall():
            print(f"{fila[0]:<15} {fila[1]:<12}\t{fila[2]}")

    elif select.lower() == "user":
        user = input("\nIngrese el nombre del usuario GIT: ")   
        gestionarUsuarioGit()
        
    elif select.lower() == "salir":
        print("")
        break
    else:
        print("\n-> Ingrese un valor valido (repos - followers - user - salir)")

# Cerramos la base de datos
cursor.close()
db.close()
for x in range(3):
    time.sleep(1)
    print(f"Saliendo.. {3-x}")
print("Chau :D")
time.sleep(1)




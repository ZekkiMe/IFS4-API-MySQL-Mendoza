CREATE DATABASE github_info;
USE github_info;

CREATE TABLE usuarios_leidos (
    id INT(10) AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50),
    fecha_scan DATE DEFAULT CURRENT_DATE
);

CREATE TABLE datos_repo (
    usuario VARCHAR(50),
    repo_nombre VARCHAR(90),
    repo_url VARCHAR(255),
    fecha_creacion VARCHAR(255)
);

CREATE TABLE datos_followers (
    usuario VARCHAR(50),
    seguidor VARCHAR(50),
    tipo VARCHAR(30),
    html_url VARCHAR(225)
);  

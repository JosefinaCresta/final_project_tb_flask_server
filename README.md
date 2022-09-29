## Flask API Server NanoPredicTorio

Simple API de Flask con autenticación JWT, y gestión de base de datos con SqlAlchemy de _SQLite_ y productivización de modelos de machine learning de _Scikit-Learn_ capaces de realizar predicciones de la energía de nanoparticulas metálicas. Utilizada como backend de [NanoPredicTorio](https://nanopredictorio.herokuapp.com)

<br />

## API disponible con Heroku

https://cresta-app-flask-react.herokuapp.com/

## Código disponible en GitHub

> **Paso #1** - Clonar el proyecto

```bash
$ git clone https://github.com/JosefinaCresta/api-server-flask.git
$ cd api-server-flask
```

<br />

> **Paso #2** - crear un entorno virtual usando python3 y activarlo.

```bash
$ # VInstalación de módulos Virtualenv (sistemas basados en Unix)
$ virtualenv env
$ source env1/bin/activate
```

<br />

> **Paso #3** - Instalar dependencias en virtualenv

```bash
$ pip install -r requirements.txt
```

<br />

> **Paso #4** - Configurar el comando `flask` para la aplicación

```bash
$ export FLASK_APP=run.py
$ export FLASK_ENV=development
```

Para sistemas **Windows**

```powershell
$ (Windows CMD) set FLASK_APP=run.py
$ (Windows CMD) set FLASK_ENV=development
$
$ (Powershell) $env:FLASK_APP = ".\run.py"
$ (Powershell) $env:FLASK_ENV = "development"
```

<br />

> **Paso #5** - Iniciar el servidor de API de prueba en `localhost: 5000`

```bash
$ flask run
```

## Inicio rápido en Docker

> Obtener el código

```bash
$ git clone https://github.com/JosefinaCresta/api-server-flask.git
$ cd api-server-flask
```

## Estructura del proyecto

```bash
api-server-flask/
├── api
│   ├── config.py
│   ├── __init__.py
│   ├── ml_models
│   │   ├── fullDB
│   │   |    ├── model_cluster_0
│   │   |    ├── model_cluster_1
│   │   |    ├── model_cluster_2
│   │   |    └── utils
│   │   |         ├── scaler
│   │   |         ├── pca
│   │   |         └── kmeans
│   │   └── subDB
│   │        ├── model_data_superficial
│   │        └── utils
│   │             └── scaler
│   ├── models.py
│   └── routes.py
├── Dockerfile
├── README.md
├── requirements.txt
├── package.json
├── Procfile
├── run.py
└── tests.py
```

<br />

## Para más información sobre la API

#### [Swagger Dashboard.](https://cresta-app-flask-react.herokuapp.com/)

**Contacto** - [Josefina Cresta](https://github.com/JosefinaCresta#:~:text=can%20reach%20me-,in%20LinkedIn,-Customize%20your%20pins)

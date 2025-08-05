# **Frexco PyLogger**

## Install

___

```bash
pip install frexco_pylogger
```

## Configure

___

```python
# main.py
from frexco_pylogger.functions import PyLogger

logger = PyLogger(appname="my_app")
logger.http(message="Uma mensagem http qualquer", status_code=200, data={"name": "Um nome qualquer", "age": 22})
```

> 2022-09-02 14:05:59 | [HTTP   ] | Uma mensagem http qualquer | [STATUSCODE 200] | {'name': 'Um nome qualquer', 'age': 22}

## Log Types

___

| Tipo      | Description                                                        |
|-----------|--------------------------------------------------------------------|
| `error`   | Informar sobre exceptions tratadas                                 |
| `warning` | Informar eventos ou estados potencialmente prejudicias ao programa |
| `debug`   | Acompanhar eventos ou estados do programa                          |
| `info`    | Descrever infos detalhadas sobre o estado do programa              |
| `http`    | Informar dados de requests e responses feitas via http             |

## Middlewares

___

### django

```python
# httpLogger.py
from frexco_pylogger.functions import PyLogger
from django.utils.deprecation import MiddlewareMixin


class HTTPLoggerMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        logger = PyLogger(appname="my_django_app")
        logger.http(message=f'{request.META.get("REMOTE_ADDR")} {request.method} {request.META.get("PATH_INFO")}',
                    status_code=response.status_code)

        return response
```

```python
# setting.py

MIDDLEWARE = [
    ...,
    'app.utils.httpLogger.HTTPLoggerMiddleware' # path to your middleware file
]

```

### Flask

```python
# Your app setup file
from flask import Flask, request, Response
from frexco_pylogger.functions import PyLogger

app = Flask(__name__)
logger = PyLogger(appname="my_flask_app")

@app.after_request
def log_response(response: Response):
    logger.http(message=f'{request.remote_addr} {request.method} {request.path}',
                status_code=response.status_code)
    return response

```

## Alert

```python
# Seu arquivo de configuração de logger
from frexco_pylogger.functions import PyLogger

logger = PyLogger(appname="my_app_name", group="nome_do_grupo") # Ex: group="warehouse", Ex: group="consumer"

logger.error(message="Uma messagem de error qualquer",
            status_code=500, data={"name": "Um error"}) # Enviar alerta

logger.error(message="Uma messagem de error qualquer repetida",
            status_code=500, data={"name": "Um error"}, alert=False) # Não enviar alerta
```

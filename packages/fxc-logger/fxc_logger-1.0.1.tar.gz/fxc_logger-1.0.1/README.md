# **fxc-logger**

## Install

___

```bash
pip install fxc-logger
```

## Configure

___

```python
# main.py
from fxc_logger import PyLogger

logger = PyLogger(appname="my_app")
logger.http(message="Uma mensagem http qualquer", status_code=200, data={"name": "Um nome qualquer", "age": 22})
```

> 2022-09-02 14:05:59 | [HTTP] | | 9fd8… | Uma mensagem http qualquer | [STATUSCODE 200] | {"name": "Um nome qualquer", "age": 22}

## Correlation ID (Contexto)

Cada requisição ou mensagem pode ter um identificador único para facilitar filtros de log.
A biblioteca gera um UUID v4 automaticamente no primeiro log, mas você pode controlar
isso manualmente.

```python
from fxc_logger import PyLogger, correlation_scope, with_new_correlation_id

logger = PyLogger(appname="consumer")

# 1) Definindo manualmente
auto_id = correlation_scope()      # context-manager
with correlation_scope():          # gera novo UUID
    logger.info("log dentro do bloco")

# 2) Decorando callback do RabbitMQ / Kafka
@with_new_correlation_id
def callback(ch, method, props, body):
    logger.info("mensagem recebida", data=body)
```

*Todos* os logs emitidos dentro do bloco ou função decorada carregam o mesmo
Correlation ID, permitindo rastrear todo o fluxo.

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
from fxc_logger import PyLogger
from django.utils.deprecation import MiddlewareMixin

class HTTPLoggerMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        logger = PyLogger(appname="my_django_app")
        logger.http(message=f"{request.META.get('REMOTE_ADDR')} {request.method} {request.META.get('PATH_INFO')}",
                    status_code=response.status_code)
        return response
```

settings.py:
```python
MIDDLEWARE = [
    ...,
    'app.utils.httpLogger.HTTPLoggerMiddleware'
]
```

### Flask

```python
from flask import Flask, request, Response
from fxc_logger import PyLogger

app = Flask(__name__)
logger = PyLogger(appname="my_flask_app")

@app.after_request
def log_response(response: Response):
    logger.http(message=f"{request.remote_addr} {request.method} {request.path}",
                status_code=response.status_code)
    return response
```

## Alert

```python
from fxc_logger import PyLogger

logger = PyLogger(appname="my_app", group="warehouse")

# envia alerta (ENV=PRD)
logger.error("Falhou o checkout", status_code=500, data={"order_id": 123})

# não envia alerta
logger.error("Falhou o checkout de novo", status_code=500, alert=False)
```

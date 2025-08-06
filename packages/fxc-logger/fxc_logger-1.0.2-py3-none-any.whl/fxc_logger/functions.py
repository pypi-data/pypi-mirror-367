import json
import logging
import os
from copy import copy
from datetime import datetime, timedelta, timezone
from typing import Optional

from .context import get_correlation_id

import requests

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    "DEBUG": 30 + BLUE,
    "INFO": 30 + GREEN,
    "WARNING": 30 + YELLOW,
    "HTTP": 30 + CYAN,
    "ERROR": 30 + RED,
}

PREFIX = "\033["
SUFFIX = "\033[0m"

TIME = "%Y-%m-%d %H:%M:%S"
FORMAT = (
    "%(asctime)s | [%(levelname)s] | %(correlation)s | %(message)s %(status)s %(data)s"
)


def send_message(url: str, data=None):
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    return requests.post(url=url, json=data, headers=headers)


class LoggerFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        try:
            _record = copy(record)
            status: int | None = record.args.get("status") if record.args else None  # type: ignore
            data: dict[str, any] | None = record.args.get("data") if record.args else None  # type: ignore

            if status and type(status) != int:
                raise TypeError("Status type must be integer.")

            _record.status = f"| [STATUSCODE {status}]" if status else ""
            _record.data = f"| {data}" if data else ""
            correlation = get_correlation_id()  # gera automaticamente se não existir
            _record.correlation = f"| {correlation}" if correlation else ""

            message = logging.Formatter.format(self, _record)
            color = COLORS.get(_record.levelname.upper(), 37)

            return "{0}{1}m{2}{3}".format(PREFIX, color, message, SUFFIX)
        except Exception as error:  # noqa: BLE001
            return f"Error while logging your message: {error}"


def setup_logger(appname: str):
    HTTP = logging.DEBUG + 2
    logging.addLevelName(HTTP, "HTTP")

    def http(self, message, *args, **kws):
        self.log(HTTP, message, *args, **kws)

    logging.Logger.http = http  # type: ignore

    logger = logging.getLogger(appname)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Silence other loggers
    for log_name, log_obj in logging.Logger.manager.loggerDict.items():
        if log_name != appname:
            log_obj.disabled = True  # type: ignore

    ch = logging.StreamHandler()
    ch.setFormatter(LoggerFormatter(FORMAT, TIME))

    logger.addHandler(ch)
    return logger


class PyLogger:
    def __init__(self, appname: str = "app exemple", group: str = "exemple"):
        self.env = os.getenv("ENV") if str(os.getenv("ENV")).upper() == "PRD" else False
        self.appname = appname
        self.group = group.lower()
        self.logger = setup_logger(appname)
        self.alertmanager_host: str = ""
        self.credentials = None
        self.bot_token: str = ""
        self.vault()

    @staticmethod
    def check_params(status_code, data):
        obj = {}
        if status_code:
            obj.update({"status": status_code})
        if data:
            obj.update({"data": data})
        return obj

    def error(
        self,
        message: str,
        status_code: Optional[int] = None,
        data=None,
        alert: bool = True,
    ):
        args = self.check_params(status_code, data)
        if args:
            self.logger.error(message, args)
            if self.env and alert:  # type: ignore
                self.send_alert(message=message, status_code=status_code, data=data)
        else:
            self.logger.error(message)
            if self.env and alert:  # type: ignore
                self.send_alert(message=message)

    def warning(self, message: str, status_code: Optional[int] = None, data=None):
        args = self.check_params(status_code, data)
        if args:
            self.logger.warning(message, args)
        else:
            self.logger.warning(message)

    def debug(self, message: str, status_code: Optional[int] = None, data=None):
        args = self.check_params(status_code, data)
        if args:
            self.logger.debug(message, args)
        else:
            self.logger.debug(message)

    def info(self, message: str, status_code: Optional[int] = None, data=None):
        args = self.check_params(status_code, data)
        if args:
            self.logger.info(message, args)
        else:
            self.logger.info(message)

    def http(self, message: str, status_code: Optional[int] = None, data=None):
        args = self.check_params(status_code, data)
        if args:
            self.logger.http(message, args)  # type: ignore
        else:
            self.logger.http(message)  # type: ignore

    def vault(self):
        vault_host = os.environ.get("VAULT_HOST")
        vault_host = vault_host if not vault_host or vault_host.endswith("/") else vault_host + "/"  # type: ignore
        vault_token = os.environ.get("VAULT_TOKEN")
        headers = {"X-Vault-Token": vault_token}

        try:
            response = requests.get(
                url=f"{vault_host}v1/prd/data/alert-logger", headers=headers  # type: ignore
            )
            response = response.json()["data"]["data"]
            self.credentials = response
            self.alertmanager_host = response["alertmanager_host"]
        except Exception as error:  # noqa: BLE001
            self.warning(message="Pylogger não conseguiu acessar o vault", data=error)

    def send_alert(self, message: str, status_code: Optional[int] = None, data=None):
        if self.alertmanager_host == "":
            return

        args = self.check_params(status_code, data)
        url = self.alertmanager_host

        now = datetime.now(timezone.utc)
        startsAt = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        diff = timedelta(minutes=5)
        endsAt = (now + diff).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        status = args.get("status") if args.get("status") else ""
        error = json.dumps(args.get("data")) if "data" in args else ""
        dashboard_link = (
            self.credentials[self.group]
            if self.group in (self.credentials or {})
            else ""
        )
        app_name = self.appname.replace("_", " ").replace("-", " ")

        data = [
            {
                "startsAt": startsAt,
                "endsAt": endsAt,
                "labels": {
                    "alertname": app_name,
                    "logs": self.group,
                    "status": "error_log",
                    "url": dashboard_link,
                    "message": message,
                    "error": error,
                    "status_code": str(status),
                },
            }
        ]

        try:
            response = send_message(url, data)
            if response.status_code != 200:
                self.warning(
                    message="Warning request POST AlertManager error",
                    data=response.json(),
                    status_code=response.status_code,
                )
        except Exception as error:  # noqa: BLE001
            self.warning(
                message="Not passing data for send alert in alertmanager",
                data=error,
                status_code=500,
            )

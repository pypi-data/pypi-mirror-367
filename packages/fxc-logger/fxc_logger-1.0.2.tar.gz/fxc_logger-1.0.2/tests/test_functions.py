"""Exemplos de uso do PyLogger.

Inclui:
1. Logs simples (gera automaticamente um UUID na primeira chamada).
2. Padrão *consumer* com um novo Correlation-ID por mensagem, usando:
   • `with_new_correlation_id` (decorator) para função síncrona.
   • `correlation_scope` para função assíncrona.

Este arquivo não é um teste automatizado de assertivas – serve como
*script de demonstração* que pode ser executado com:

    python tests/test_functions.py
"""

from __future__ import annotations

import asyncio
from random import randint
from typing import Any

from fxc_logger import PyLogger, correlation_scope, with_new_correlation_id

logger = PyLogger(appname="demo")

# ───────────────────────── Logs simples ─────────────────────────
logger.info("Primeiro log")  # gera UUID v4 e o reutiliza
logger.error("Segundo log")

# ───────────────────── Exemplo consumer síncrono ─────────────────────


@with_new_correlation_id  # garante novo ID a cada chamada
def handle_sync(msg: Any, *, correlation_id: str | None = None) -> None:  # noqa: D401
    logger.info("Consumidor síncrono", data=msg)


for i in range(3):
    payload = {"order_id": i, "valor": randint(1, 100)}
    handle_sync(payload)

# ───────────────────── Exemplo consumer assíncrono ────────────────────


async def handle_async(msg: Any, cid: str | None = None) -> None:  # noqa: D401
    # Se o produtor enviou um correlation-id, passe em cid. Caso contrário é None
    with correlation_scope(cid):
        logger.info("Consumidor assíncrono", data=msg)
        logger.info(
            message="Uma mensagem de info qualquer",
            status_code=200,
            data={"name": "Um nome qualquer"},
        )
        await asyncio.sleep(0.1)


async def main_async() -> None:
    for i in range(3, 6):
        payload = {"order_id": i, "valor": randint(1, 100)}
        await handle_async(payload)


if __name__ == "__main__":
    asyncio.run(main_async())

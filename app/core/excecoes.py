"""Exceções de domínio e como elas viram respostas HTTP."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ErroDominio(Exception):
    status_code = 400

    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class NaoEncontrado(ErroDominio):
    status_code = 404


class Conflito(ErroDominio):
    status_code = 409


class RegraDeNegocio(ErroDominio):
    status_code = 422


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErroDominio)
    async def _tratar(_: Request, exc: ErroDominio):
        return JSONResponse(
            status_code=exc.status_code,
            content={"erro": exc.__class__.__name__, "mensagem": exc.mensagem},
        )

from fastapi import FastAPI  # importa o FastAPI
from rotas import clientes         # importa as rotas de clientes


app = FastAPI()              # cria a aplicação

app.include_router(clientes.router)  # registra as rotas de clientes na API


@app.get("/")                # define que essa função responde ao endereço "/"
def inicio():                # quando alguém acessar "/", essa função vai rodar
    return {"mensagem": "API do estúdio de tatuagem funcionando!"}
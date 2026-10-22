from fastapi import APIRouter
from pydantic import BaseModel
from database import conectar
import bcrypt

router = APIRouter()


class Usuario(BaseModel):
    nome: str
    email: str
    senha: str


@router.post("/")
def criar_usuario(usuario: Usuario):
    senha_hash = bcrypt.hashpw(
        usuario.senha.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO usuario (nome, email, senha)
            VALUES (%s, %s, %s)
            """,
            (usuario.nome, usuario.email, senha_hash),
        )
        conn.commit()
        return {"mensagem": "Usuário cadastrado com sucesso"}

    except Exception:
        conn.rollback()
        return {
            "erro": (
                "Não foi possível cadastrar. "
                "Verifique se esse e-mail já está em uso."
            )
        }
    finally:
        cursor.close()
        conn.close()
from fastapi import APIRouter
from pydantic import BaseModel
from database import conectar

router = APIRouter()


class Estilo(BaseModel):
    descricao: str


@router.get("/")
def listar_estilos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM estilo")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@router.get("/{id}")
def buscar_estilo(id: int):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM estilo WHERE idestilo = %s", (id,)
        )
        estilo = cursor.fetchone()

        if not estilo:
            return {"erro": "Estilo não encontrado"}

        return estilo
    finally:
        cursor.close()
        conn.close()


@router.post("/")
def criar_estilo(estilo: Estilo):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO estilo (descricao) VALUES (%s)",
            (estilo.descricao,),
        )
        conn.commit()
        return {"mensagem": "Estilo cadastrado com sucesso"}
    finally:
        cursor.close()
        conn.close()


@router.put("/{id}")
def atualizar_estilo(id: int, estilo: Estilo):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE estilo
            SET descricao=%s
            WHERE idestilo=%s
            """,
            (estilo.descricao, id),
        )
        conn.commit()
        return {"mensagem": "Estilo atualizado com sucesso"}
    finally:
        cursor.close()
        conn.close()


@router.delete("/{id}")
def deletar_estilo(id: int):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM estilo WHERE idestilo = %s", (id,)
        )
        conn.commit()
        return {"mensagem": "Estilo deletado com sucesso"}

    except Exception:
        conn.rollback()
        return {
            "erro": (
                "Não foi possível excluir este estilo. "
                "Verifique se algum tatuador já foi associado a ele."
            )
        }
    finally:
        cursor.close()
        conn.close()
from fastapi import APIRouter
from pydantic import BaseModel
from database import conectar

router = APIRouter()


class Senioridade(BaseModel):
    nome: str


@router.get("/")
def listar_senioridade():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM senioridade")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@router.get("/{id}")
def buscar_senioridade(id: int):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM senioridade WHERE idsenioridade = %s",
            (id,),
        )
        senioridade = cursor.fetchone()

        if not senioridade:
            return {"erro": "Senioridade não encontrada"}

        return senioridade
    finally:
        cursor.close()
        conn.close()


@router.post("/")
def criar_senioridade(senioridade: Senioridade):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO senioridade (nome) VALUES (%s)",
            (senioridade.nome,),
        )
        conn.commit()
        return {"mensagem": "Senioridade cadastrada com sucesso"}
    finally:
        cursor.close()
        conn.close()


@router.put("/{id}")
def atualizar_senioridade(id: int, senioridade: Senioridade):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE senioridade
            SET nome=%s
            WHERE idsenioridade=%s
            """,
            (senioridade.nome, id),
        )
        conn.commit()
        return {"mensagem": "Senioridade atualizada com sucesso"}
    finally:
        cursor.close()
        conn.close()


@router.delete("/{id}")
def deletar_senioridade(id: int):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM senioridade WHERE idsenioridade = %s",
            (id,),
        )
        conn.commit()
        return {"mensagem": "Senioridade deletada com sucesso"}

    except Exception:
        conn.rollback()
        return {
            "erro": (
                "Não foi possível excluir esta senioridade. "
                "Verifique se ela está sendo usada por algum tatuador."
            )
        }
    finally:
        cursor.close()
        conn.close()
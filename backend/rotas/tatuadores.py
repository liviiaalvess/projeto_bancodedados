from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from database import conectar

router = APIRouter()


class EstilosDoTatuador(BaseModel):
    idestilos: List[int]


class Tatuador(BaseModel):
    nometatuador: str
    cpf: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    datacontratacao: Optional[str] = None
    idsenioridade: int


@router.get("/")
def listar_tatuadores():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT tatuador.*,
                   senioridade.nome AS senioridade
            FROM tatuador
            JOIN senioridade
              ON tatuador.idsenioridade = senioridade.idsenioridade
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@router.get("/{id}")
def buscar_tatuador(id: int):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM tatuador WHERE idtatuador = %s",
            (id,),
        )
        tatuador = cursor.fetchone()

        if not tatuador:
            return {"erro": "Tatuador não encontrado"}

        return tatuador
    finally:
        cursor.close()
        conn.close()


@router.post("/")
def criar_tatuador(tatuador: Tatuador):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO tatuador
            (nometatuador, cpf, email, telefone,
             datacontratacao, idsenioridade)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                tatuador.nometatuador,
                tatuador.cpf,
                tatuador.email,
                tatuador.telefone,
                tatuador.datacontratacao,
                tatuador.idsenioridade,
            ),
        )
        novo_id = cursor.lastrowid
        conn.commit()

        return {
            "mensagem": "Tatuador cadastrado com sucesso",
            "idtatuador": novo_id,
        }
    finally:
        cursor.close()
        conn.close()


@router.put("/{id}")
def atualizar_tatuador(id: int, tatuador: Tatuador):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE tatuador
            SET nometatuador=%s, cpf=%s, email=%s,
                telefone=%s, datacontratacao=%s, idsenioridade=%s
            WHERE idtatuador=%s
            """,
            (
                tatuador.nometatuador,
                tatuador.cpf,
                tatuador.email,
                tatuador.telefone,
                tatuador.datacontratacao,
                tatuador.idsenioridade,
                id,
            ),
        )
        conn.commit()
        return {"mensagem": "Tatuador atualizado com sucesso"}
    finally:
        cursor.close()
        conn.close()


@router.delete("/{id}")
def deletar_tatuador(id: int):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM tatuador WHERE idtatuador = %s",
            (id,),
        )
        conn.commit()
        return {"mensagem": "Tatuador deletado com sucesso"}

    except Exception:
        conn.rollback()
        return {
            "erro": (
                "Não foi possível excluir este tatuador. "
                "Verifique se possui agendamentos ou estilos associados."
            )
        }
    finally:
        cursor.close()
        conn.close()


@router.get("/{id}/estilos")
def listar_estilos_do_tatuador(id: int):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT estilo.idestilo, estilo.descricao
            FROM tatuador_estilo
            JOIN estilo
              ON tatuador_estilo.idestilo = estilo.idestilo
            WHERE tatuador_estilo.idtatuador = %s
        """, (id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@router.put("/{id}/estilos")
def atualizar_estilos_do_tatuador(
    id: int, dados: EstilosDoTatuador
):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM tatuador_estilo WHERE idtatuador = %s",
            (id,),
        )

        for idestilo in dados.idestilos:
            cursor.execute(
                """
                INSERT INTO tatuador_estilo
                (idtatuador, idestilo, dataestilo)
                VALUES (%s, %s, CURDATE())
                """,
                (id, idestilo),
            )

        conn.commit()
        return {"mensagem": "Estilos atualizados com sucesso"}
    finally:
        cursor.close()
        conn.close()
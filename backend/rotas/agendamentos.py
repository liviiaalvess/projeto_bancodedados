from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import conectar
import os

router = APIRouter()

PASTA_UPLOADS = "uploads"
os.makedirs(PASTA_UPLOADS, exist_ok=True)


class Agendamento(BaseModel):
    idcliente: int
    idtatuador: int
    dataagendamento: str
    horaagendamento: str
    descricaotatuagem: Optional[str] = None
    valortatuagem: Optional[float] = None
    status: Optional[str] = None


def formatar_hora(agendamento):
    hora = agendamento.get("horaagendamento")

    if hora is not None and hasattr(hora, "total_seconds"):
        total = int(hora.total_seconds())
        horas, resto = divmod(total, 3600)
        minutos, segundos = divmod(resto, 60)
        agendamento["horaagendamento"] = (
            f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        )

    return agendamento


@router.get("/")
def listar_agendamentos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT agendamento.*,
                   cliente.nome AS cliente,
                   tatuador.nometatuador AS tatuador
            FROM agendamento
            JOIN cliente
              ON agendamento.idcliente = cliente.idcliente
            JOIN tatuador
              ON agendamento.idtatuador = tatuador.idtatuador
        """)

        agendamentos = cursor.fetchall()
        return [formatar_hora(a) for a in agendamentos]
    finally:
        cursor.close()
        conn.close()


@router.post("/")
def criar_agendamento(agendamento: Agendamento):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO agendamento
            (idcliente, idtatuador, dataagendamento,
             horaagendamento, descricaotatuagem, valortatuagem)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                agendamento.idcliente,
                agendamento.idtatuador,
                agendamento.dataagendamento,
                agendamento.horaagendamento,
                agendamento.descricaotatuagem,
                agendamento.valortatuagem,
            ),
        )

        novo_id = cursor.lastrowid
        conn.commit()

        return {
            "mensagem": "Agendamento cadastrado com sucesso",
            "idagendamento": novo_id,
        }
    finally:
        cursor.close()
        conn.close()


@router.get("/{id}")
def buscar_agendamento(id: int):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM agendamento WHERE idagendamento = %s",
            (id,),
        )
        agendamento = cursor.fetchone()

        if not agendamento:
            return {"erro": "Agendamento não encontrado"}

        return formatar_hora(agendamento)
    finally:
        cursor.close()
        conn.close()


@router.put("/{id}")
def atualizar_agendamento(id: int, agendamento: Agendamento):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE agendamento
            SET idcliente=%s, idtatuador=%s,
                dataagendamento=%s, horaagendamento=%s,
                descricaotatuagem=%s, valortatuagem=%s, status=%s
            WHERE idagendamento=%s
            """,
            (
                agendamento.idcliente,
                agendamento.idtatuador,
                agendamento.dataagendamento,
                agendamento.horaagendamento,
                agendamento.descricaotatuagem,
                agendamento.valortatuagem,
                agendamento.status,
                id,
            ),
        )
        conn.commit()
        return {"mensagem": "Agendamento atualizado com sucesso"}
    finally:
        cursor.close()
        conn.close()


@router.delete("/{id}")
def deletar_agendamento(id: int):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM agendamento WHERE idagendamento = %s",
            (id,),
        )
        conn.commit()
        return {"mensagem": "Agendamento deletado com sucesso"}
    finally:
        cursor.close()
        conn.close()


@router.post("/{id}/desenho")
async def upload_desenho(
    id: int,
    arquivo: UploadFile = File(...),
):
    nome_arquivo = f"{id}_{os.path.basename(arquivo.filename or 'desenho')}"
    caminho = os.path.join(PASTA_UPLOADS, nome_arquivo)

    conteudo = await arquivo.read()

    try:
        with open(caminho, "wb") as f:
            f.write(conteudo)

        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE agendamento
                SET desenhoaprovado=%s
                WHERE idagendamento=%s
                """,
                (nome_arquivo, id),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    except Exception:
        if os.path.exists(caminho):
            os.remove(caminho)
        raise HTTPException(
            status_code=500,
            detail="Não foi possível salvar o desenho.",
        )

    return {
        "mensagem": "Desenho enviado com sucesso",
        "arquivo": nome_arquivo,
    }
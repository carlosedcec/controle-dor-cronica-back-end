from flask import Flask, request, render_template, jsonify, redirect
from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import json

from model import Session, Record, Event, RecordType
from functions import CRUDFunctions
from functions import ValidationsHelper as validation
from schema import *

info = Info(title="Controle de Dor Crônica API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# ------------------------------------------------------------
# Init DB
# ------------------------------------------------------------
def init_database():
    session = Session()
    try:
        # Verifica se não existe nenhum tipo de registro no banco
        if session.query(RecordType).count() == 0:
            # Se não existe nenhum, cria um default
            default_record_type = RecordType(name="dor", order=1)
            session.add(default_record_type)
            session.commit()
    except Exception as e:
        session.rollback()
        print("Erro ao tentar inicializar o banco: " + e)
    finally:
        session.close()

# ------------------------------------------------------------
# Render Template Routes
# ------------------------------------------------------------

@app.get("/")
def home():
    return redirect("/openapi")

# ------------------------------------------------------------
# Record Types
# ------------------------------------------------------------

record_type_tag = Tag(name="Tipos de Registro", description="Adição, visualização, edição e remoção de tipos de registro")

@app.get("/get-record-types", tags=[record_type_tag],
        responses={ "200": RecordType_ListReturnSchema, "400": ErrorSchema })
def get_record_types():
    """Pesquisa  por todos os tipos de registro cadastrados
    Retorna uma listagem dos tipos de registro
    """

    def get_function(session, params):

        record_types = session.query(RecordType).order_by(RecordType.order.asc()).all()

        data = []
        for record_type in record_types:
            data.append({
                "id": record_type.id,
                "name": record_type.name,
                "order": record_type.order
            })

        return data
    
    crud = CRUDFunctions()
    return crud.get_data(get_function, {}, "tipos de registros")

@app.post("/add-record-type", tags=[record_type_tag],
        responses={ "200": RecordType_AddReturnSchema, "400": ErrorSchema })
def add_record_type(body: RecordType_AddFormSchema):
    """Adiciona um novo tipo de registro ao banco de dados
    Retorna o objeto inserído e uma mensagem de confirmação ou uma menasgem de erro
    """

    def insert_function(body, session):

        new_maximum_order = 1
        record_type_with_maximum_order = session.query(RecordType).order_by(RecordType.order.desc()).first()
        if record_type_with_maximum_order and record_type_with_maximum_order.order > 0:
            new_maximum_order = (record_type_with_maximum_order.order + 1)

        return RecordType(
            name=str(body.name).lower(),
            order=new_maximum_order
        )

    crud = CRUDFunctions()
    return crud.add_data(body, insert_function, "tipo de registro")

@app.put("/update-record-type/<int:record_type_id>", tags=[record_type_tag],
        responses={ "200": RecordType_UpdateReturnSchema, "400": ErrorSchema })
def update_record_type(path: RecordType_IdSchema, body: RecordType_UpdateFormSchema):
    """Atualiza o tipo de registro informado
    Retorna o objeto atualizado e uma mensagem de confirmação ou uma menasgem de erro
    """

    def update_function(body, session, url_parameter):

        record_type = session.query(RecordType).filter(RecordType.id == url_parameter).first()
        if not record_type:
            return { "error": "Tipo de Registro não encontrado no banco de dados" }, 404
        record_type.name = str(body.name).lower()

        return record_type

    crud = CRUDFunctions()
    return crud.update_data(body, update_function, path.record_type_id, "tipo de registro")

@app.put("/update-record-type-order/", tags=[record_type_tag],
        responses={ "200": RecordType_UpdateOrderReturnSchema, "400": ErrorSchema })
def update_record_type_order(body: RecordType_UpdateOrderFormSchema):
    """Atualiza a ordenação dos tipos de registro no banco de dados
    Retorna uma mensagem de confirmação ou erro
    """

    def update_function(body, session, url_parameter):

        if not body.record_types_order or len(body.record_types_order) == 0:
            return { "error": "Formato de dados inválido" }, 422

        record_types_return = []

        for rto in body.record_types_order:
            record_type = session.query(RecordType).filter(RecordType.id == rto.id).first()
            if not record_type:
                return { "error": "Tipo de Registro não encontrado no banco de dados" }, 404
            record_type.order = int(rto.order)
            record_types_return.append(record_type)

        return record_types_return

    crud = CRUDFunctions()
    return crud.update_data(body, update_function, 0, "tipos de registros")

@app.delete("/delete-record-type/<int:record_type_id>", tags=[record_type_tag],
        responses={ "200": RecordType_DeleteReturnSchema, "400": ErrorSchema })
def delete_record_type(path: RecordType_IdSchema):
    """Deleta o tipo de registro informado do banco de dados
    Retorna uma mensagem de confirmação ou erro
    """
    crud = CRUDFunctions()
    return crud.delete_data(RecordType, RecordType.id, path.record_type_id, "tipo de registro")

# ------------------------------------------------------------
# Records
# ------------------------------------------------------------

record_tag = Tag(name="Registros", description="Adição, visualização, edição e remoção de registros")

@app.get("/get-records", tags=[record_tag],
        responses={ "200": Record_ListCompleteReturnSchema, "400": ErrorSchema })
def get_records():
    """Pesquisa por todos os registros cadastrados
    Retorna uma listagem dos registros
    """

    def get_function(session, params):
        # Seleciona os dados agrupando registros que são iguais na mesma data e calculando a média destes
        daily_records = session.query(
            Record.id,
            Record.date,
            Record.time,
            Record.record_type_id,
            RecordType.name.label('record_type_name'),
            func.sum(Record.value).label('total_value'),
            func.avg(Record.value).label('average_value')
        ).join(
            RecordType,
            Record.record_type_id == RecordType.id
        ).group_by(
            Record.date,
            Record.record_type_id
        ).all()
        
        data = []
        for record in daily_records:
            data.append({
                "id": record.id,
                "date": record.date,
                "time": record.time,
                "record_type_id": record.record_type_id,
                "record_type_name": record.record_type_name,
                "total_value": record.total_value,
                "average_value": round(record.average_value, 2) if record.average_value else 0
            })

        return data

    crud = CRUDFunctions()
    return crud.get_data(get_function, {}, "registros")

@app.get("/get-records-by-record-type/<int:record_type_id>", tags=[record_tag],
        responses={ "200": Record_ListBasicReturnSchema, "400": ErrorSchema })
def get_records_by_record_type(path: RecordType_IdSchema):
    """Pesquisa pelos registros referentes ao tipo de registro informado como parâmetro
    Retorna uma listagem dos registros encontrados
    """

    def get_function(session, params):
        # Busca os registros filtrando por tipo de registro
        records = session.query(
            Record,
            RecordType.name.label('record_type_name')
        ).join(
            RecordType, 
            Record.record_type_id == RecordType.id
        ).filter(
            Record.record_type_id == params["record_type_id"]
        ).order_by(Record.date.desc(), Record.time.desc()).all()
        
        data = []
        for record, record_type_name in records:
            data.append({
                "id": record.id,
                "date": record.date,
                "time": record.time,
                "record_type_id": record.record_type_id,
                "record_type_name": record_type_name,
                "value": record.value
            })
        
        return data

    crud = CRUDFunctions()
    return crud.get_data(get_function, { "record_type_id": path.record_type_id }, "registros")    

@app.post("/add-record", tags=[record_tag],
        responses={ "200": Record_AddReturnSchema, "400": ErrorSchema })
def add_record(body: Record_AddFormSchema):
    """Adiciona um novo registro ao banco de dados
    Retorna o objeto inserído e uma mensagem de confirmação ou uma menasgem de erro
    """

    def insert_function(body, session):

        if not validation.is_valid_date(body.date):
            return { "error": "O campo \"Data\" está inválido" }, 422

        if not validation.is_valid_time(body.time):
            return { "error": "O campo \"Hora\" está inválido" }, 422

        record_type = session.query(RecordType).filter(RecordType.id == int(body.record_type_id)).first()

        if not record_type:
            return { "error": "Tipo de registro não encontrado no banco de dados" }, 404

        return Record(
            record_type_id=record_type.id,
            date=body.date,
            time=body.time,
            value=body.value
        )

    crud = CRUDFunctions()
    return crud.add_data(body, insert_function, "registro")

@app.post("/add-batch-records", tags=[record_tag],
        responses={ "200": Record_AddBatchReturnSchema, "400": ErrorSchema })
def add_batch_records(body: Record_AddBatchFormSchema):
    """Adiciona registros em lote no banco de dados
    Retorna a lista de objetos inserídos e uma mensagem de confirmação ou uma mensagem de erro
    """

    def insert_function(body, session):

        if not validation.is_valid_date(body.date):
            return { "error": "O campo \"Data\" está inválido" }, 422

        if not validation.is_valid_time(body.time):
            return { "error": "O campo \"Hora\" está inválido" }, 422

        if not body.batch_records or len(body.batch_records) == 0:
            return { "error": "Formato de dados inválido" }, 422

        records = []

        for record in body.batch_records:
            records.append(Record(
                record_type_id=record.record_type_id,
                date=body.date,
                time=body.time,
                value=record.value
            ))
        
        return records

    crud = CRUDFunctions()
    return crud.add_data(body, insert_function, "registro")

@app.put("/update-record/<int:record_id>", tags=[record_tag],
        responses={ "200": Record_UpdateReturnSchema, "400": ErrorSchema })
def update_record(path: Record_IdSchema, body: Record_UpdateFormSchema):
    """Atualiza o registro informado
    Retorna o objeto atualizado e uma mensagem de confirmação ou uma menasgem de erro
    """

    def update_function(body, session, url_parameter):

        if not validation.is_valid_date(body.date):
            return { "error": "O campo \"Data\" está inválido" }, 422

        if not validation.is_valid_time(body.time):
            return { "error": "O campo \"Hora\" está inválido" }, 422

        record = session.query(Record).filter(Record.id == url_parameter).first()

        if not record:
            return { "error": "Registro não encontrado no banco de dados" }, 404

        record.date = str(body.date)
        record.time = str(body.time)
        record.value = str(body.value)

        return record

    crud = CRUDFunctions()
    return crud.update_data(body, update_function, path.record_id, "tipo de registro")

@app.delete("/delete-record/<int:record_id>", tags=[record_tag],
        responses={ "200": Record_DeleteReturnSchema, "400": ErrorSchema })
def delete_record(path: Record_IdSchema):
    """Deleta o registro informado do banco de dados
    Retorna uma mensagem de confirmação ou um erro
    """
    crud = CRUDFunctions()
    return crud.delete_data(Record, Record.id, path.record_id, "registro")

@app.delete("/delete-records-date/<string:records_date>", tags=[record_tag],
        responses={ "200": Record_DeleteReturnSchema, "400": ErrorSchema })
def delete_records_date(path: Record_DateIdSchema):
    """Deleta todos os registro referentes a data passada como parâmetro
    Retorna uma mensagem de confirmação ou um erro
    """
    crud = CRUDFunctions()
    return crud.delete_data(Record, Record.date, path.records_date, "dia")

# ------------------------------------------------------------
# Events
# ------------------------------------------------------------

event_tag = Tag(name="Eventos", description="Adição, visualização, edição e remoção de eventos")

@app.get("/get-events", tags=[event_tag],
        responses={ "200": Event_ListReturnSchema, "400": ErrorSchema })
def get_events():
    """Pesquisa por todos os eventos cadastrados
    Retorna uma listagem dos eventos
    """

    def get_function(session, params):

        events = session.query(Event).order_by(Event.date.desc(), Event.time.desc()).all()

        data = []
        for event in events:
            data.append({
                "id": event.id,
                "description": event.description,
                "date": event.date,
                "time": event.time
            })
    
        return data
    
    crud = CRUDFunctions()
    return crud.get_data(get_function, {}, "eventos")

@app.post("/add-event", tags=[event_tag],
        responses={ "200": Event_AddReturnSchema, "400": ErrorSchema })
def add_event(body: Event_AddFormSchema):
    """Adiciona um novo evento ao banco de dados
    Retorna o objeto inserído e uma mensagem de confirmação ou uma menasgem de erro
    """

    def insert_function(body, session):

        if not validation.is_valid_date(body.date):
            return { "error": "O campo \"Data\" está inválido" }, 422

        if not validation.is_valid_time(body.time):
            return { "error": "O campo \"Hora\" está inválido" }, 422

        return Event(
            description=body.description,
            date=body.date,
            time=body.time
        )

    crud = CRUDFunctions()
    return crud.add_data(body, insert_function, "evento")

@app.put("/update-event/<int:event_id>", tags=[event_tag],
        responses={ "200": Event_UpdateReturnSchema, "400": ErrorSchema })
def update_event(path: Event_IdSchema, body: Event_UpdateFormSchema):
    """Atualiza o evento informado
    Retorna o objeto atualizado e uma mensagem de confirmação ou uma menasgem de erro
    """

    def update_function(body, session, url_parameter):

        if not validation.is_valid_date(body.date):
            return { "error": "O campo \"Data\" está inválido" }, 422

        if not validation.is_valid_time(body.time):
            return { "error": "O campo \"Hora\" está inválido" }, 422

        event = session.query(Event).filter(Event.id == url_parameter).first()
        if not event:
            return { "error": "Evento não encontrado no banco de dados" }, 404

        event.description = str(body.description)
        event.date = str(body.date)
        event.time = str(body.time)

        return event

    crud = CRUDFunctions()
    return crud.update_data(body, update_function, path.event_id, "evento")

@app.delete("/delete-event/<int:event_id>", tags=[event_tag],
        responses={ "200": Event_DeleteReturnSchema, "400": ErrorSchema })
def delete_event(path: Event_IdSchema):
    """Deleta o evento informado do banco de dados
    Retorna uma mensagem de confirmação ou erro
    """
    crud = CRUDFunctions()
    return crud.delete_data(Event, Event.id, path.event_id, "evento")

# ------------------------------------------------------------
# App Run
# -----------------------------------------------------------

if __name__ == '__main__':
    init_database()
    app.run(host="127.0.0.1", port=5000)
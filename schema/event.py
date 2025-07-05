from pydantic import BaseModel, Field
from typing import Optional, List

# --------------
# Views Schema

class Event_ViewSchema(BaseModel):
    """ Define a estrutura de retorno de um evento
    """
    id: int = 1
    description: str = "Descrição do evento"
    date: str = "2025-12-17"
    time: str = "09:36"

class Event_ListReturnSchema(BaseModel):
    """ Define como a listagem de eventos será retornada
    """
    data: List[Event_ViewSchema]

# --------------
# Add Schema

class Event_AddFormSchema(BaseModel):
    """ Define como um novo evento a ser inserido deve ser estruturado
    """
    description: str = Field(..., example="Descrição do evento")
    date: str = Field(..., example="2025-12-17")
    time: str = Field(..., example="09:36")

class Event_AddReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a inserção de um evento
    """
    data: Event_ViewSchema
    message: str

# --------------
# Update Schema

class Event_IdSchema(BaseModel):
    """ Define o parâmetro a ser passado na URL para update ou delete
    """
    event_id: int

class Event_UpdateFormSchema(BaseModel):
    """ Define como um evento a ser atulizado deve ser estruturado
    """
    description: str = Field(..., example="Nova descrição")
    date: str = Field(..., example="2025-12-17")
    time: str = Field(..., example="09:36")

class Event_UpdateReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a atualização de um evento
    """
    data: Event_ViewSchema
    message: str

# --------------
# Delete Schema

class Event_DeleteReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a exclusão de um evento
    """
    message: str
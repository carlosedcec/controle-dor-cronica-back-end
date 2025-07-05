from pydantic import BaseModel, Field
from typing import Optional, List

# --------------
# Views Schema

class RecordType_ViewSchema(BaseModel):
    """ Define a estrutura de retorno de um tipo de registro
    """
    id: int = 1
    name: str = "Dor"
    order: int = 1

class RecordType_ListReturnSchema(BaseModel):
    """ Define como a listagem de tipos de registro será retornada
    """
    data: List[RecordType_ViewSchema]

# --------------
# Add Schema

class RecordType_AddFormSchema(BaseModel):
    """ Define como um novo tipo de registro a ser inserido deve ser estruturado
    """
    name: str = Field(..., example="Dor")

class RecordType_AddReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a inserção de um tipo de registro
    """
    data: RecordType_ViewSchema
    message: str

# --------------
# Update Schema

class RecordType_IdSchema(BaseModel):
    """ Define o parâmetro a ser passado na URL para update ou delete
    """
    record_type_id: int

class RecordType_UpdateFormSchema(BaseModel):
    """ Define como um tipo de registro a ser atulizado deve ser estruturado
    """
    name: str = Field(..., example="Novo nome")

class RecordType_UpdateReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a atualização de um tipo de registro
    """
    data: RecordType_ViewSchema
    message: str

class RecordType_UpdateOrderInnerFormSchema(BaseModel):
    """ Define como um tipo de registro deve ser estruturado para a atualização da ordenação dos tipos de registro
    """
    id: int = Field(..., example=1)
    order: int = Field(..., example=1)

class RecordType_UpdateOrderFormSchema(BaseModel):
    """ Define como deve ser a estrutura para a atualização da ordenação dos tipos de registro
    """
    record_types_order: List[RecordType_UpdateOrderInnerFormSchema]

class RecordType_UpdateOrderReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a atualização da ordenação dos tipos de registro
    """
    data: RecordType_ViewSchema
    message: str

# --------------
# Delete Schema

class RecordType_DeleteReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a exclusão de um tipo de registro
    """
    message: str
from pydantic import BaseModel, Field
from typing import Optional, List, Any

# --------------
# Views Schema

class Record_ViewBasicSchema(BaseModel):
    """ Define a estrutura básica de retorno de um registro (com nome do tipo de registro incluso)
    """
    id: int = 1
    date: str = "2025-06-07"
    time: str = "10:05"
    record_type_id: int = 1
    record_type_name: str = "Dor"
    value: float = 6

class Record_ViewCompleteSchema(BaseModel):
    """ Define a estrutura mais completa de retorno de um registro  (com nome do tipo de registro, valor total do registro no dia e média do registro no dia incluso)
    """
    id: int = 1
    date: str = "2025-06-07"
    time: str = "10:05"
    record_type_id: int = 1
    record_type_name: str = "Dor"
    total_value: float = 21
    average_value: float = 10.5

class Record_ViewReturnSchema(BaseModel):
    """ Define a estrutura padrão de retorno de um registro
    """
    id: int = 1
    date: str = "2025-06-07"
    time: str = "10:05"
    record_type_id: int = 1
    value: float = 6

class Record_ListBasicReturnSchema(BaseModel):
    """ Define como a listagem básica de registros será retornada
    """
    data: List[Record_ViewBasicSchema]

class Record_ListCompleteReturnSchema(BaseModel):
    """ Define como a listagem mais completa de registros será retornada
    """
    data: List[Record_ViewCompleteSchema]

# --------------
# Add Schema

class Record_AddFormSchema(BaseModel):
    """ Define como um novo registro a ser inserido deve ser estruturado
    """
    record_type_id: int = Field(..., example=1)
    date: str = Field(..., example="2025-06-07")
    time: str = Field(..., example="10:05")
    value: float = Field(..., example=6, ge=0, le=10)

class Record_AddReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a inserção de um registro
    """
    data: Record_ViewReturnSchema
    message: str

class Record_AddBatchInnerFormSchema(BaseModel):
    """ Define como um registro deve ser estruturado para a inserção em lote
    """
    record_type_id: int = Field(..., example=1)
    value: float = Field(..., example=7, ge=0, le=10)

class Record_AddBatchFormSchema(BaseModel):
    """ Define como deve ser a estrutura para a inserção em lote de registros
    """
    date: str = Field(..., example="2025-06-07")
    time: str = Field(..., example="10:05")
    batch_records: List[Record_AddBatchInnerFormSchema]

class Record_AddBatchReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a inserção em lote
    """
    data: List[Record_AddFormSchema]
    message: str

# --------------
# Update Schema

class Record_IdSchema(BaseModel):
    """ Define o parâmetro a ser passado na URL para update ou delete
    """
    record_id: int

class Record_UpdateFormSchema(BaseModel):
    """ Define como um registro a ser atulizado deve ser estruturado
    """
    date: str = Field(..., example="2025-06-07")
    time: str = Field(..., example="10:05")
    value: float = Field(..., example=6, ge=0, le=10)

class Record_UpdateReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a atualização de um registro
    """
    data: Record_ViewReturnSchema
    message: str

# --------------
# Delete Schema

class Record_DateIdSchema(BaseModel):
    """ Define o parâmetro da data a ser passado na URL para delação de data
    """
    records_date: str = "2025-11-10"

class Record_DeleteReturnSchema(BaseModel):
    """ Define a estrutura de retorno após a exclusão de um registro
    """
    message: str
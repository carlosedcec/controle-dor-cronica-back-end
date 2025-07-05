from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import event as sqlalchemy_event
import os

from model.base import Base
from model.record_type import RecordType
from model.record import Record
from model.event import Event

db_path = "database/"

# verifica se o diretorio não existe
if not os.path.exists(db_path):
   # então cria o diretorio
   os.makedirs(db_path)


# url de acesso ao banco
db_url = 'sqlite:///%s/controle_dor_db.sqlite3' % db_path

# cria a engine de conexão com o banco
engine = create_engine(db_url)

# configuração de foreign key constraints
@sqlalchemy_event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# instancia um criador de seção com o banco
Session = sessionmaker(bind=engine)

# cria o banco se ele não existir 
if not database_exists(engine.url):
    create_database(engine.url) 

# cria as tabelas do banco, caso não existam
Base.metadata.create_all(engine)
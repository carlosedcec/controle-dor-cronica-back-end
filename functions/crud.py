from flask import jsonify
from sqlalchemy.exc import IntegrityError
from model import Session

class CRUDFunctions():

    # função que converte o sqlalchemy object num objeto "normal" para ser retornado para o front
    def to_dict(self, data):
        # verifica se é uma lista de objetos ou um objeto único
        if isinstance(data, (list, tuple)) and len(data) > 0:
            data_list = []
            for d in data:
                data_list.append({ c.name: getattr(d, c.name) for c in d.__table__.columns })
            # retorna a lista de objetos
            return data_list
        else:
            # retorna o objeto único
            return { c.name: getattr(data, c.name) for c in data.__table__.columns }

    def get_data(self, get_function, function_params, message):
        try:
            # instancia a sessão
            session = Session()
            # executa a get_funtion passada recebendo dados de retorno ou um erro
            get_return = get_function(session, function_params)
            # verifica se deu erro
            if type(get_return) is tuple and "error" in get_return[0]:
                # se deu erro retorna o erro
                return get_return
            # se não deu erro erro retorna os dados
            return { "data": get_return }
        except Exception as e:
            print(str(e))
            session.rollback()
            return { "message": "Não foi possível buscar os " + message + " no banco de dados" }, 400
        finally:
            session.close()    

    def add_data(self, body, insert_function, message):
        try:
            # instancia a sessão
            session = Session()
            # executa a insert_function passada recebendo um sqlalchemy object para ser inserido ou um erro
            add_return = insert_function(body, session)
            # verifica se deu erro
            if type(add_return) is tuple and "error" in add_return[0]:
                # se deu erro retorna o erro
                return add_return
            # se não deu erro verifica se o objeto é uma list ou um objeto único e adiciona no banco
            if isinstance(add_return, (list)) and len(add_return) > 0:
                for item in add_return:
                    session.add(item)
            else:
                session.add(add_return)
            # commita a operação
            session.commit()
            # atualiza o sqlalchemy object
            if isinstance(add_return, (list)) and len(add_return) > 0:
                for item in add_return:
                    session.refresh(item)
            else:
                session.refresh(add_return)
            # transforma o sqlachmey object inserído num objeto "normal" e retorna o object e a mensagem de sucesso
            return { "data": self.to_dict(add_return), "message": message.capitalize() + " adicionado com sucesso" }, 200
        except IntegrityError as e:
            print(str(e))
            session.rollback()
            return { "error": message.capitalize() + " já existente no banco de dados" }, 409
        except Exception as e:
            print(str(e))
            session.rollback()
            return { "error": "Não foi possível salvar o " + message + " no banco de dados" }, 400
        finally:
            session.close()

    def update_data(self, body, update_function, url_parameter, message):
        try:
            # instancia a sessão
            session = Session()
            # executa a update_function passada recebendo o sqlalchemy object que foi atualizado ou um erro
            update_return = update_function(body, session, url_parameter)
            # verifica se deu erro
            if type(update_return) is tuple and "error" in update_return[0]:
                # se deu erro retorna o erro
                return update_return
            # se não deu erro commita a operação
            session.commit()
            # transforma o sqlachmey object atualizado num objeto "normal" e retorna o dict object e a mensagem de sucesso
            return { "data": self.to_dict(update_return), "message": message.capitalize() + " atualizado com sucesso" }, 200
        except IntegrityError as e:
            print(str(e))
            session.rollback()
            return { "error": "Já existe um " + message + " com este nome" }, 409
        except Exception as e:
            print(str(e))
            session.rollback()
            return { "error": "Não foi possível atualizar o " + message + " no banco de dados" }, 400
        finally:
            session.close()

    def delete_data(self, object, attribute, url_parameter, message):
        try:
            # instancia a sessão
            session = Session()
            # deleta o objeto guardando a quantidade de linhas deletadas
            count = session.query(object).filter(attribute == url_parameter).delete()
            # commita a operação
            session.commit()
            # verifica se alguma linha foi afetada e retorna uma mensagem de sucesso ou erro
            if count:
                return { "message": message.capitalize() + " deletado com sucesso" }, 200
            else:
                return { "message": message.capitalize() + " não encontrado no banco de dados" }, 404
        except IntegrityError as e:
            print(str(e))
            session.rollback()
            return { "message": "Não é possível deletar este registro do banco de dados" }, 409
        except Exception as e:
            print(str(e))
            session.rollback()
            return { "message": "Não foi possível deletar o registro do banco de dados" }, 400
        finally:
            session.close()
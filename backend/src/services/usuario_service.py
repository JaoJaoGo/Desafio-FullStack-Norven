from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_password_hash

from models.usuario_model import UsuarioModel

from repositories.contato_repository import ContatoRepository
from repositories.endereco_repository import EnderecoRepository
from repositories.usuario_repository import UsuarioRepository

from schemas.contato_schema import ContatoCreateSchema
from schemas.endereco_schema import EnderecoCreateSchema
from schemas.usuario_schema import UsuarioCreateSchema, UsuarioUpdateSchema

class UsuarioService:
    @staticmethod
    async def create_usuario(db: AsyncSession, data: UsuarioCreateSchema) -> UsuarioModel:
        try:
            usuario_existente = await UsuarioRepository.find_by_email(db, str(data.email))

            if usuario_existente:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um usuário com este e-mail."
                )
            
            endereco = await EnderecoRepository.create(db, data.endereco)
            contato = await ContatoRepository.create(db, data.contato)

            hashed_password = get_password_hash(data.password)

            usuario = await UsuarioRepository.create(
                db=db,
                nome=data.nome,
                email=data.email,
                hashed_password=hashed_password,
                nivel_acesso=data.nivel_acesso,
                endereco_id=endereco.id,
                contato_id=contato.id
            )

            await db.commit()
            await db.refresh(usuario)

            return usuario

        except HTTPException:
            await db.rollback()
            raise

        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível cadastrar o usuário. Alguns dados informados já existem.")

        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def list(db: AsyncSession, search: Optional[str], nivel_acesso: Optional[str], page: int, per_page: int) -> tuple[list[UsuarioModel], int]:
        return await UsuarioRepository.list(db, search, nivel_acesso, page, per_page)

    @staticmethod
    async def find_by_id(db: AsyncSession, usuario_id: int) -> UsuarioModel:
        usuario = await UsuarioRepository.find_by_id(db, usuario_id, with_relations=True)

        if usuario is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

        return usuario

    @staticmethod
    async def update(db: AsyncSession, usuario_id: int, data: UsuarioUpdateSchema, current_user_id: int) -> UsuarioModel:  
        if current_user_id == usuario_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não é permitido editar o usuário da conta autenticada.")

        usuario = await UsuarioRepository.find_by_id(db=db, usuario_id=usuario_id, with_relations=True)

        if usuario is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

        try:
            # ---------------------------------
            # E-MAIL
            # ---------------------------------

            if (data.email is not None and str(data.email) != usuario.email):
                usuario_email = await UsuarioRepository.find_by_email(db, str(data.email))

                if (usuario_email is not None and usuario_email.id != usuario.id):
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um usuário cadastrado com este e-mail.")

            usuario_values = {}

            # ---------------------------------
            # ENDEREÇO
            # ---------------------------------

            if data.endereco is not None:
                endereco_atual = usuario.endereco

                endereco_values = {
                    "logradouro": endereco_atual.logradouro,
                    "numero": endereco_atual.numero,
                    "complemento": endereco_atual.complemento,
                    "cep": endereco_atual.cep,
                    "bairro": endereco_atual.bairro,
                    "municipio_id": endereco_atual.municipio_id
                }

                endereco_values.update(data.endereco.model_dump(exclude_unset=True))

                novo_endereco_data = EnderecoCreateSchema(**endereco_values)

                endereco = await EnderecoRepository.find_by_data(db, novo_endereco_data)

                if endereco is None:
                    endereco = await EnderecoRepository.create(db, novo_endereco_data)

                usuario_values["endereco_id"] = endereco.id
                usuario.endereco = endereco

            # ---------------------------------
            # CONTATO
            # ---------------------------------

            if data.contato is not None:
                contato_atual = usuario.contato

                contato_values = {
                    "cod_pais": contato_atual.cod_pais,
                    "ddd": contato_atual.ddd,
                    "numero": contato_atual.numero
                }

                contato_values.update(data.contato.model_dump(exclude_unset=True))

                novo_contato_data = ContatoCreateSchema(**contato_values)

                contato = await ContatoRepository.find_by_data(db, novo_contato_data)

                if contato is None:
                    contato = await ContatoRepository.create(db, novo_contato_data)

                usuario_values["contato_id"] = contato.id
                usuario.contato = contato

            # ---------------------------------
            # USUÁRIO
            # ---------------------------------

            if data.nome is not None:
                usuario_values["nome"] = data.nome

            if data.email is not None:
                usuario_values["email"] = str(data.email)

            if data.password is not None:
                usuario_values["password"] = get_password_hash(data.password)

            if data.nivel_acesso is not None:
                usuario_values["nivel_acesso"] = data.nivel_acesso

            if usuario_values:
                await UsuarioRepository.update(db, usuario, usuario_values)

            await db.commit()

            return await UsuarioService.find_by_id(db, usuario_id)

        except HTTPException:
            await db.rollback()
            raise

        except IntegrityError:
            await db.rollback()

            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar o usuário. Verifique os dados informados.")

        except Exception:
            await db.rollback()
            raise
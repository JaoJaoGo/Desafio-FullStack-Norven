from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import NivelAcessoEnum
from core.security import get_password_hash

from models.usuario_model import UsuarioModel

from repositories.contato_repository import ContatoRepository
from repositories.endereco_repository import EnderecoRepository
from repositories.usuario_repository import UsuarioRepository

from schemas.usuario_schema import UsuarioCreateSchema

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

            password_hash = get_password_hash(data.password)

            usuario = await UsuarioRepository.create(
                db=db,
                nome=data.nome,
                email=data.email,
                password_hash=password_hash,
                nivel_acesso=NivelAcessoEnum.USER,
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
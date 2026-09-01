from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.contato_repository import ContatoRepository
from repositories.endereco_repository import EnderecoRepository
from repositories.fornecedor_repository import FornecedorRepository
from schemas.contato_schema import ContatoCreateSchema
from schemas.endereco_schema import EnderecoCreateSchema
from schemas.fornecedor_schema import FornecedorCreateSchema, FornecedorUpdateSchema

class FornecedorService:
    @staticmethod
    async def create(db: AsyncSession, data: FornecedorCreateSchema):
        try:
            existente = await FornecedorRepository.find_by_cnpj(db, data.cnpj)
            if existente:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe fornecedor com este CNPJ")

            endereco = await EnderecoRepository.find_by_data(db, data.endereco)
            if endereco is None:
                endereco = await EnderecoRepository.create(db, data.endereco)

            contato = await ContatoRepository.find_by_data(db, data.contato)
            if contato is None:
                contato = await ContatoRepository.create(db, data.contato)

            fornecedor = await FornecedorRepository.create(db=db, nome=data.nome, cnpj=data.cnpj, endereco_id=endereco.id, contato_id=contato.id)

            await db.commit()

            return await FornecedorService.find_by_id(db, fornecedor.id)
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar fornecedor")
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def find_by_id(db: AsyncSession, fornecedor_id: int):
        fornecedor = await FornecedorRepository.find_by_id(db, fornecedor_id, with_relations=True)

        if fornecedor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado.")
        
        return fornecedor

    @staticmethod
    async def list(db: AsyncSession, search: str, page: int, per_page: int):
        return await FornecedorRepository.list(db, search, page, per_page)

    @staticmethod
    async def update(db: AsyncSession, fornecedor_id: int, data: FornecedorUpdateSchema):
        fornecedor = await FornecedorRepository.find_by_id(db, fornecedor_id, with_relations=True)
        if fornecedor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado.")

        try:
            values = {}

            if data.nome is not None:
                values["nome"] = data.nome

            if data.cnpj is not None and data.cnpj != fornecedor.cnpj:
                existente = await FornecedorRepository.find_by_cnpj(db, data.cnpj)

                if existente:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe fornecedor com este CNPJ")

                values['cnpj'] = data.cnpj

            if data.endereco is not None:
                endereco_values = {
                    "logradouro":
                        fornecedor.endereco.logradouro,
                    "numero":
                        fornecedor.endereco.numero,
                    "complemento":
                        fornecedor.endereco.complemento,
                    "cep":
                        fornecedor.endereco.cep,
                    "bairro":
                        fornecedor.endereco.bairro,
                    "municipio_id":
                        fornecedor.endereco.municipio_id,
                }

                endereco_values.update(data.endereco.model_dump(exclude_none=True))

                endereco_data = EnderecoCreateSchema(**endereco_values)

                endereco = await EnderecoRepository.find_by_data(db, endereco_data)

                if endereco is None:
                    endereco = await EnderecoRepository.create(db, endereco_data)

                values["endereco_id"] = endereco.id
                fornecedor.endereco = endereco

            if data.contato is not None:
                contato_values = {
                    "cod_pais":
                        fornecedor.contato.cod_pais,
                    "ddd":
                        fornecedor.contato.ddd,
                    "numero":
                        fornecedor.contato.numero,
                }

                contato_values.update(
                    data.contato.model_dump(
                        exclude_unset=True
                    )
                )

                contato_data = ContatoCreateSchema(**contato_values)

                contato = await ContatoRepository.find_by_data(db, contato_data)

                if contato is None:
                    contato = await ContatoRepository.create(db, contato_data)

                values["contato_id"] = contato.id
                fornecedor.contato = contato

            if values:
                await FornecedorRepository.update(db, fornecedor, values)
            
            await db.commit()

            return await FornecedorRepository.find_by_id(db, fornecedor.id)
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar o fornecedor.")
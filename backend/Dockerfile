FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# Copia primeiro apenas os arquivos de dependências
COPY pyproject.toml uv.lock ./

# Instala dependências sem tentar instalar o projeto ainda
RUN uv sync --frozen --no-install-project

# Agora copia o código da aplicação
COPY . .

# Agora o projeto já existe dentro da imagem e pode ser instalado
RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "desafio_fullstack_norven.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
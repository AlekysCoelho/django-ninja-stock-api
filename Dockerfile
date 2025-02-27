FROM python:3.13-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash appuser

# Definir diretório de trabalho
WORKDIR /src

# Instalar Poetry
RUN pip install poetry

# Copiar os arquivos do Poetry primeiro para otimizar cache
COPY pyproject.toml /src/
COPY poetry.lock /src/

# Instalar dependências sem criar ambiente virtual
RUN poetry config virtualenvs.create false && poetry install --no-root --with dev && poetry sync

# Copiar o restante do código para manter a estrutura correta
COPY app /src/app/
COPY tests /src/tests/
COPY manage.py /src/

# Ajustar permissões para o usuário não-root
RUN chown -R appuser:appuser /src

# Trocar para o usuário não-root
USER appuser

# Expor a porta do Django
EXPOSE 8000

# Comando de inicialização
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
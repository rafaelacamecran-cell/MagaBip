# Use uma imagem base oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instale as dependências do sistema necessárias para o psycopg2 e outras libs
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto
COPY . .

# Define as variáveis de ambiente padrão
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expõe a porta que o app vai rodar
EXPOSE 80

# Torna o script de entrada executável
RUN chmod +x entrypoint.sh

# Define o script de entrada
ENTRYPOINT ["./entrypoint.sh"]

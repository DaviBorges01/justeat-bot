# Usar a imagem oficial do Python
FROM python:3.9

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos para dentro do container
COPY . /app/

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta 8000
EXPOSE 8000

# Comando para rodar o bot
CMD ["uvicorn", "Justeat_Bot:app", "--host", "0.0.0.0", "--port", "8000"]

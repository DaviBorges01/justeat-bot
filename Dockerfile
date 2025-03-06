# Usar a imagem oficial do Python
FROM python:3.9

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y     wget     unzip     curl     chromium     chromium-driver     libglib2.0-0     libnss3     libgconf-2-4     libxi6     libxrender1     libxtst6     libxss1     fonts-liberation     libappindicator3-1     xdg-utils     && apt-get clean

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos para dentro do container
COPY . /app/

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta 8000
EXPOSE 8000

# Comando para rodar o bot
CMD ["uvicorn", "Justeat_Bot:app", "--host", "0.0.0.0", "--port", "8000"]

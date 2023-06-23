# Use uma imagem base do Python
FROM python:3.9

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o conteúdo do diretório atual para o diretório de trabalho no contêiner
COPY . .

# Exponha a porta que o Flask está usando
EXPOSE 5000

# Comando para executar o aplicativo Flask
CMD ["python", "main.py"]
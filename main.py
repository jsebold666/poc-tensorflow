from datetime import datetime
import requests
import vertexai
from vertexai.preview.language_models import TextGenerationModel
from bs4 import BeautifulSoup
import json
import logging
import re
from collections import defaultdict
import html
import unicodedata
from flask import make_response
from flask import Flask
from flask_cors import CORS
from google.cloud import bigquery
import textwrap
import pandas as pd

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

def conectar_e_prever(tenantId, text):
    # Crie uma instância do cliente BigQuery
    client = bigquery.Client()

    # Defina a consulta SQL
    query = """
    SELECT input_text, output_text FROM `gglobo-hd-builder-ai-hdg-prd.multicontent_sample.multicontent_context` 
    WHERE LENGTH(output_text) >= 10
    """

    query_job = client.query(query)
    df_exemplers = query_job.to_dataframe()
    def wrap(s):
        return '\n'.join(textwrap.wrap(s))

    # Extraia os exemplos do DataFrame
    exemplers = [f'input_text: {input_text} \noutput_text: {output_text.strip()}'
                 for input_text, output_text in df_exemplers.head(5).values]
    exemplers = '\n\n'.join(exemplers)

    # Defina outras variáveis necessárias
    tenantid = tenantId
    body = text

    prompt = f"{exemplers} \n\nbody content: {body} \n context: this content is from {tenantid}, \noutput_text: "

    return f"{wrap(str(prompt))}"

def insert_subpath(url, subpath):
    pattern = r"(https?://(?:\w+\.)*(?:globo\.com(?:\.br)?|br))(?:/|$)"
    return re.sub(pattern, r"\1" + subpath + "/", url)

def scrapperText(url):
    try:
        transformed_url = insert_subpath(url, "/globo/raw")

        # Do request
        json_data = requests.get(transformed_url).json()
        # 'materias' or 'video', etc.
        if 'resource' in json_data:
            # Get tenantId from url
            tenantId = (html.unescape(json_data['resource']['tenantId']))

            # Get body from url
            body = ". ".join([
                unicodedata.normalize('NFKD', html.unescape(text['text'])).encode('ASCII', 'ignore').decode()
                if 'text' in text else None
                for text in json_data['resource']['bodyData']['blocks']
            ])
        else:
            # Get tenantId from url
            tenantId = (json_data['feedData']['tenantId'])

            # Get body from url
            body = (json_data['mainContent']['description'])

        return body, tenantId
    except:
        return None

def title_generation(mensagem, tenantId, temperature: float = 0.7) -> None:
    logging.info('Iniciando o teste')
    text_model = TextGenerationModel.from_pretrained("text-bison@001")

    # TODO developer - override these parameters as needed:
    parameters = {
        "temperature": temperature,  # Temperature controls the degree of randomness in token selection.
        "max_output_tokens": 15,  # Token limit determines the maximum amount of text output.
        "top_p": 0.95,  # Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.
        "top_k": 40,  # A top_k of 1 means the selected token is the most probable among all tokens.
    }
    logging.info('send model')
    prompt = conectar_e_prever(mensagem, tenantId)
    title = text_model.predict(
            prompt,
        **parameters
    )
    
    
    logging.info('send response from vertex')
    return title.text

def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    logging.info(request_json)
    url = request_json['url']
    mensagem, tenantId = scrapperText(url)
    resp = title_generation(mensagem, tenantId)
    resp_normalized = unicodedata.normalize('NFKD', resp).encode('ASCII', 'ignore').decode()
     # Criar a resposta
    res = {"title_response": resp_normalized}
    response = make_response(json.dumps(res))
    
    # Adicionar cabeçalhos CORS
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    return response
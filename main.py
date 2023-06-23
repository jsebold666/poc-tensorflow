from datetime import datetime
import requests
import vertexai
from vertexai.preview.language_models import TextGenerationModel
import requests
from bs4 import BeautifulSoup
import json
import logging
import re
from collections import defaultdict
import html
import unicodedata

logging.basicConfig(level=logging.INFO)

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
            ##tenantId = (json_data['feedData']['tenantId'])

            # Get body from url
            body = (json_data['mainContent']['description'])

        return body
    except:
        return None

def title_generation(mensagem, temperature: float = 0.7) -> None:
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
    title = text_model.predict(
         """ Criar títulos de matérias para a globo.com

            Article: Yellowstone National Park is an American national park located in the western United States, largely in the northwest corner of Wyoming and extending into Montana and Idaho. It was established by the 42nd U.S. Congress with the Yellowstone National Park Protection Act and signed into law by President Ulysses S. Grant on March 1, 1872. Yellowstone was the first national park in the U.S. and is also widely held to be the first national park in the world. The park is known for its wildlife and its many geothermal features, especially the Old Faithful geyser, one of its most popular. While it represents many types of biomes, the subalpine forest is the most abundant. It is part of the South Central Rockies forests ecoregion.
            The title of above article can be: Yellowstone National Park: A Natural Wonder

            Article: As many businesses figure out new ways to go digital, one thing is clear: talent continues to be one of the key ways to enable an inclusive digital economy. Employers in Asia Pacific list technology as the leading in-demand skill, with digital marketing and e-commerce following close behind. Simultaneously, many people are looking to learn new skills that will help them meet the requirements of the evolving job market. So we must create new ways to help businesses and job seekers alike.
            The title of above article can be: How to Prepare for the Digital Economy

            Article: STEM Minds empowers K-12 students worldwide to reach their full potential as self-directed, life-long learners. As we grow our team, we\'ll continue to work closely with Google for Startups experts and Google for Startups Accelerator Canada advisors to further expand our AI/ML tech stack, develop additional educational solutions, and launch STEM Minds in new markets.
            The title of above article can be: STEM Minds: Empowering K-12 Students Worldwide

            Article: Acostumado a frases polêmicas e ataques a tribunais, o ex-presidente Jair Bolsonaro adotou uma postura diferente nas semanas que precederam o julgamento que pode torná-lo inelegível. Orientado por advogados e assessores, ele chegou a pedir desculpas por desinformação sobre a vacina contra a Covid-19, manteve um tom respeitoso em relação ao relator do caso, Benedito Gonçalves, e evitou criticar a indicação de Cristiano Zanin ao Supremo Tribunal Federal (STF) — seu partido, o PL, liberou a bancada, com anuência do ex-titular do Palácio do Planalto. Ao visitar o Senado ontem, porém, Bolsonaro fugiu do roteiro alinhado e adotou o que integrantes do PL classificaram como "estratégia kamikaze", como mostrou a colunista Bela Megale.
            The title of above article can be: Bolsonaro viaja durante julgamento, e aliados tentam conter novos ataques ao TSE 

            Article: """ + mensagem + """\n     The title of above article can be:""",
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
    mensagem = scrapperText(url)
    resp = title_generation(mensagem)
    res = {"title_response": resp }
    return res
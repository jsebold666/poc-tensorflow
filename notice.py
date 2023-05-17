from flask import Flask, render_template
import tensorflow as tf

app = Flask(__name__)

class Noticia:
    def __init__(self, nome, titulo, imagem, link):
        self.nome = nome
        self.titulo = titulo
        self.imagem = imagem
        self.link = link
        self.cliques = 0

    def registrar_clique(self):
        self.cliques += 1

def obter_lista_noticias():
    # Mock das notícias
    noticias = []
    noticias.append(Noticia("Notícia 1", "Título 1", "imagem1.jpg", "https://www.example.com/noticia1"))
    noticias.append(Noticia("Notícia 2", "Título 2", "imagem2.jpg", "https://www.example.com/noticia2"))
    noticias.append(Noticia("Notícia 3", "Título 3", "imagem3.jpg", "https://www.example.com/noticia3"))

    return noticias

@app.route('/')
def exibir_noticias():
    noticias = obter_lista_noticias()

    # Extrair características e cliques das notícias
    caracteristicas = []
    cliques = []

    for noticia in noticias:
        caracteristicas.append([noticia.titulo, noticia.imagem])  # Adaptar para suas características relevantes
        cliques.append(noticia.cliques)

    # Pré-processar características (converter texto em representações numéricas)

    # Construir e treinar o modelo do TensorFlow
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(numero_de_caracteristicas,)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    model.fit(caracteristicas, cliques, epochs=10, batch_size=32)

    return render_template('noticias.html', noticias=noticias)


@app.route('/clique/<int:noticia_id>')
def registrar_clique(noticia_id):
    noticias = obter_lista_noticias()
    noticia = noticias[noticia_id]
    noticia.registrar_clique()

    # Atualizar o modelo do TensorFlow com o novo clique

    return 'Clique registrado com sucesso!'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
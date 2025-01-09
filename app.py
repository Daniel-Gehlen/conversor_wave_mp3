from flask import Flask, request, jsonify, send_file, render_template
import ffmpeg
import os
import tempfile
from threading import Thread

# Configuração do Flask
app = Flask(__name__)

# Pasta temporária para armazenar as partes do arquivo
UPLOAD_FOLDER = tempfile.mkdtemp()

# Rota principal para servir o frontend
@app.route('/')
def index():
    return render_template('index.html')  # Serve o arquivo index.html

# Rota para receber partes do arquivo
@app.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    file = request.files['file']
    chunk_index = int(request.form['chunkIndex'])
    total_chunks = int(request.form['totalChunks'])
    file_name = request.form['fileName']

    # Salva a parte do arquivo em um arquivo temporário
    chunk_path = os.path.join(UPLOAD_FOLDER, f'{file_name}.part{chunk_index}')
    file.save(chunk_path)

    return jsonify({"message": "Parte recebida com sucesso."})

# Função assíncrona para converter o arquivo
def convert_async(file_name, total_chunks):
    try:
        # Reúne as partes do arquivo
        full_file_path = os.path.join(UPLOAD_FOLDER, f'{file_name}.full')
        with open(full_file_path, 'wb') as full_file:
            for i in range(total_chunks):
                chunk_path = os.path.join(UPLOAD_FOLDER, f'{file_name}.part{i}')
                with open(chunk_path, 'rb') as chunk_file:
                    full_file.write(chunk_file.read())

        # Converte o arquivo WAV para MP3
        mp3_path = os.path.join(UPLOAD_FOLDER, f'{os.path.splitext(file_name)[0]}.mp3')
        (
            ffmpeg
            .input(full_file_path)
            .output(mp3_path, format='mp3')
            .run()
        )

        # Limpa os arquivos temporários
        os.remove(full_file_path)
        for i in range(total_chunks):
            os.remove(os.path.join(UPLOAD_FOLDER, f'{file_name}.part{i}'))

    except Exception as e:
        print(f"Erro ao converter o arquivo: {e}")

# Rota para iniciar a conversão
@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    file_name = data['fileName']
    total_chunks = data['totalChunks']

    # Inicia a conversão em uma thread separada
    thread = Thread(target=convert_async, args=(file_name, total_chunks))
    thread.start()

    return jsonify({"message": "Conversão iniciada."})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, request, jsonify, send_file
import ffmpeg
import io

# Configuração do Flask
app = Flask(__name__)

# Rota para receber partes do arquivo
@app.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    file = request.files['file']
    chunk_index = int(request.form['chunkIndex'])
    total_chunks = int(request.form['totalChunks'])
    file_name = request.form['fileName']

    # Armazena a parte do arquivo em memória
    chunk_data = file.read()

    # Aqui você pode armazenar as partes em uma lista global (não recomendado para produção)
    # Ou usar um banco de dados em memória como Redis (gratuito para pequenos volumes)
    # Para este exemplo, vamos simular o processo
    if not hasattr(app, 'chunks'):
        app.chunks = {}
    app.chunks[f'{file_name}.part{chunk_index}'] = chunk_data

    return jsonify({"message": "Parte recebida com sucesso."})

# Rota para converter o arquivo completo
@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    file_name = data['fileName']

    # Cria um buffer em memória para o arquivo completo
    full_file = io.BytesIO()

    # Reúne as partes do arquivo em memória
    for i in range(total_chunks):
        chunk_key = f'{file_name}.part{i}'
        if chunk_key in app.chunks:
            full_file.write(app.chunks[chunk_key])
        else:
            return jsonify({"error": f"Parte {i} do arquivo não encontrada."}), 400

    # Converte o arquivo WAV para MP3 (usando ffmpeg)
    try:
        # Salva o arquivo completo em um buffer temporário
        full_file.seek(0)  # Volta ao início do buffer
        with io.BytesIO() as mp3_buffer:
            (
                ffmpeg
                .input('pipe:0')  # Lê da entrada padrão (buffer)
                .output('pipe:1', format='mp3')  # Escreve na saída padrão (buffer)
                .run(input=full_file.read(), capture_stdout=True, capture_stderr=True)
            )

            # Envia o arquivo MP3 como download
            mp3_buffer.seek(0)
            return send_file(mp3_buffer, as_attachment=True, download_name=f'{os.path.splitext(file_name)[0]}.mp3')

    except ffmpeg.Error as e:
        return jsonify({"error": f"Erro ao converter o arquivo: {e.stderr.decode()}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
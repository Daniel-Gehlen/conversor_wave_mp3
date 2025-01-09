from flask import Flask, request, jsonify, send_file
import os
import tempfile
import shutil

app = Flask(__name__)

# Pasta temporária para armazenar partes do arquivo
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Rota para receber partes do arquivo
@app.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    file = request.files['file']
    chunk_index = int(request.form['chunkIndex'])
    total_chunks = int(request.form['totalChunks'])
    file_name = request.form['fileName']

    # Salva a parte do arquivo
    chunk_path = os.path.join(UPLOAD_FOLDER, f'{file_name}.part{chunk_index}')
    file.save(chunk_path)

    return jsonify({"message": "Parte recebida com sucesso."})

# Rota para converter o arquivo completo
@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    file_name = data['fileName']

    # Reúne as partes do arquivo
    output_path = os.path.join(UPLOAD_FOLDER, file_name)
    with open(output_path, 'wb') as output_file:
        for i in range(total_chunks):
            chunk_path = os.path.join(UPLOAD_FOLDER, f'{file_name}.part{i}')
            with open(chunk_path, 'rb') as chunk_file:
                output_file.write(chunk_file.read())
            os.remove(chunk_path)  # Remove a parte após a junção

    # Converte o arquivo WAV para MP3 (usando ffmpeg)
    mp3_path = os.path.join(UPLOAD_FOLDER, f'{os.path.splitext(file_name)[0]}.mp3')
    try:
        (
            ffmpeg
            .input(output_path)
            .output(mp3_path)
            .run()
        )
    except ffmpeg.Error as e:
        return jsonify({"error": f"Erro ao converter o arquivo: {e.stderr.decode()}"}), 500

    # Envia o arquivo MP3 como download
    return send_file(mp3_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
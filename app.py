from flask import Flask, request, jsonify, send_file
import ffmpeg
import io
import os
import tempfile

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

    # Retorna uma resposta simples
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
        # Aqui você precisaria de uma maneira de acessar as partes armazenadas
        # Como estamos usando memória, você pode armazenar as partes em uma lista global (não recomendado para produção)
        # Ou usar um banco de dados em memória como Redis (gratuito para pequenos volumes)
        # Para este exemplo, vamos simular o processo
        chunk_data = b''  # Substitua isso pelos dados reais da parte
        full_file.write(chunk_data)

    # Converte o arquivo WAV para MP3 (usando ffmpeg)
    try:
        # Salva o arquivo completo em um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_wav:
            tmp_wav.write(full_file.getvalue())
            tmp_wav_path = tmp_wav.name

        # Converte o arquivo WAV para MP3
        mp3_path = tmp_wav_path.replace('.wav', '.mp3')
        (
            ffmpeg
            .input(tmp_wav_path)
            .output(mp3_path)
            .run()
        )

        # Envia o arquivo MP3 como download
        return send_file(mp3_path, as_attachment=True)

    except ffmpeg.Error as e:
        return jsonify({"error": f"Erro ao converter o arquivo: {e.stderr.decode()}"}), 500

    finally:
        # Remove os arquivos temporários
        if os.path.exists(tmp_wav_path):
            os.remove(tmp_wav_path)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
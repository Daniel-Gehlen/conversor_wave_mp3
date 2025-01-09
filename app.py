from flask import Flask, render_template, request, send_file, jsonify
from pydub import AudioSegment
import os
import tempfile
import shutil

# Configuração do Flask
app = Flask(__name__, template_folder=".", static_folder=".")

# Função para converter WAV para MP3
def convert_wav_to_mp3(wav_path, mp3_path):
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3")

# Rota principal
@app.route("/")
def index():
    return render_template("index.html")

# Rota para servir arquivos estáticos (CSS e JS)
@app.route("/<filename>")
def static_files(filename):
    return app.send_static_file(filename)

# Rota para conversão
@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    # Verifica o tamanho do arquivo (4.5 MB)
    max_size = 4.5 * 1024 * 1024  # 4.5 MB em bytes
    if request.content_length > max_size:
        return jsonify({"error": "O arquivo é muito grande. O tamanho máximo permitido é 4.5 MB."}), 413

    # Cria um diretório temporário
    tmpdir = tempfile.mkdtemp()
    try:
        wav_path = os.path.join(tmpdir, file.filename)
        mp3_filename = f"{os.path.splitext(file.filename)[0]}.mp3"
        mp3_path = os.path.join(tmpdir, mp3_filename)

        # Salva o WAV no diretório temporário
        file.save(wav_path)

        # Converte o WAV para MP3
        convert_wav_to_mp3(wav_path, mp3_path)

        # Envia o arquivo MP3 como download
        response = send_file(
            mp3_path,
            as_attachment=True,
            download_name=mp3_filename,
            mimetype="audio/mpeg"
        )

        # Fecha o arquivo explicitamente após o envio
        response.call_on_close(lambda: shutil.rmtree(tmpdir, ignore_errors=True))
        return response

    except Exception as e:
        # Remove o diretório temporário em caso de erro
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify({"error": f"Erro durante a conversão: {str(e)}"}), 500

# Inicia o servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
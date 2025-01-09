## **Conversor de WAVE para MP3**

Esta é uma aplicação Flask que converte arquivos de áudio WAVE (WAV) para MP3. O usuário pode fazer upload de um arquivo WAV, e a aplicação gera um arquivo MP3 para download.

---

## **Estrutura do Projeto**

```
conversor_wave_mp3/
│
├── app.py                # Código fonte principal (Flask + lógica de conversão)
├── index.html            # Interface do usuário (HTML)
├── styles.css            # Estilos (CSS)
├── script.js             # Lógica do frontend (JavaScript)
├── requirements.txt      # Dependências do projeto
├── vercel.json           # Configuração do deploy na Vercel
└── README.md             # Documentação do projeto (este arquivo)
```

---

## **Dependências**

As dependências do projeto estão listadas no arquivo `requirements.txt`:

```plaintext
Flask==3.1.0
pydub==0.25.1
ffmpeg-python==0.2.0
```

---

## **Instalação e Execução**

### **1. Clone o repositório**
Se você estiver usando Git, clone o repositório:

```bash
git clone https://github.com/seu-usuario/conversor_wave_mp3.git
cd conversor_wave_mp3
```

### **2. Crie um ambiente virtual**
Crie um ambiente virtual para isolar as dependências do projeto:

```bash
python -m venv venv
```

### **3. Ative o ambiente virtual**
- No Windows:
  ```bash
  venv\Scripts\activate
  ```

- No Linux/macOS:
  ```bash
  source venv/bin/activate
  ```

### **4. Instale as dependências**
Instale as dependências listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### **5. Execute a aplicação**
Execute o Flask para iniciar a aplicação:

```bash
python app.py
```

A aplicação estará disponível em `http://127.0.0.1:5000/`.

---

## **Códigos Completos**

### **1. `app.py`**
```python
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
    app.run(debug=True)
```

---

### **2. `index.html`**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversor de WAVE para MP3</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Conversor de WAVE para MP3</h1>
        <form id="uploadForm">
            <input type="file" id="fileInput" accept="audio/wav" required>
            <div class="progress-bar">
                <div class="progress" id="progressBar"></div>
            </div>
            <button type="submit" id="convertButton">Converter</button>
        </form>
        <p id="status"></p>
    </div>

    <script src="script.js"></script>
</body>
</html>
```

---

### **3. `styles.css`**
```css
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
}

.container {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    text-align: center;
    width: 300px;
}

h1 {
    margin-bottom: 20px;
}

.progress-bar {
    width: 100%;
    background-color: #e0e0e0;
    border-radius: 5px;
    overflow: hidden;
    margin-bottom: 20px;
}

.progress {
    width: 0%;
    height: 10px;
    background-color: #76c7c0;
    transition: width 0.3s ease;
}

button {
    background-color: #76c7c0;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}

button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}
```

---

### **4. `script.js`**
```javascript
const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const convertButton = document.getElementById('convertButton');
const progressBar = document.getElementById('progressBar');
const statusText = document.getElementById('status');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];

    if (!file) {
        alert('Selecione um arquivo WAV.');
        return;
    }

    convertButton.disabled = true;
    statusText.textContent = "Convertendo...";
    progressBar.style.width = "0%";

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro desconhecido');
        }

        // Simula uma barra de progresso
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            progressBar.style.width = `${progress}%`;
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 300);

        // Faz o download do arquivo
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name.replace('.wav', '.mp3');
        a.click();
        window.URL.revokeObjectURL(url);

        statusText.textContent = "Conversão concluída!";
    } catch (error) {
        statusText.textContent = `Erro: ${error.message}`;
    } finally {
        convertButton.disabled = false;
    }
});
```

---

### **5. `vercel.json`**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

---

## **Aspectos Técnicos**

### **Tecnologias Utilizadas**
- **Flask**: Framework web em Python para criar a aplicação.
- **Pydub**: Biblioteca para manipulação de áudio.
- **FFmpeg**: Biblioteca para conversão de formatos de áudio.
- **HTML/CSS/JavaScript**: Interface do usuário e interações no frontend.
- **Vercel**: Plataforma para deploy da aplicação.

### **Funcionalidades**
- Upload de arquivos WAV.
- Conversão de WAV para MP3.
- Download do arquivo MP3 gerado.
- Barra de progresso simulada no frontend.

### **Requisitos do Sistema**
- Python 3.7 ou superior.
- Dependências listadas no `requirements.txt`.
- FFmpeg instalado no sistema (necessário para o Pydub).

---

## **Como Contribuir**
1. Faça um fork do repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`).
4. Faça push para a branch (`git push origin feature/nova-feature`).
5. Abra um pull request.

---

## **Licença**
Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## **Notas Adicionais**
- Certifique-se de que o FFmpeg está instalado e configurado corretamente no seu sistema para que o Pydub funcione adequadamente.
- Para instalar o FFmpeg, siga as instruções no site oficial: [FFmpeg](https://ffmpeg.org/download.html).
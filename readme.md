# Conversor de WAVE para MP3

Este projeto é um conversor de arquivos de áudio WAVE para MP3, desenvolvido com Flask (Python) e implantado na Vercel. Ele permite que os usuários façam upload de arquivos WAVE, convertam-nos para MP3 e façam o download do arquivo convertido.

---

## Tecnologias Utilizadas

- **Flask**: Framework web em Python para criar a aplicação.
- **FFmpeg**: Biblioteca para conversão de áudio.
- **Vercel**: Plataforma de implantação serverless.
- **HTML/CSS/JavaScript**: Frontend para interface do usuário.
- **Gunicorn**: Servidor WSGI para produção.

---

## Estrutura do Projeto

```
conversor_wave_mp3/
│
├── api/                  # Pasta para funções serverless (opcional)
│   └── convert.js        # Exemplo de função serverless
├── app.py                # Código principal do Flask
├── build.sh              # Script de build (opcional)
├── readme.md             # Este arquivo
├── requirements.txt      # Dependências do projeto
├── static/               # Pasta para arquivos estáticos
│   ├── favicon.ico       # Ícone do site
│   ├── script.js         # Lógica do frontend
│   └── styles.css        # Estilos CSS
├── templates/            # Pasta para templates HTML
│   └── index.html        # Página principal
├── vercel.json           # Configuração do deploy na Vercel
└── wsgi.py               # Arquivo WSGI para produção
```

---

## Funcionalidades

1. **Upload de Arquivos WAVE**: Os usuários podem fazer upload de arquivos WAVE.
2. **Conversão para MP3**: O arquivo WAVE é convertido para MP3 usando FFmpeg.
3. **Download do Arquivo Convertido**: O usuário pode fazer o download do arquivo MP3 convertido.

---

## Passo a Passo para Criar o Projeto

### 1. **Configuração do Ambiente**

#### Criar o Diretório do Projeto
```bash
mkdir conversor_wave_mp3
cd conversor_wave_mp3
```

#### Criar um Ambiente Virtual (venv)
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

#### Instalar Dependências
Crie um arquivo `requirements.txt` com as seguintes dependências:

```txt
Flask==2.3.2
ffmpeg-python==0.2.0
gunicorn==20.1.0
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

---

### 2. **Código do Projeto**

#### `app.py`
```python
from flask import Flask, render_template, request, jsonify, send_file
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
    return render_template('index.html')

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
```

#### `wsgi.py`
```python
from app import app

if __name__ == "__main__":
    app.run()
```

#### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "wsgi.py"
    }
  ]
}
```

#### `templates/index.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversor de WAVE para MP3</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
</head>
<body>
    <div class="container">
        <h1>Conversor de WAVE para MP3</h1>
        <form id="uploadForm">
            <input type="file" id="fileInput" accept="audio/wav" required>
            <button type="submit" id="convertButton">Converter</button>
        </form>
        <p id="status"></p>
    </div>

    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
```

#### `static/script.js`
```javascript
document.getElementById('uploadForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/convert', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'converted.mp3';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Erro:', error);
    });
});
```

#### `static/styles.css`
```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f0f0f0;
}

.container {
    background-color: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    text-align: center;
}

h1 {
    margin-bottom: 20px;
}

input[type="file"] {
    margin-bottom: 20px;
}

button {
    padding: 10px 20px;
    background-color: #007bff;
    color: #fff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}
```

---

### 3. **Implantação na Vercel**

1. **Instale a CLI da Vercel:**
   ```bash
   npm install -g vercel
   ```

2. **Faça o Login na Vercel:**
   ```bash
   vercel login
   ```

3. **Faça o Deploy:**
   ```bash
   vercel --prod
   ```

---

### 4. **Testes**

- Acesse a URL fornecida pela Vercel.
- Faça upload de um arquivo WAVE e verifique se a conversão para MP3 funciona corretamente.

---

## Licença

Este projeto está licenciado sob a MIT License. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

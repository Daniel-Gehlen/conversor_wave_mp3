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

    // Tamanho máximo de cada parte (50 MB)
    const chunkSize = 50 * 1024 * 1024; // 50 MB em bytes
    const totalChunks = Math.ceil(file.size / chunkSize);

    convertButton.disabled = true;
    statusText.textContent = "Convertendo...";
    progressBar.style.width = "0%";

    try {
        // Envia cada parte do arquivo
        for (let i = 0; i < totalChunks; i++) {
            const start = i * chunkSize;
            const end = Math.min(start + chunkSize, file.size);
            const chunk = file.slice(start, end);

            const formData = new FormData();
            formData.append('file', chunk);
            formData.append('chunkIndex', i);
            formData.append('totalChunks', totalChunks);
            formData.append('fileName', file.name);

            const response = await fetch('/upload-chunk', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erro ao enviar parte do arquivo.');
            }

            // Atualiza a barra de progresso
            const progress = ((i + 1) / totalChunks) * 100;
            progressBar.style.width = `${progress}%`;
        }

        // Solicita a conversão do arquivo completo
        const convertResponse = await fetch('/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ fileName: file.name, totalChunks: totalChunks }),
        });

        if (!convertResponse.ok) {
            const errorData = await convertResponse.json();
            throw new Error(errorData.error || 'Erro ao converter o arquivo.');
        }

        // Faz o download do arquivo MP3 convertido
        const blob = await convertResponse.blob();
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
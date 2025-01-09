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
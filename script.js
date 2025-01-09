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

    // Desabilita o botão de conversão e exibe o status
    convertButton.disabled = true;
    statusText.textContent = "Convertendo...";
    progressBar.style.width = "0%";

    // Cria um objeto FormData para enviar o arquivo
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Envia o arquivo para o backend
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData,
        });

        // Verifica se a resposta foi bem-sucedida
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

        // Faz o download do arquivo MP3 convertido
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name.replace('.wav', '.mp3');
        a.click();
        window.URL.revokeObjectURL(url);

        // Exibe mensagem de conclusão
        statusText.textContent = "Conversão concluída!";
    } catch (error) {
        // Exibe mensagem de erro
        statusText.textContent = `Erro: ${error.message}`;
    } finally {
        // Reabilita o botão de conversão
        convertButton.disabled = false;
    }
});
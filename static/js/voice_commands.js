/**
 * MagaBip Hands-free Voice System
 * Permite comandos por voz para retirada e devolução.
 */

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.continuous = false;
    recognition.interimResults = false;

    window.startVoiceCommand = function () {
        recognition.start();
        const btn = document.getElementById('voice-btn');
        if (btn) btn.classList.add('btn-danger', 'animate-pulse');
        console.log("Ouvindo...");
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript.toLowerCase();
        console.log("Comando reconhecido:", transcript);
        processVoiceCommand(transcript);
        resetVoiceBtn();
    };

    recognition.onerror = function (event) {
        console.error("Erro no reconhecimento:", event.error);
        resetVoiceBtn();
    };

    recognition.onend = function () {
        resetVoiceBtn();
    };

    function resetVoiceBtn() {
        const btn = document.getElementById('voice-btn');
        if (btn) btn.classList.remove('btn-danger', 'animate-pulse');
    }

    function processVoiceCommand(text) {
        // Exemplos de comandos: 
        // "Retirar coletor 05"
        // "Devolver equipamento"
        // "Abrir chamado"

        if (text.includes("retirar")) {
            const match = text.match(/\d+/);
            if (match) {
                const deviceNum = match[0];
                alert(`Tentando retirar equipamento com número ${deviceNum}...`);
                // Aqui você pode disparar uma busca na página pelos botões de retirada
                findAndClickPickup(deviceNum);
            }
        } else if (text.includes("devolver")) {
            const btn = document.querySelector('button[formaction*="return"]');
            if (btn) {
                btn.click();
            } else {
                alert("Nenhum equipamento em uso para devolver.");
            }
        } else if (text.includes("chamado")) {
            const btn = document.querySelector('[data-bs-target="#modalReportDefeito"]');
            if (btn) btn.click();
        }
    }

    function findAndClickPickup(num) {
        // Procura botões que tenham o número no nome do dispositivo
        const buttons = document.querySelectorAll('button[id^="btn-pickup-"]');
        let found = false;
        buttons.forEach(btn => {
            if (btn.innerText.includes(num) || btn.getAttribute('data-device-name').includes(num)) {
                btn.click();
                found = true;
            }
        });
        if (!found) alert(`Equipamento ${num} não encontrado ou ocupado.`);
    }
} else {
    console.warn("Seu navegador não suporta reconhecimento de voz.");
}

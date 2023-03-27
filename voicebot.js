var recordButton = document.getElementById('record');
var botResponse = document.getElementById('transcript');
window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
var recognition = new SpeechRecognition();
const synth = window.speechSynthesis;

recognition.lang = "pt-BR";
recognition.continuous = true;
recognition.interimResults = true;

recordButton.addEventListener('click', function() {
    recognition.start();
});

recognition.onresult = function(event) {
    var interimTranscript = '';
    for (var i = event.resultIndex; i < event.results.length; i++) {
        var transcriptText = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
            sendToServer(transcriptText);
            recognition.stop();
        } else {
            interimTranscript += transcriptText;
        }
    }
};

function sendToServer(transcriptText) {
    fetch('http://localhost:5007/webhooks/rest/webhook', {
        method: "POST",
        body: JSON.stringify({"message": transcriptText}),
        headers: {"Content-type": "application/json; charset=UTF-8"}
    })
    .then(response => response.json())
    .then(data => {
        console.log("Bot disse: ");
        let botMessage = "";
        for (let i of data) {
            botMessage = i.text;
            console.log(botMessage);  
        }            
        botResponse.innerHTML = botMessage;
        var utter = new SpeechSynthesisUtterance(botMessage);
        var voices = speechSynthesis.getVoices();
        var selectedVoice = voices.find(function(voice) {
            return voice.lang === 'pt-BR' && voice.name === "Microsoft Maria - Portuguese (Brazil)";
        });
        if (selectedVoice) {
            utter.voice = selectedVoice;
            synth.speak(utter);
        } else {
            console.error('Selected voice not available.');
        }
    })
    .catch(error => {
        console.error(error);
        botResponse.innerHTML = "Desculpe, não foi possível obter resposta do servidor.";
    });
    }

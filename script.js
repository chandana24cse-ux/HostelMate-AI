
async function uploadHandbook() {

    const fileInput = document.getElementById("handbookFile");
    const status = document.getElementById("uploadStatus");

    const file = fileInput.files[0];

    if (!file) {
        status.innerText = "Please select a PDF file first.";
        return;
    }

    if (file.type !== "application/pdf") {
        status.innerText = "Please upload a PDF file.";
        return;
    }

    status.innerText = "Uploading handbook...";

    const formData = new FormData();

    formData.append("file", file);

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/upload-handbook",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (response.ok) {

            status.innerText =
                "✓ " + data.message +
                " Pages: " + data.pages;

        } else {

            status.innerText =
                "Upload failed.";

        }

    } catch (error) {

        console.error(error);

        status.innerText =
            "Could not connect to the backend.";

    }
}


function setQuestion(question) {

    document.getElementById("question").value = question;

}


async function askQuestion() {

    const questionInput =
        document.getElementById("question");

    const chatHistory =
        document.getElementById("chatHistory");

    const question =
        questionInput.value.trim();

    if (!question) {

        chatHistory.innerHTML +=
            "<p>⚠️ Please enter a question.</p>";

        return;
    }

    // Add user's question
    chatHistory.innerHTML +=
        "<div class='chat-message user-message'>" +
        "<strong>👤 You:</strong><br>" +
        question +
        "</div>";

    // Show thinking message
    const thinkingMessage =
        document.createElement("div");

    thinkingMessage.className =
        "chat-message assistant-message";

    thinkingMessage.innerHTML =
        "<strong>🤖 Assistant:</strong><br>" +
        "Thinking...";

    chatHistory.appendChild(
        thinkingMessage
    );

    // Clear question box
    questionInput.value = "";

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );

        const data = await response.json();

        // Display answer
        if (data.source) {

            thinkingMessage.innerHTML =
                "<strong>🤖 Assistant:</strong><br><br>" +
                data.answer +
                "<br><br>" +
                "<small>" +
                data.source +
                "</small>";

        } else {

            thinkingMessage.innerHTML =
                "<strong>🤖 Assistant:</strong><br><br>" +
                data.answer;

        }

    } catch (error) {

        console.error(error);

        thinkingMessage.innerHTML =
            "<strong>🤖 Assistant:</strong><br><br>" +
            "❌ Could not connect to the backend.";

    }

}
function startVoiceInput() {

    const questionInput =
        document.getElementById("question");

    const voiceStatus =
        document.getElementById("voiceStatus");

    // Check if browser supports speech recognition
    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

        voiceStatus.innerText =
            "❌ Voice input is not supported in this browser.";

        return;
    }

    const recognition =
        new SpeechRecognition();

    recognition.lang = "en-IN";

    recognition.interimResults = false;

    recognition.maxAlternatives = 1;

    voiceStatus.innerText =
        "🎤 Listening... Speak your question.";

    recognition.start();

    recognition.onresult = function(event) {

        const spokenText =
            event.results[0][0].transcript;

        questionInput.value =
            spokenText;

        voiceStatus.innerText =
            "✓ Voice input received.";

    };

    recognition.onerror = function(event) {

        console.error(event.error);

        voiceStatus.innerText =
            "❌ Could not understand your voice.";

    };

    recognition.onend = function() {

        if (
            voiceStatus.innerText ===
            "🎤 Listening... Speak your question."
        ) {

            voiceStatus.innerText =
                "Voice input stopped.";

        }

    };
}
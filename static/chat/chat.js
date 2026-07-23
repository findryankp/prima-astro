document.addEventListener("DOMContentLoaded", () => {
// --- Chatbot Logic ---
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const chatMessages = document.getElementById("chat-messages");

    function appendMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}-message`;
        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.textContent = text;
        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // User Message
        appendMessage(text, "user");
        chatInput.value = "";

        // Show typing
        const typingMsg = appendMessage("Thinking...", "ai");
        typingMsg.querySelector(".bubble").classList.add("typing-indicator");

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();

            // Remove typing and add real response
            chatMessages.removeChild(typingMsg);
            if (data.status === "success") {
                appendMessage(data.response, "ai");
            } else {
                appendMessage("Error: " + data.response, "ai");
            }
        } catch (error) {
            chatMessages.removeChild(typingMsg);
            appendMessage("Connection error. Please try again.", "ai");
        }
    }

    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                sendMessage();
            }
        });
    }
});

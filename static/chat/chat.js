document.addEventListener("DOMContentLoaded", () => {
    // --- Chatbot Logic ---
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const chatMessages = document.getElementById("chat-messages");

    function appendMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.textContent = sender === "ai" ? "🤖" : "👤";
        
        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.innerHTML = formatMarkdownText(text);
        
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubble);
        
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv;
    }

    function formatMarkdownText(text) {
        if (!text) return "";
        // Simple safe formatter for line breaks, bold, and bullet points
        let formatted = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/`([^`]+)`/g, "<code style='background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.85em;'>$1</code>")
            .replace(/\n/g, "<br>");
        return formatted;
    }

    async function sendMessage(customText) {
        const text = customText || chatInput.value.trim();
        if (!text) return;

        // User Message
        appendMessage(text, "user");
        if (!customText) chatInput.value = "";

        // Show typing indicator
        const typingMsg = document.createElement("div");
        typingMsg.className = "message ai-message";
        typingMsg.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="bubble typing-indicator">
                <span>Sedang berpikir</span>
                <span class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </span>
            </div>
        `;
        chatMessages.appendChild(typingMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();

            // Remove typing indicator
            if (typingMsg.parentNode) {
                chatMessages.removeChild(typingMsg);
            }

            if (data.status === "success") {
                appendMessage(data.response, "ai");
            } else {
                appendMessage("❌ Maaf, terjadi kendala: " + data.response, "ai");
            }
        } catch (error) {
            if (typingMsg.parentNode) {
                chatMessages.removeChild(typingMsg);
            }
            appendMessage("⚠️ Gagal terhubung ke server. Pastikan Celery worker & backend aktif.", "ai");
        }
    }

    // Expose quickPrompt to window for pill clicks
    window.quickPrompt = function(promptText) {
        chatInput.value = promptText;
        sendMessage(promptText);
        chatInput.value = "";
    };

    if (sendBtn) {
        sendBtn.addEventListener("click", () => sendMessage());
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                sendMessage();
            }
        });
    }
});

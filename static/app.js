document.addEventListener("DOMContentLoaded", () => {
    
    // --- Navigation Logic ---
    const navDashboard = document.getElementById("nav-dashboard");
    const navChat = document.getElementById("nav-chat");
    const viewDashboard = document.getElementById("view-dashboard");
    const viewChat = document.getElementById("view-chat");

    navDashboard.addEventListener("click", () => {
        navDashboard.classList.add("active");
        navChat.classList.remove("active");
        viewDashboard.classList.add("active");
        viewChat.classList.remove("active");
    });

    navChat.addEventListener("click", () => {
        navChat.classList.add("active");
        navDashboard.classList.remove("active");
        viewChat.classList.add("active");
        viewDashboard.classList.remove("active");
    });

    // --- Dashboard Data Fetching ---
    async function loadDashboardData() {
        try {
            // Fetch Stats
            const statsRes = await fetch("/api/dashboard/stats");
            const stats = await statsRes.json();
            document.getElementById("stat-total").textContent = stats.total_items.toLocaleString();
            document.getElementById("stat-low").textContent = stats.low_stock_items.toLocaleString();
            document.getElementById("stat-tx").textContent = stats.total_transactions.toLocaleString();

            // Fetch Low Stock
            const lowStockRes = await fetch("/api/stock/low");
            const lowStock = await lowStockRes.json();
            const lowStockTbody = document.getElementById("table-low-stock");
            lowStockTbody.innerHTML = "";
            lowStock.forEach(item => {
                const tr = document.createElement("tr");
                const statusClass = item.status.toLowerCase() === "danger" ? "status-danger" : "status-warning";
                tr.innerHTML = `
                    <td>${item.item_number}</td>
                    <td>${item.product_name}</td>
                    <td>${item.soh}</td>
                    <td>${item.safety_stock}</td>
                    <td class="${statusClass}">${item.status}</td>
                `;
                lowStockTbody.appendChild(tr);
            });

            // Fetch Recent Transactions
            const txRes = await fetch("/api/transactions/recent");
            const txData = await txRes.json();
            const txTbody = document.getElementById("table-recent-tx");
            txTbody.innerHTML = "";
            txData.forEach(tx => {
                const tr = document.createElement("tr");
                const dateOnly = tx.tanggal.split(" ")[0];
                tr.innerHTML = `
                    <td>${dateOnly}</td>
                    <td>${tx.product_name}</td>
                    <td>${tx.qty_out}</td>
                    <td>${tx.department}</td>
                    <td>${tx.pic}</td>
                `;
                txTbody.appendChild(tr);
            });
        } catch (error) {
            console.error("Error loading dashboard data:", error);
        }
    }

    loadDashboardData();

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

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

});

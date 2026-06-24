document.addEventListener("DOMContentLoaded", () => {
    
    // --- Navigation Logic ---
    const navDashboard = document.getElementById("nav-dashboard");
    const navForecast = document.getElementById("nav-forecast");
    const navChat = document.getElementById("nav-chat");
    const viewDashboard = document.getElementById("view-dashboard");
    const viewForecast = document.getElementById("view-forecast");
    const viewChat = document.getElementById("view-chat");

    function setActiveView(navEl, viewEl) {
        [navDashboard, navForecast, navChat].forEach(n => n.classList.remove("active"));
        [viewDashboard, viewForecast, viewChat].forEach(v => v.classList.remove("active"));
        navEl.classList.add("active");
        viewEl.classList.add("active");
    }

    navDashboard.addEventListener("click", () => setActiveView(navDashboard, viewDashboard));
    navForecast.addEventListener("click", () => setActiveView(navForecast, viewForecast));
    navChat.addEventListener("click", () => setActiveView(navChat, viewChat));

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

    // --- Forecasting Logic ---
    let forecastChart = null;

    async function loadForecastItems() {
        try {
            const res = await fetch("/api/items");
            const items = await res.json();
            const select = document.getElementById("item-select");
            select.innerHTML = '<option value="">-- Select an item to forecast --</option>';
            items.forEach(item => {
                const opt = document.createElement("option");
                opt.value = item.item_number;
                opt.textContent = `${item.item_number} - ${item.product_name}`;
                select.appendChild(opt);
            });
        } catch (e) {
            console.error("Error loading items:", e);
        }
    }

    loadForecastItems();

    document.getElementById("btn-forecast").addEventListener("click", async () => {
        const itemNumber = document.getElementById("item-select").value;
        if (!itemNumber) {
            alert("Please select an item first.");
            return;
        }

        const loading = document.getElementById("forecast-loading");
        loading.style.display = "block";

        try {
            const res = await fetch(`/api/forecast/${itemNumber}`);
            const data = await res.json();
            
            if (data.status === "error") {
                alert(data.message);
                loading.style.display = "none";
                return;
            }

            renderChart(data);
        } catch (e) {
            console.error(e);
            alert("Failed to load forecast data");
        } finally {
            loading.style.display = "none";
        }
    });

    function renderChart(data) {
        const ctx = document.getElementById("forecastChart").getContext("2d");
        
        if (forecastChart) {
            forecastChart.destroy();
        }

        // We want actuals and predicted to share the same date axis
        // For actuals, missing values will be skipped by chart.js if they are null
        
        forecastChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: 'Historical Actuals',
                        data: data.actual,
                        borderColor: '#10b981', // success color
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        pointRadius: 3,
                        spanGaps: true,
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Prophet Forecast (Next 30 Days)',
                        data: data.predicted,
                        borderColor: '#3b82f6', // primary color
                        borderDash: [5, 5],
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    title: {
                        display: true,
                        text: `Demand Forecast for ${data.product_name}`,
                        color: '#f8fafc',
                        font: { size: 16, family: 'Inter' }
                    },
                    legend: {
                        labels: { color: '#f8fafc', font: { family: 'Inter' } }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8', maxTicksLimit: 15 },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        beginAtZero: true
                    }
                }
            }
        });
    }

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

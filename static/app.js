document.addEventListener("DOMContentLoaded", () => {
    
    // --- Navigation Logic ---
    const navDashboard = document.getElementById("nav-dashboard");
    const navInsight = document.getElementById("nav-insight");
    const navForecast = document.getElementById("nav-forecast");
    const navChat = document.getElementById("nav-chat");
    const viewDashboard = document.getElementById("view-dashboard");
    const viewInsight = document.getElementById("view-insight");
    const viewForecast = document.getElementById("view-forecast");
    const viewChat = document.getElementById("view-chat");

    function setActiveView(navEl, viewEl) {
        [navDashboard, navInsight, navForecast, navChat].forEach(n => n.classList.remove("active"));
        [viewDashboard, viewInsight, viewForecast, viewChat].forEach(v => v.classList.remove("active"));
        navEl.classList.add("active");
        viewEl.classList.add("active");
    }

    navDashboard.addEventListener("click", () => setActiveView(navDashboard, viewDashboard));
    navInsight.addEventListener("click", () => {
        setActiveView(navInsight, viewInsight);
        loadInsights();
    });
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

    // --- Insight Logic ---
    let insightsLoaded = false;

    function fmtNum(n) {
        return (n === null || n === undefined) ? "-" : Number(n).toLocaleString(undefined, { maximumFractionDigits: 1 });
    }

    async function loadInsights() {
        if (insightsLoaded) return; // cached for the session; data only changes when the DB is re-synced
        try {
            const res = await fetch("/api/insights");
            const data = await res.json();

            if (data.status !== "success") {
                document.getElementById("insight-total-demand").textContent = "N/A";
                document.getElementById("insight-restock-count").textContent = "N/A";
                document.getElementById("insight-as-of").textContent = data.message || "No data";
                return;
            }

            insightsLoaded = true;

            document.getElementById("insight-total-demand").textContent = fmtNum(data.total_forecasted_demand_30d);
            document.getElementById("insight-restock-count").textContent = data.restock_alerts.length;
            document.getElementById("insight-as-of").textContent = data.as_of_date;
            document.querySelectorAll(".window-days").forEach(el => el.textContent = data.window_days);

            const restockBody = document.getElementById("table-restock-alerts");
            restockBody.innerHTML = "";
            data.restock_alerts.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${item.product_name}</td>
                    <td>${fmtNum(item.soh)} ${item.unit || ""}</td>
                    <td>${fmtNum(item.avg_daily_usage)}</td>
                    <td class="status-danger">${item.days_to_stockout !== null ? fmtNum(item.days_to_stockout) + " days" : "-"}</td>
                `;
                restockBody.appendChild(tr);
            });
            if (data.restock_alerts.length === 0) {
                restockBody.innerHTML = `<tr><td colspan="4">No urgent restock needs right now.</td></tr>`;
            }

            const upBody = document.getElementById("table-trending-up");
            upBody.innerHTML = "";
            data.trending_up.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${item.product_name}</td>
                    <td>${fmtNum(item.recent_total)}</td>
                    <td>${fmtNum(item.previous_total)}</td>
                    <td class="trend-up">+${fmtNum(item.trend_pct)}%</td>
                `;
                upBody.appendChild(tr);
            });

            const downBody = document.getElementById("table-trending-down");
            downBody.innerHTML = "";
            data.trending_down.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${item.product_name}</td>
                    <td>${fmtNum(item.recent_total)}</td>
                    <td>${fmtNum(item.previous_total)}</td>
                    <td class="trend-down">${fmtNum(item.trend_pct)}%</td>
                `;
                downBody.appendChild(tr);
            });
        } catch (error) {
            console.error("Error loading insights:", error);
        }
    }

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
                
                let label = `${item.item_number} - ${item.product_name}`;
                if (item.tx_count > 5) {
                    label += " ⭐ (>5 tx)";
                }
                
                opt.textContent = label;
                select.appendChild(opt);
            });
            
            // Initialize Select2 on the dropdown
            $(select).select2({
                placeholder: "-- Select an item to forecast --",
                allowClear: true,
                width: '100%'
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

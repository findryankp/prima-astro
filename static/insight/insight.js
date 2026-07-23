document.addEventListener("DOMContentLoaded", () => {
// --- Insight Logic ---
    if (document.getElementById("view-insight")) {
        loadInsights();
    }

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
});

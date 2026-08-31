document.addEventListener("DOMContentLoaded", () => {
    // --- Insight Logic ---
    let insightsLoaded = false;

    function fmtNum(n) {
        return (n === null || n === undefined) ? "-" : Number(n).toLocaleString(undefined, { maximumFractionDigits: 1 });
    }

    async function loadInsights() {
        if (insightsLoaded) return;
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
            if (data.restock_alerts.length === 0) {
                restockBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: #10b981; padding: 20px;">✅ Tidak ada item yang mendesak untuk restock saat ini.</td></tr>`;
            } else {
                data.restock_alerts.forEach(item => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>${item.product_name}</strong></td>
                        <td><span style="font-weight: 600; color: #dc2626;">${fmtNum(item.soh)}</span> <span style="font-size: 0.8rem; color: #64748b;">${item.unit || ""}</span></td>
                        <td>${fmtNum(item.avg_daily_usage)}</td>
                        <td><span class="badge badge-danger">${item.days_to_stockout !== null ? fmtNum(item.days_to_stockout) + " hari" : "-"}</span></td>
                    `;
                    restockBody.appendChild(tr);
                });
            }

            const upBody = document.getElementById("table-trending-up");
            upBody.innerHTML = "";
            if (data.trending_up.length === 0) {
                upBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: #94a3b8; padding: 20px;">Tidak ada tren lonjakan konsumsi.</td></tr>`;
            } else {
                data.trending_up.forEach(item => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>${item.product_name}</strong></td>
                        <td>${fmtNum(item.recent_total)}</td>
                        <td>${fmtNum(item.previous_total)}</td>
                        <td><span class="trend-up">▲ +${fmtNum(item.trend_pct)}%</span></td>
                    `;
                    upBody.appendChild(tr);
                });
            }

            const downBody = document.getElementById("table-trending-down");
            downBody.innerHTML = "";
            if (data.trending_down.length === 0) {
                downBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: #94a3b8; padding: 20px;">Tidak ada tren penurunan signifikan.</td></tr>`;
            } else {
                data.trending_down.forEach(item => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>${item.product_name}</strong></td>
                        <td>${fmtNum(item.recent_total)}</td>
                        <td>${fmtNum(item.previous_total)}</td>
                        <td><span class="trend-down">▼ ${fmtNum(item.trend_pct)}%</span></td>
                    `;
                    downBody.appendChild(tr);
                });
            }
        } catch (error) {
            console.error("Error loading insights:", error);
        }
    }

    if (document.getElementById("view-insight")) {
        loadInsights();
    }
});

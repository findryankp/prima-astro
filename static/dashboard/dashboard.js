document.addEventListener("DOMContentLoaded", () => {
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

    if (document.getElementById("view-dashboard")) {
        loadDashboardData();
    }
});

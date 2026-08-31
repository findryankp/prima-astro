document.addEventListener("DOMContentLoaded", () => {
    let usageChartInstance = null;

    // --- Dashboard Data Fetching ---
    async function loadDashboardData() {
        try {
            // Fetch Stats
            const statsRes = await fetch("/api/dashboard/stats");
            const stats = await statsRes.json();

            document.getElementById("stat-total").textContent = stats.total_items.toLocaleString();
            document.getElementById("stat-low").textContent = stats.low_stock_items.toLocaleString();
            document.getElementById("stat-tx").textContent = stats.total_transactions.toLocaleString();

            // Fetch Usage Bar Chart
            loadUsageChart();

            // Fetch Low Stock
            const lowStockRes = await fetch("/api/stock/low");
            const lowStock = await lowStockRes.json();
            const lowStockTbody = document.getElementById("table-low-stock");
            lowStockTbody.innerHTML = "";
            
            if (lowStock.length === 0) {
                lowStockTbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #10b981; padding: 20px;">✅ Semua stok aman di atas batas safety stock.</td></tr>`;
            } else {
                lowStock.forEach(item => {
                    const tr = document.createElement("tr");
                    const statusClass = item.status.toLowerCase() === "danger" ? "badge-danger" : "badge-warning";
                    tr.innerHTML = `
                        <td><strong>${item.item_number}</strong></td>
                        <td>${item.product_name}</td>
                        <td><span style="font-weight: 700; color: #dc2626;">${item.soh}</span></td>
                        <td>${item.safety_stock}</td>
                        <td><span class="badge ${statusClass}">${item.status}</span></td>
                    `;
                    lowStockTbody.appendChild(tr);
                });
            }

            // Fetch Recent Transactions
            const txRes = await fetch("/api/transactions/recent");
            const txData = await txRes.json();
            const txTbody = document.getElementById("table-recent-tx");
            txTbody.innerHTML = "";
            
            if (txData.length === 0) {
                txTbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #94a3b8; padding: 20px;">Belum ada riwayat transaksi keluar.</td></tr>`;
            } else {
                txData.forEach(tx => {
                    const tr = document.createElement("tr");
                    const dateOnly = tx.tanggal.split(" ")[0];
                    tr.innerHTML = `
                        <td><span style="color: #64748b; font-size: 0.85rem;">${dateOnly}</span></td>
                        <td><strong>${tx.product_name}</strong></td>
                        <td><span class="badge badge-warning" style="font-weight: 700;">-${tx.qty_out}</span></td>
                        <td><span style="background: #f1f5f9; padding: 3px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 500;">${tx.department || "-"}</span></td>
                        <td><span style="color: #475569;">${tx.pic || "-"}</span></td>
                    `;
                    txTbody.appendChild(tr);
                });
            }
        } catch (error) {
            console.error("Error loading dashboard data:", error);
        }
    }

    async function loadUsageChart() {
        try {
            const res = await fetch("/api/dashboard/usage-chart");
            const data = await res.json();
            
            const totalEl = document.getElementById("chart-total-usage");
            if (totalEl) {
                totalEl.textContent = (data.total_all || 0).toLocaleString();
            }

            const canvas = document.getElementById("usageBarChart");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");

            if (usageChartInstance) {
                usageChartInstance.destroy();
            }

            usageChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.periods || [],
                    datasets: [{
                        data: data.totals || [],
                        backgroundColor: '#4f46e5',
                        hoverBackgroundColor: '#6366f1',
                        borderRadius: 4,
                        borderSkipped: false,
                        barPercentage: 0.65,
                        categoryPercentage: 0.85
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: { display: false },
                        tooltip: {
                            enabled: true,
                            backgroundColor: '#0f172a',
                            titleColor: '#ffffff',
                            bodyColor: '#e2e8f0',
                            titleFont: { family: 'Poppins', size: 11, weight: '600' },
                            bodyFont: { family: 'Poppins', size: 11 },
                            padding: 8,
                            cornerRadius: 6,
                            displayColors: false,
                            callbacks: {
                                title: function(context) {
                                    return "Periode: " + context[0].label;
                                },
                                label: function(context) {
                                    return "Pengeluaran: " + Number(context.raw).toLocaleString() + " units";
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            display: false,
                            grid: { display: false, drawBorder: false }
                        },
                        y: {
                            display: false,
                            grid: { display: false, drawBorder: false },
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (e) {
            console.error("Error loading usage chart:", e);
        }
    }

    if (document.getElementById("view-dashboard")) {
        loadDashboardData();
    }
});

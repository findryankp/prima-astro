document.addEventListener("DOMContentLoaded", () => {
    // --- Forecasting Logic ---
    let forecastChart = null;

    async function loadForecastItems() {
        try {
            const res = await fetch("/api/items");
            const items = await res.json();
            const select = document.getElementById("item-select");
            
            // Filter hanya item yang memenuhi syarat prediksi Prophet (minimal 5 transaksi)
            const forecastableItems = items.filter(item => (item.tx_count || 0) >= 5);

            select.innerHTML = `<option value="">-- Pilih item sparepart (${forecastableItems.length} item siap diprediksi) --</option>`;
            
            forecastableItems.forEach(item => {
                const opt = document.createElement("option");
                opt.value = item.item_number;
                opt.textContent = `${item.item_number} - ${item.product_name} (${item.tx_count} transaksi)`;
                select.appendChild(opt);
            });

            // Initialize Select2 on the dropdown
            $(select).select2({
                placeholder: "-- Pilih item sparepart siap diprediksi --",
                allowClear: true,
                width: '100%'
            });
        } catch (e) {
            console.error("Error loading items:", e);
        }
    }

    if (document.getElementById("view-forecast")) {
        loadForecastItems();
    }

    if (document.getElementById("btn-forecast")) {
        document.getElementById("btn-forecast").addEventListener("click", async () => {
            const itemNumber = document.getElementById("item-select").value;
            if (!itemNumber) {
                alert("Silakan pilih item sparepart terlebih dahulu.");
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
                alert("Gagal memuat data prediksi.");
            } finally {
                loading.style.display = "none";
            }
        });
    }

    function renderChart(data) {
        const ctx = document.getElementById("forecastChart").getContext("2d");

        if (forecastChart) {
            forecastChart.destroy();
        }

        forecastChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: 'Data Historis Pemakaian',
                        data: data.actual,
                        borderColor: '#059669', // Emerald
                        backgroundColor: 'rgba(5, 150, 105, 0.08)',
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointBackgroundColor: '#059669',
                        spanGaps: true,
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Prediksi Prophet AI (30 Hari ke Depan)',
                        data: data.predicted,
                        borderColor: '#4f46e5', // Primary Indigo
                        backgroundColor: 'rgba(79, 70, 229, 0.06)',
                        borderDash: [6, 6],
                        borderWidth: 2.5,
                        pointRadius: 2,
                        pointBackgroundColor: '#4f46e5',
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
                        text: `Prediksi Kebutuhan: ${data.product_name}`,
                        color: '#0f172a',
                        font: { size: 13, family: 'Poppins', weight: '600' },
                        padding: { bottom: 14 }
                    },
                    legend: {
                        labels: { 
                            color: '#475569', 
                            font: { family: 'Poppins', size: 11, weight: '500' },
                            usePointStyle: true,
                            padding: 14
                        }
                    },

                    tooltip: {
                        backgroundColor: '#0f172a',
                        titleColor: '#ffffff',
                        bodyColor: '#e2e8f0',
                        titleFont: { family: 'Poppins', weight: '600' },
                        bodyFont: { family: 'Poppins' },
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        ticks: { 
                            color: '#64748b', 
                            maxTicksLimit: 15,
                            font: { family: 'Poppins', size: 11 }
                        },
                        grid: { color: '#f1f5f9' }
                    },
                    y: {
                        ticks: { 
                            color: '#64748b',
                            font: { family: 'Poppins', size: 11 }
                        },
                        grid: { color: '#f1f5f9' },
                        beginAtZero: true
                    }
                }
            }
        });
    }
});

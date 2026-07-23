document.addEventListener("DOMContentLoaded", () => {
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

    if (document.getElementById("view-forecast")) {
        loadForecastItems();
    }

    if (document.getElementById("btn-forecast")) {
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
    }

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
});

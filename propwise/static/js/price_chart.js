// static/js/price_chart.js

document.addEventListener('DOMContentLoaded', function() {
    
    const ctx = document.getElementById('priceTrendChart');
    if (!ctx) {
        return; // No chart on this page
    }

    const chartLabels = JSON.parse(ctx.dataset.labels);
    const chartData = JSON.parse(ctx.dataset.data);

    // Don't draw the chart if there's no data
    if (chartData.length === 0) {
        return;
    }

    // Create the new chart
    new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [{
                // --- THIS IS THE LABEL CHANGE ---
                label: 'Average Price Per Sq. Ft. (PKR)',
                data: chartData,
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 2,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        // --- THIS IS THE TICKS CALLBACK CHANGE ---
                        // It now formats as "PKR 5,000 / sqft"
                        callback: function(value, index, values) {
                            return 'PKR ' + value.toLocaleString('en-US', {maximumFractionDigits: 0}) + ' / sqft';
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        // --- THIS IS THE TOOLTIP CALLBACK CHANGE ---
                        label: function(context) {
                            let label = 'Avg. Price / Sq. Ft.: ';
                            if (context.parsed.y !== null) {
                                // Format the number with commas and currency
                                label += new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'PKR',
                                    minimumFractionDigits: 0
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
});
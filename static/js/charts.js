const colors = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
    '#FF9F40', '#66BB6A', '#D4E157', '#BA68C8', '#F06292',
    '#8D6E63', '#789262', '#9575CD', '#4DB6AC', '#AED581'
];

// Pie Chart
const ctxPie = document.getElementById('pieChart').getContext('2d');
new Chart(ctxPie, {
    type: 'pie',
    data: {
        labels: categories,
        datasets: [{
            label: 'Expenses by Category',
            data: amounts,
            backgroundColor: colors
        }]
    },
    options: {
        responsive: false
    }
});

// Bar Chart
const ctxBar = document.getElementById('barChart').getContext('2d');
new Chart(ctxBar, {
    type: 'bar',
    data: {
        labels: categories,
        datasets: [{
            label: 'Expenses by Category',
            data: amounts,
            backgroundColor: colors
        }]
    },
    options: {
        responsive: false,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

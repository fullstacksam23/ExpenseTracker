// Pie Chart - Category Spending
const ctx1 = document.getElementById('categoryChart').getContext('2d');
const categoryChart = new Chart(ctx1, {
    type: 'pie',
    data: {
        labels: ['Food', 'Travel', 'Books', 'Entertainment'],
        datasets: [{
            label: 'Spending',
            data: [200, 150, 100, 80],
            backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56']
        }]
    }
});

// Bar Chart - Monthly Spending
const ctx2 = document.getElementById('monthlyChart').getContext('2d');
const monthlyChart = new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr'],
        datasets: [{
            label: 'Expenses',
            data: [400, 300, 500, 200],
            backgroundColor: '#36a2eb'
        }]
    }
});
// Example data - you can replace this with dynamic data later!
const recentExpensesLabels = ['Office Supplies', 'Food', 'Travel', 'Subscriptions', 'Books'];
const recentExpensesData = [150, 75, 450, 30, 60];

const ctxRecent = document.getElementById('recentExpensesChart').getContext('2d');
const recentExpensesChart = new Chart(ctxRecent, {
    type: 'bar',
    data: {
        labels: recentExpensesLabels,
        datasets: [{
            label: 'Expense Amount (€)',
            data: recentExpensesData,
            backgroundColor: 'rgba(54, 162, 235, 0.7)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            borderRadius: 5
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

$(document).ready(function() {
    drawGraphs();
});

const shortDateString = date => `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}`;

const drawGraphs = () => {
    const MS_PER_WEEK = 1000 * 60 * 60 * 24 * 7;
    $('.graph').each(function(_, el) {
        const ctx = $(el);
        const startDate = new Date($(el).data('startDate'));    
        const endDate = new Date($(el).data('endDate'));
        const weeksBetween = (endDate - startDate) / MS_PER_WEEK;
        const dates = [];
        let d;
        for (let i = 0; i < weeksBetween; i++) {
            d = new Date();
            d.setDate(startDate.getDate() + (7 * i));
            dates.push(shortDateString(d));
        }
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: $(el).data('label'),
                    data: JSON.parse($('#weekly-data').text()),
                    backgroundColor: '#222'
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'category',
                        labels: dates
                    }],
                    yAxes: [{
                        type: 'linear',
                        beginAtZero: true,
                        precision: 0
                    }]
                }
            }
        })
    });
}

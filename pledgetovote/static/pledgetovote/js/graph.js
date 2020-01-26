$(document).ready(function() {
    drawGraphs();
});

const drawGraphs = () => {
    $('.graph').each(function(_, el) {
        const ctx = $(el);

        const startWeek = parseInt($(el).data('startWeekNum'));
        const numWeeks = parseInt($(el).data('numWeeks'));
        const weekLabels = [];
        for (let i = startWeek; i <= startWeek + numWeeks; i++) {
            weekLabels.push(`Week ${i}`);
        }
        weekLabels[weekLabels.length - 1] = 'Post Strike Circle';

        const data = JSON.parse($(this).parent().find('#weekly-data').text());

        // Removes all trailing weeks of data where no data was entered
        let i = data.length - 2;
        for (; i >= 0; i--) {
            if (data[i] != data[i + 1]) {
                break;
            }
        }
        const parsedData = data.slice(0, i + 2);

        new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: $(el).data('label'),
                    fill: false,
                    data: parsedData,
                    borderColor: '#222'
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'category',
                        labels: weekLabels
                    }],
                    yAxes: [{
                        type: 'linear',
                        ticks: {
                            beginAtZero: true,
                            precision: 0
                        }
                    }]
                }
            }
        })
    });
}

$(document).ready(function() {
    drawGraphs();
});

const drawGraphs = () => {
    $('.graph').each(function(_, el) {
        const ctx = $(el);

        const goal = parseInt($(el).data('goal'));
        const goalType = $(el).data('goalType');
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
                    fill: false,
                    data: parsedData,
                    borderColor: '#222',
                    lineTension: 0  // Draw straight lines between points
                }]
            },
            options: {
                maintainAspectRatio: false,
                legend: { display: false },
                tooltips: {
                    callbacks: {
                        title: tooltipItem => `${tooltipItem[0].value} ${goalType}`,
                        label: _ => false
                    }
                },
                scales: {
                    xAxes: [{
                        type: 'category',
                        labels: weekLabels
                    }],
                    yAxes: [{
                        gridLines: {
                            borderDash: [5, 15],
                            lineWidth: 2
                        },
                        ticks: {
                            min: 0,
                            max: Math.trunc(goal * 1.15),
                            callback: value => `Goal: ${value} ${goalType}`
                        },
                        afterBuildTicks: axis => {
                            axis.ticks = [];
                            axis.ticks.push(goal);
                        }
                    }]
                }
            }
        })
    });
}

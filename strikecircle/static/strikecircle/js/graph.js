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
        const maxVal = parsedData[parsedData.length - 1];

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
                    displayColors: false,
                    callbacks: {
                        title: _ => '',
                        label: tooltipItem => `${tooltipItem.value} ${goalType}`,
                        labelTextColor: _ => '#FFDE16'
                    }
                },
                scales: {
                    xAxes: [{
                        type: 'category',
                        labels: weekLabels,
                        gridLines: {
                            zeroLineWidth: 2,
                            zeroLineColor: '#AAA'
                        }
                    }],
                    yAxes: [{
                        gridLines: {
                            borderDash: [5, 15],
                            lineWidth: 2,
                            zeroLineWidth: 2,
                            zeroLineColor: '#AAA'
                        },
                        ticks: {
                            min: 0,
                            max: Math.max(Math.ceil(goal * 1.15), maxVal * 1.15),
                            callback: value => (value == goal ? 'Goal: ' : '') + `${value} ${goalType}`
                        },
                        afterBuildTicks: axis => {
                            axis.ticks = [0, goal, maxVal];
                        }
                    }]
                }
            }
        })
    });
}

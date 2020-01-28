$(document).ready(function() {
    const weekMap = JSON.parse($('#week-map').text());    

    function dateToWeek(date) {
        for (let dateTuple of weekMap) {
            if (dateTuple[0] == date) {
                return dateTuple[1];
            }
        }
    }

    $('p[data-field="date_collected"]').each(function(_, el) {
        $(el).text(dateToWeek($(el).data('value')));
    });

    $('p[data-field="one_on_one"]').each(function(_, el) {
        $(el).text($(el).data('value') != 'None' ? '✓' : 'x');
    });
});

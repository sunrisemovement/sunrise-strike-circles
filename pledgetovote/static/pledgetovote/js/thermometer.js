const THERM_HEIGHT = 400;

$(document).ready(function() {
    setThermHeight();
});

const setThermHeight = () => {
    const therm = $('.thermometer');
    
    $(therm).each(function(_, element) {
        const goal = parseInt($(element).data('goal'), 10);
        const count = parseInt($(element).data('count'), 10);
        const percentage = count / goal;
        const newHeight = THERM_HEIGHT - (percentage * THERM_HEIGHT);
        $(element).find('.thermometer-cover').css('height', `${newHeight}px`);
        $(element).parent().find('.thermometer-labels .goal').css('height', `${newHeight - 10}px`);    
    });
}

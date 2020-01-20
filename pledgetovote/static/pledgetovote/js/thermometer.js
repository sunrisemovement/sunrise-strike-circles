$(document).ready(function() {
    setThermHeight();
});

const setThermHeight = () => {
    // Capture thermometer height in format '<num>px' (e.g., '400px'), and convert it to an integer (e.g., 400)
    const thermHeightStr = $('.thermometer-inner-container').css('height');
    const thermHeight = parseInt(thermHeightStr.replace(/[A-Za-z]/, ''));
    const therm = $('.thermometer');
    
    $(therm).each(function(_, element) {
        const goal = parseInt($(element).data('goal'), 10);
        const count = parseInt($(element).data('count'), 10);
        const percentage = count / goal;
        const newHeight = thermHeight - (percentage * thermHeight);
        $(element).find('.thermometer-cover').css('height', `${newHeight}px`);
        $(element).parent().find('.thermometer-labels .goal').css('height', `${newHeight - 10}px`);    
    });
}

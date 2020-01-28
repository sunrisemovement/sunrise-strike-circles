$(document).ready(function() {
    setThermHeight();
});

const setThermHeight = () => {
    // Capture progress bar width in format '<num>px' (e.g., '400px'), and convert it to an integer (e.g., 400)
    const barWidthStr = $('.progress-bar-container').css('width');
    const barWidth = parseInt(barWidthStr.replace(/[A-Za-z]/, ''));
    const bar = $('.progress-bar');
    
    $(bar).each(function(_, element) {
        const goal = parseInt($(element).data('goal'), 10);
        const count = parseInt($(element).data('count'), 10);
        const percentage = count / goal;
        const newWidth = barWidth - (percentage * barWidth);
        $(element).find('.progress-bar-cover').css('width', `${newWidth}px`);
    });
}

$(document).ready(function() {
    // When a week option is clicked, set the pledge form's date_collected input to the date corresponding
    // to the week that was clicked
    $('.week').click(function() {
        const date = $(this).data('date');
        $('#pledge-form input[name="date_collected"]').val(date);
        $(this).parent().css('display', 'none');
        $('#pledge-form').css('display', 'block');
    });

    $('#back-to-week').click(function() {
        $(this).parent().css('display', 'none');
        $('.weeks-container').css('display', 'block');
    })

    const listDisplayRowEl = ' .listdisplay.columns';
    // Click on pledges that haven't had one-on-ones to select/deselect them for having one-on-ones added
    $('#no-one-on-one' + listDisplayRowEl).click(function() {
        if (!$(this).data('selected')) {
            const copy = $(this).clone();
            $(this).addClass('has-text-danger');
            $(this).data('selected', true);
            $('#selected-one-on-ones').append(copy);    
        } else {
            const inSelectedList = $('#selected-one-on-ones').find(`[data-index='${elIndex(this)}']`);
            $(inSelectedList).remove();
            $(this).removeClass('has-text-danger');
            $(this).data('selected', false);
        }

        updateSubmitButtonStatus();
    });

    // Click on pledges that were selected to have one-on-ones added to un-select them
    $('#selected-one-on-ones').on('click', listDisplayRowEl, function() {
        // Find the original list item in the list of pledges with no one-on-one
        const inOriginalList = $('#no-one-on-one').find(`[data-index='${elIndex(this)}']`);
        // Delete the style="color:red" attribute that was added when this pledge was copied to the selected table
        $(inOriginalList).removeClass('has-text-danger');
        $(this).remove();
        updateSubmitButtonStatus();
    });

    // Collect ids of pledges to add one-on-ones to
    $('#submit-one-on-ones').click(function() {
        if ($(this).disabled) {
            return false;
        }

        const ids = [];
        $('#selected-one-on-ones' + listDisplayRowEl).each(function() {
            ids.push($(this).data('id'));
        });
        $('#one-on-one-form input[name="add_one_on_ones"]').val(ids);
        return true;
    });

    const elIndex = el => $(el).data('index');

    const updateSubmitButtonStatus = () => {
        if ($('#selected-one-on-ones' + listDisplayRowEl).length == 0) {
            $('#submit-one-on-ones').attr('disabled', true);
        } else {
            $('#submit-one-on-ones').removeAttr('disabled');
        }
    };
});

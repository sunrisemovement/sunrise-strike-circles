$(document).ready(function() {
    const dateToWeek = date => {
        for (let dateTuple of weekMap) {
            if (dateTuple[0] == date) {
                return dateTuple[1];
            }
        }
    };

    const addModeToggle = () => {
        let rowsToToggle = $('.input-table-added-row').not('.hidden');
        // If there aren't any empty form rows, add one and refresh the rowsToToggle selector
        if (rowsToToggle.length == 0) {
            addForm();
            rowsToToggle = $(rowsToToggle.selector);
        }

        // Change the visibility of the form rows
        const newDisplayStyle = $(rowsToToggle[0]).css('display') == 'flex' ? 'none' : 'flex';
        $(rowsToToggle).each(function() {
            $(this).css('display', newDisplayStyle);
        });
        $('.mode-add').toggle();
        $('.mode-default').toggle();
    };

    // Add another form to the formset
    const addForm = () => {
        const numForms = parseInt($('#id_form-TOTAL_FORMS').val());
        $('#id_form-TOTAL_FORMS').val(numForms + 1);
        let clone = $('#empty-clone').clone().removeAttr('id').removeClass('hidden');
        $(clone).find('input, select').each(function() {
            const el = $(this);
            // Iterate over every attribute of the current element, and replace '__prefix__' in any attribute value
            // with the current number of input form rows (0-indexed)
            $.each(this.attributes, function() {
                if (this.specified && this.value.includes('__prefix__')) {
                    const newValue = this.value.replace('__prefix__', numForms);
                    $(el).attr(this.name, newValue);
                }
            })
        });
        $(clone).css('display', 'flex');
        $('#add-pledges-form').append(clone);
    };

    // Submit the formset
    const submitFormset = () => {
        $('#add-pledges-form').submit();
    };

    const weekMap = JSON.parse($('#week-map').text());  // Array of arrays, pairing dates with week names
    const checkmark = $('#hidden-check').clone().removeAttr('id', 'aria-hidden').removeClass('hidden');

    // Button triggers for adding new pledges
    $('#add-pledges-button').click(addModeToggle);
    $('#cancel-adding-button').click(addModeToggle);
    $('#submit-pledges-button').click(submitFormset);
    $('#add-another-button').click(addForm);

    // Replace the date_collected field of each pledge with the week corresponding to date_collected
    $('p[data-field="date_collected"]').each(function(_, el) {
        $(el).text(dateToWeek($(el).data('value')));
    });

    // Replace one-on-one dates with checkmarks
    $('p[data-field="one_on_one"]').each(function(_, el) {
        const innerHtml = $(el).data('value') != 'None' ? $(checkmark).clone() : '';
        $(el).html(innerHtml);
    });

    // If one-on-one display checkbox is checked, set real (hidden) one-on-one input to the current date
    $('#add-pledges-form').on('change', 'input:checkbox', function() {
        if ($(this).is(':checked')) {
            const date = new Date();
            const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
            $($(this).prev()[0]).val(dateString);
        } else {
            $($(this).prev()[0]).val(null);
        }
    });
});

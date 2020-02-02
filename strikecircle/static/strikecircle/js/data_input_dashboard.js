$(document).ready(function() {
    const setCookie = (cname, cvalue, exdays) => {
        var d = new Date();
        d.setTime(d.getTime() + (exdays*24*60*60*1000));
        var expires = "expires="+ d.toUTCString();
        document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    }

    const getCookie = cname => {
        var name = cname + "=";
        var decodedCookie = decodeURIComponent(document.cookie);
        var ca = decodedCookie.split(';');
        for(var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ')
              c = c.substring(1);
            if (c.indexOf(name) == 0)
              return c.substring(name.length, c.length);
        }
        return "";
    }

    const dateToWeek = date => {
        for (let dateTuple of weekMap) {
            if (dateTuple[0] == date) {
                return dateTuple[1];
            }
        }
    };

    const addModeToggle = turnOn => {
        return () => {
            let rowsToToggle = $('.input-table-added-row').not('.hidden');
            // If add mode was toggled on and there aren't any empty form rows, add one and refresh
            // the rowsToToggle selector
            if (turnOn && rowsToToggle.length == 0) {
                addForm();
                rowsToToggle = $(rowsToToggle.selector);
            }

            // Change the visibility of the form rows
            const newDisplayStyle = turnOn ? 'flex' : 'none';
            $(rowsToToggle).each(function() {
                $(this).css('display', newDisplayStyle);
            });
            $('.mode-add').toggle();
            $('.mode-default').toggle();
        }

    };

    // Add another form to the formset
    const addForm = () => {
        const numForms = parseInt($('#id_form-TOTAL_FORMS').val());
        $('#id_form-TOTAL_FORMS').val(numForms + 1);
        let clone = $('#empty-clone').clone().removeAttr('id').removeClass('hidden');
        $(clone).find('input, select').addBack('.input-table-added-row').each(function() {
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

        // Set the week to the most recently selected value (& save to cookie)
        const $weekSelect = $(clone).find('[data-field="date_collected"] select');
        const weekCname = 'sunrise-strike-circle-week';
        if (getCookie(weekCname)) {
            $weekSelect.val(getCookie(weekCname));
        }
        $weekSelect.change(ev => {
            const weekVal = $(ev.currentTarget).val();
            setCookie(weekCname, weekVal, 7); // save cookie for 7 days
        });
    };

    const weekMap = JSON.parse($('#week-map').text());  // Array of arrays, pairing dates with week names
    const checkmark = $('#hidden-check').clone().removeAttr('id', 'aria-hidden').removeClass('hidden');

    // Button triggers for adding new pledges
    $('#add-pledges-button').click(addModeToggle(true));
    $('#cancel-adding-button').click(addModeToggle(false));
    $('#submit-pledges-button').click(() => {
        $('#add-pledges-form').submit();
    });
    $('#add-another-button').click(addForm);
    // Make it possible to delete input rows
    $('#add-pledges-form').on('click', '.del-row', function() {
        // By adding the "hidden" class to the row, we make sure that it doesn't get re-displayed if the user deletes
        // the row, hits the cancel button, and then re-enters add mode. addModeToggle() ignores rows with the class "hidden".
        $(this).parent().addClass('hidden');

        // Django formsets require a hidden field to be added when a form in the formset is to be deleted/not processed.
        // See https://docs.djangoproject.com/en/3.0/topics/forms/formsets/#understanding-the-managementform
        const delTemplate = $('#delete-template');
        const deleteInputName = $(delTemplate).attr('name').replace('__prefix__', $(this).parent().data('formNum'));
        const deleteInput = $(delTemplate).attr('name', deleteInputName);
        $('#add-pledges-form').append(deleteInput);
    });


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

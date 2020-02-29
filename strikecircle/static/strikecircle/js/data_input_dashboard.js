$(document).ready(function() {
    /********************/
    /** Misc functions **/

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

    /** End misc functions **/
    /************************/


    /**********************/
    /** Common selectors/other strings **/

    const _inputTableRow = '.input-table-row';
    const _hiddenClass = 'hidden';
    const _addPledgesForm = '#add-pledges-form';
    const _editPledgesForm = '#edit-pledges-form';
    const _formAttrPlaceholder = '__prefix__';

    /** End common selectors/strings **/
    /**************************/


    /********************************************/
    /** Related to displaying existing pledges **/

    const weekMap = JSON.parse($('#week-map').text());  // Array of arrays, pairing dates with week names
    const checkmark = $('#hidden-check').clone().removeAttr('id', 'aria-hidden').removeClass('hidden');

    const updateDateCollected = el => {
        $(el).text(dateToWeek($(el).data('value')));
    };

    const oneOnOneToCheckmark = el => {
        const innerHtml = $(el).data('value') != 'None' ? $(checkmark).clone() : '';
        $(el).html(innerHtml);
    };

    // Replace the date_collected field of each pledge with the week corresponding to date_collected
    $('p[data-field="date_collected"]').each((_, el) => updateDateCollected(el));

    // Replace one-on-one dates with checkmarks
    $('p[data-field="one_on_one"]').each((_, el) => oneOnOneToCheckmark(el));

    /** End code related to displaying existing pledges **/
    /*****************************************************/


    /*******************************/
    /** Related to adding pledges **/

    const csrfToken = getCookie('csrftoken');
    // These HTTP methods do not require CSRF protection
    const csrfSafeMethod = method => /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });

    // Toggles between add mode and view mode
    const addModeToggle = turnOn => {
        return () => {
            let $rowsToToggle = $(_inputTableRow).not(`.${_hiddenClass}`);
            // If add mode was toggled on and there aren't any empty form rows, add one and refresh
            // the rowsToToggle selector
            if (turnOn && $rowsToToggle.length == 0) {
                addInputFormRow();
                $rowsToToggle = $($rowsToToggle.selector);
            }

            // Change the visibility of the form rows
            const newDisplayStyle = turnOn ? 'flex' : 'none';
            $rowsToToggle.each(function() {
                $(this).css('display', newDisplayStyle);
            });
            $('.mode-add').toggle();
            $('.mode-default').toggle();
        }
    };

    // POST data from current form row, displaying form errors if they exist
    const submitPledge = cb => {
        const form = document.getElementById(_addPledgesForm.substring(1));

        // If there isn't any data to submit, just call the callback
        if ($(form).find(_inputTableRow).not(`.${_hiddenClass}`).length == 0) {
            cb();
            return;
        }

        const formData = new FormData(form);

        $.ajax({
            type: 'POST',
            url: '/strike-circle/data-entry/',
            data: formData,
            processData: false,
            contentType: false,
            success: (data, status, jqXHR) => {
                if (data.status == 'success') {
                    $(form).find(_inputTableRow).remove();
                    cb(data);
                } else if (data.status == 'unchanged') {
                    cb();
                } else if (data.status == 'error') {
                    for (let key of Object.keys(data.form_errors)) {
                        $(_addPledgesForm).find(`input[name=${key}]`).addClass('invalid')
                    }
                }
            },
            error: (jqXHR, status, error) => {
                console.log(error, status);
            }
        });
    };

    // Add newly added Pledge to the display table
    const addDataRow = rowData => {
        if (rowData) {
            $clone = $('#display-row-template .table-row').clone();
            $clone.find('.column p').each(function(_, el) {
                const fieldName = $(this).data('field');
                const fieldVal = rowData[fieldName]
                $(this).data('value', fieldVal);
                $(this).text(fieldVal);
            });
            updateDateCollected($clone.find('p[data-field="date_collected"]'));
            oneOnOneToCheckmark($clone.find('p[data-field="one_on_one"]'));
            $('.data-input > .table-row.read-only-row').not(`.${_hiddenClass}`).first().before($clone);
        }
    };

    // Add another form to the formset
    const addInputFormRow = () => {
        const $totalFormsSel = $(_addPledgesForm).find('#id_form-TOTAL_FORMS');
        const numForms = parseInt($totalFormsSel.val());
        $totalFormsSel.val(numForms + 1);
        let $clone = $('#empty-clone').clone().removeAttr('id').removeClass(_hiddenClass).removeClass('template');
        $clone.find('input, select').addBack('.input-table-row').each(function() {
            const $el = $(this);
            // Iterate over every attribute of the current element, and replace '__prefix__' in any attribute value
            // with the current number of input form rows (0-indexed)
            $.each(this.attributes, function() {
                if (this.specified && this.value.includes(_formAttrPlaceholder)) {
                    const newValue = this.value.replace(_formAttrPlaceholder, numForms);
                    $el.attr(this.name, newValue);
                }
            });
        });
        $clone.css('display', 'flex');
        $(_addPledgesForm).append($clone);

        // Set the week to the most recently selected value (& save to cookie)
        const $weekSelect = $clone.find('[data-field="date_collected"] select');
        const weekCname = 'sunrise-strike-circle-week';
        if (getCookie(weekCname)) {
            $weekSelect.val(getCookie(weekCname));
        }
        $weekSelect.change(ev => {
            const weekVal = $(ev.currentTarget).val();
            setCookie(weekCname, weekVal, 7); // save cookie for 7 days
        });
    };

    // Button actions for adding new pledges
    $('#add-pledges-button').click(addModeToggle(true));
    $('#submit-pledges-button').click(() => {
        submitPledge(_ => {
            location.reload();
            return false;
        })
    });
    $('#add-another-button').click(() => {
        submitPledge(data => {
            addDataRow(data.data);
            addInputFormRow();
        });
    });

    /** End code related to adding new pledges **/
    /********************************************/


    /*****************************************/
    /** Related to editing existing pledges **/

    // Toggles between edit mode and view mode
    const editModeToggle = () => {
        $('.mode-edit').toggle();
        $('.mode-default').toggle();

        const inViewMode = $(_editPledgesForm).hasClass(_hiddenClass);

        /*
         * This copies the original rendered formset into the _editPledgesForm element every time the user enters/re-enters edit mode.
         * Without this, any changes they made to pledges in the _editPledgesForm element would persist if they entered edit mode,
         * edited a pledge, exited edit mode, and then re-entered edit mode. When they re-entered edit mode, the form would not show
         * the correct state of any pledges they'd edited previously, and would instead still show the edits they'd made before.
        */
        if (inViewMode) {
            const $originalFormContents = $('#edit-pledges-form-original').children().clone();
            $(_editPledgesForm).html($originalFormContents);
        } else {
            $(_editPledgesForm).children().remove();
        }

        // The methods to apply to the edit form and the pledge display table, respectively, to add/remove the class 'hidden'
        const editClassMethods = inViewMode ? ['removeClass', 'addClass'] : ['addClass', 'removeClass'];

        const $hiddenEditFormEls = $(_editPledgesForm).find(_inputTableRow).addBack(_editPledgesForm);
        const $viewTableEls = $('.table-row.read-only-row');

        // Apply the methods from editClassMethods to the edit form and display table
        $hiddenEditFormEls[editClassMethods[0]](_hiddenClass);
        $viewTableEls[editClassMethods[1]](_hiddenClass);
    };

    // Button actions for editing existing pledges
    $('#edit-pledges-button').click(editModeToggle);
    $('#cancel-edit-button').click(editModeToggle);
    $('#submit-edits-button').click(() => {
        $('#edit-pledges-form').submit();
    });

    /** End code related to editing existing pledges **/
    /**************************************************/


    /** Related to both adding and editing pledges **/
    /************************************************/

    // Visually removes a row a form row from the add/edit formset, and sets the value of the hidden DELETE field for that form
    // to true, to ensure that any data associated with that form row is deleted.
    $(`${_addPledgesForm}, ${_editPledgesForm}`).on('click', '.del-row', function() {
        // By adding the "hidden" class to the row, we make sure that it doesn't get re-displayed if the user deletes
        // the row, hits the cancel button, and then re-enters add mode. addModeToggle() ignores rows with the class "hidden".
        $(this).parent().addClass('hidden');

        // Django formsets can include a hidden "DELETE" field that must be set to some truthy value added when a
        // form in the formset is to be deleted/not processed.
        // See https://docs.djangoproject.com/en/3.0/topics/forms/formsets/#understanding-the-managementform
        const formNum = $(this).parent().data('formNum');
        $(this).siblings(`input[name="form-${formNum}-DELETE"]`).val('true');
    });

    // If one-on-one display checkbox is checked, set real (hidden) one-on-one input to the current date
    $(`${_addPledgesForm}, ${_editPledgesForm}`).on('change', 'input:checkbox', function() {
        if ($(this).is(':checked')) {
            const date = new Date();
            const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
            $($(this).prev()[0]).val(dateString);
        } else {
            $($(this).prev()[0]).val(null);
        }
    });

    /** End code related to both adding and editing pledges **/
    /*********************************************************/
});

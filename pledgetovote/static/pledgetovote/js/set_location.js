$(document).ready(function() {
  // Toggle new location field based on checkbox
  $('#id_create_new_location').change(function() {
    $('#id_new_location').attr('disabled', !$(this).is(':checked'));
  });
});

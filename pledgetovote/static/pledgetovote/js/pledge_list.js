$(document).ready(function() {
  // Turn entire row into a link to the update form
  $('#pledge-list .columns').click(function() {
    const editLink = $(this).data('link');
    window.location.assign(editLink);
  });
});

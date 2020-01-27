$(document).ready(function() {
  // Turn entire row into a link to the update form, unless there aren't any pledges
  if (!$('#pledge-list .columns#no-pledges-container').length) {
    $('#pledge-list .columns').click(function() {
      const editLink = $(this).data('link');
      window.location.assign(editLink);
    });
  }
});

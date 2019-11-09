$(document).ready(function() {
  // Display file name on Choose File button
  $('#id_picture').change(function() {
    if (this.files.length > 0) {
      $(this).next().find('.file-label').html(this.files[0].name);
    }
  });

  // Click hidden image upload form field when current image is clicked
  $('.pledge-img').click(function() {
    $('#hide-img-upload input').click();
  });
});

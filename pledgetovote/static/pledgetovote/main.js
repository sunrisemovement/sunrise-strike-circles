$(document).ready(function() {
  $('#id_picture').change(function() {
    if (this.files.length > 0) {
      $(this).next().find('.file-label').html(this.files[0].name);
    }
  });

  $('#pledge-img').click(function() {
    $('#hide-img-upload input').click();
  });
});

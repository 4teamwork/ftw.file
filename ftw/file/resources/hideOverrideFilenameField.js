$(function() {

    $('#form-widgets-file input[type=radio]').change(function() {
        display = ($('input#form-widgets-file-replace').is(':checked')) ? 'none' : '';
        $('#formfield-form-widgets-filename_override').css('display', display);
    });

})

$(function() {

    $('#archetypes-fieldname-file input[type=radio]').change(function() {
        display = ($('#file_upload').is(':checked')) ? 'None' : '';
        $('#archetypes-fieldname-originFilename').css('display', display);
    });

})

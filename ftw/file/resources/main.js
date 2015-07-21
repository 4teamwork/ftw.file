$(document).ready(function(){
    uploader.init();

    $('div.sidebar a.delete-object-link').prepOverlay(
    {
        subtype: 'ajax',
        filter: common_content_filter,
        formselector: '#delete_confirmation',
        cssclass: 'overlay-delete',
        noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
        redirect: $.plonepopups.redirectbasehref,
        closeselector: '[name="form.button.Cancel"]',
        width:'50%'
    }
    );
});
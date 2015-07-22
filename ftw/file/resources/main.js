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

   $('.journal-item > a').colorbox({
      iframe: false,
      width: '90%',
      height: '90%',

      trapFocus: true,
      fixed: true,
      reposition: false,
      scrolling: true,

      transition: 'none',
      onOpen: function() {
        $('body').css('overflow', 'hidden');
        $('#colorbox').addClass('file-version-preview-colorbox');
        $('#cboxOverlay').addClass('file-version-preview-colorbox-background');
      },

      onCleanup: function() {
        $('body').css('overflow', 'scroll');
      }
    });
});
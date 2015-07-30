$(window).on("load", function() {
    initBumblebee();
});

var initBumblebee = function() {
    initFilePreviewOverlays.init();
    initShowmore.init();
};

var initFilePreviewOverlays = (function($) {
  var self = {}
  var init = function() {
      $('.journalItem > a').colorbox({
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
      $('div.sidebar a.deleteObjectLink').prepOverlay({
          subtype: 'ajax',
          filter: common_content_filter,
          formselector: '#delete_confirmation',
          cssclass: 'overlay-delete',
          noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
          redirect: $.plonepopups.redirectbasehref,
          closeselector: '[name="form.button.Cancel"]',
          width:'50%'
      });
    };
  self.init = init;
  return self;

})(jQuery);

var initShowmore = (function($) {

  var self = {},
    start = 5,
    step = 10,
    journalitems = 0,
    button,
    init = function(){
      journalitems = $('.journalItem').length;
      shown = 0,
      button = $('.showMore');
      showMoreElements(start);
      bindEvents();
    },
    bindEvents = function() {
      button.on('click', function() {
        showMoreElements(step);
      });
    },
    showMoreElements = function(nextElements){
      shown = shown + nextElements;
      $('.journalItem:lt('+ shown +')').css("display", "block");
      if(shown >= journalitems){
        button.hide();
      }else{
        button.show();
      }
    };
  self.init = init;
  return self;

}(jQuery));

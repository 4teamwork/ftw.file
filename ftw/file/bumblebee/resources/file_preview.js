$(window).on("load", function() {
    initBumblebee();
});

var initBumblebee = function() {
    initDeleteButtonOverlay.init();
    initVersionPreviewOverlay.init();
    initShowmore.init();
};

var initDeleteButtonOverlay = (function($){
  var self = {};
  var init = function() {
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
  }
  self.init = init;
  return self;
})(jQuery);

var initVersionPreviewOverlay = (function($) {
  var self = {};
  var init = function() {
      $('.journalItem > a').colorbox({
        iframe: false,
        width: '95%',
        height: '90%',

        className: 'cbFileVersionPreview',
        trapFocus: true,
        fixed: true,
        reposition: false,
        scrolling: false,
        fadeOut: 0,

        transition: 'none',
        onClosed: function() {
          $(document).trigger( "cbFileVersionPreviewClosed" );
        }
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
      $base = $('#file-preview')
      journalitems = $('.journalItem', $base).length;
      shown = 0;
      button = $('.showMore', $base);

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
      $('.journalItem:lt('+ shown +')', $base).css("display", "block");
      if(shown >= journalitems){
        button.hide();
      }else{
        button.show();
      }
    };
  self.init = init;
  return self;

}(jQuery));

$( window ).on('resize', function() {
    if ($('.cbFileVersionPreview').is(':visible')){
      $.colorbox.resize({width:$('body').width()*0.95, height:$('body').height()*0.9});
    }
  });
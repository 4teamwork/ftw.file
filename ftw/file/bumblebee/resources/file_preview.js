$(window).on("load", function() {
    initBumblebee();
});

var initBumblebee = function() {
    initDeleteButtonOverlay.init();
    initOpenInOverlay.init();
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
        width: '98%',
        height: '98%',

        className: 'cbFileVersionPreview',
        trapFocus: true,
        fixed: true,
        reposition: false,
        scrolling: false,
        fadeOut: 0,
        current: "",

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
      journalitems = $('.journal .journalItem').length;
      shown = 0;
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
      $('.journal .journalItem:lt('+ shown +')').css("display", "block");
      if(shown >= journalitems){
        button.hide();
      }else{
        button.show();
      }
    };
  self.init = init;
  return self;

}(jQuery));

var initOpenInOverlay = function($) {
    var init = function() {
      $('a.openInOverlay').colorbox({
        iframe: false,
        width: '98%',
        height: '98%',

        className: 'cbFilePreview',
        trapFocus: true,
        fixed: true,
        reposition: false,
        scrolling: true,
        fadeOut: 0,
        current: "",
        transition: 'none',
        onComplete: onComplete,
      });
  };
  var onComplete = function() {
    original_journal = $('.filePreview .journal');
    original_journal.removeClass('journal');
    initBumblebee();
    original_journal.addClass('journal');
    // After clicking a version-entry, the old journal will be deleted and is no longer
    // available for the version-colorbox. Its no longer possible to swich between the versions.
    // To fix this, we copy the given journal into the dom and it will be available for
    // the versioning-colorbox too. After closing the version-colorbox we delete it.
    // see: cbFileVersionPreviewClosed-event
    $('.journalItemLink.cboxElement').on("click", function(){
      $('#colorbox').after($('.cbFilePreview .journal').css('display', 'none').addClass('tempJournal'))
    })
  }
  $(document).on("cbFileVersionPreviewClosed", function() {
      $('.tempJournal').remove();
  })
  self.init = init;
  return self;
}(jQuery)

$( window ).on('resize', function() {
    if ($('.cbFileVersionPreview').is(':visible') || $('.cbFilePreview').is(':visible')){
      $.colorbox.resize({width:$(this).width()*0.95, height:$(this).height()*0.9});
    }
});

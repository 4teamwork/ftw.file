var progress = (function() {

  var self = {},

    curValue = 0,
    element = null,
    overlay = null,
    tick = null,
    fail = null,
    increment = 360 / 100,
    options = {
      colors: {
        barColor: '#75ad0a',
        backColor: '#000000'
      },
      templates: {
        barGtHalf: 'linear-gradient($nextdeg, $barColor 50% , transparent 50% , transparent),linear-gradient(270deg, $barColor 50% , $backColor 50% , $backColor)',
        barStHalf: 'linear-gradient(90deg, $backColor 50% , transparent 50% , transparent),linear-gradient($nextdeg, $barColor 50% , $backColor 50% , $backColor)'
      }
    },
    init = function(selector) {
      if (!selector) {
        throw "InvalidArgumentException: " + selector;
      }
      build(selector);
      value(curValue);
    },
    build = function(selector) {
      element = document.getElementById(selector);
      overlay = document.createElement('div');
      overlay.className = 'overlay';
      tick = document.createElement('img');
      tick.id = 'tick';
      tick.src = '++resource++ftw.file.resources/tick.png';
      fail = document.createElement('img');
      fail.id = 'fail';
      fail.src = '++resource++ftw.file.resources/fail.svg';
      element.appendChild(overlay);
      element.appendChild(tick);
      element.appendChild(fail);
      options.templates.barStHalf = options.templates.barStHalf.replace(/\$backColor/g, options.colors.backColor);
      options.templates.barStHalf = options.templates.barStHalf.replace(/\$barColor/g, options.colors.barColor);
      options.templates.barGtHalf = options.templates.barGtHalf.replace(/\$backColor/g, options.colors.backColor);
      options.templates.barGtHalf = options.templates.barGtHalf.replace(/\$barColor/g, options.colors.barColor);
    },
    value = function(value) {
      if (!value && value !== 0) {
        return curValue;
      }
      if (isNaN(value)) {
        throw "InvalidArgumentException: " + value;
      } else {
        value = Math.abs(Math.round(value));
        if (value > 100) {
          throw "InvalidArgumentException: " + value + " is larger than 100";
        }
        curValue = value;
        var angle;
        if (curValue < 50) {
          angle = 90 + increment * curValue;
          element.style.backgroundImage = options.templates.barStHalf.replace('$nextdeg', angle + 'deg');
        } else {
          angle = -90 + (increment * (curValue - 50));
          element.style.backgroundImage = options.templates.barGtHalf.replace('$nextdeg', angle + 'deg');
        }
        overlay.innerHTML = curValue + '%';
      }
    },
    done = function() {
      tick.style.display = 'block';
    },
    failure = function() {
      fail.style.display = 'block';
    },
    reset = function() {
      tick.style.display = 'none';
      fail.style.display = 'none';
      hide();
      curValue = 0;
      value(curValue);
    },
    show = function() {
      element.style.display = 'block';
    },
    hide = function() {
      element.style.display = 'none';
    };
  self.init = init;
  self.value = value;
  self.done = done;
  self.reset = reset;
  self.show = show;
  self.hide = hide;
  self.failure = failure;
  return self;

}());

(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'progress'], factory);
    } else {
        // Browser globals
        root.uploader= factory(root.jQuery, root.progress);
    }
}(typeof self !== 'undefined' ? self : this, function ($, progress) {
  var self = {},
    dropzone = null,
    dragging = 0,
    done = false,
    fail = false,
    overlay = null,
    $dragAndDropHint = null,
    tests = {
      filereader: null,
      dnd: null,
      formdata: null,
      progress: null
    },
    readfile = function(file) {
      var formData = tests.formdata ? new FormData() : null;
      reset();
      progress.show();
      dropzone.className = 'uploading';
      if (tests.formdata) {
        formData.append('file', file);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', context_url + '/ajax-upload');
        xhr.onload = function() {
          progress.value(0);
        };

        if (tests.progress) {
          xhr.upload.onprogress = function(event) {
            if (event.lengthComputable) {
              var complete = (event.loaded / event.total * 100 | 0);
              progress.value(complete);
            }
          };
        }
        xhr.onreadystatechange = function() {
          if (xhr.readyState == 4 && xhr.status == 200) {
            dropzone.className = 'done';
            done = true;
            progress.done();
            window.setTimeout(function() {
              updateView();
            },
              1000
            );
          } else if (xhr.readyState == 4 && xhr.status != 200) {
            dropzone.className = 'fail';
            fail = true;
            progress.failure();
            window.setTimeout(function() {
              window.location.reload();
            },
              1000
            );
          }
        };
        xhr.send(formData);
      }
    },
    bindEvents = function() {
      unbindEvents();
      if (tests.dnd) {
        $(document).on('dragenter', function(event) {
          if($.inArray('Files', event.dataTransfer.types) !== -1) {
            dragging++;
            overlay.overlay().load();
            event.preventDefault();
          }
        }).on('dragleave', function(event) {
          dragging--;
          if (dragging === 0) {
            close();
          }
        }).on('dragover', function(event) {
          event.preventDefault();
        });


        $(dropzone).on('dragover', function(event) {
          done ? this.className = 'done hover' : this.className = 'hover';
          fail ? this.className = 'fail hover' : this.className = 'hover';
          event.preventDefault();
        }).on('dragleave', function() {
          done ? this.className = 'done' : this.className = '';
          fail ? this.className = 'fail' : this.className = '';
        });

        // I could not make jQuery catch the drop event (it does work in an
        // isolated environment like codepen but not in the Plone 5
        // environment for some reason). The vanilla js implementation though
        // works just fine. ¯\_(ツ)_/¯
        document.addEventListener('drop', function (event) {
          event.preventDefault();
          $target = $(event.target);
          if (!($target.is($(dropzone)) || $target.parent().is($(dropzone)))) {
            close();
          }
        });
        dropzone.addEventListener('drop', function (event) {
          $(this).className = '';
          readfile(event.dataTransfer.files[0]);
          event.preventDefault();
        });
      }
    },
    unbindEvents = function() {
      $(dropzone).off('dragover').off('dragleave').off('drop');
      $(document).off('dragenter').off('dragleave').off('drop');
    },
    init = function() {
      $.event.props.push("dataTransfer");
      dropzone = document.getElementById('dropzone');
      $dragAndDropHint = $('#dnd-file-replacement-hint');
      progress.init('uploadprogress');
      tests.filereader = !!window.FileReader;
      tests.dnd = 'draggable' in document.createElement('span');
      tests.formdata = !!window.FormData;
      tests.progress = 'upload' in new XMLHttpRequest();
      overlay = null;
      if (!tests.filereader || !tests.dnd || !tests.formdata) {
        $dragAndDropHint.hide();
      }
      overlay = $('#dropzone').overlay({
        top: 80,
        mask: {
          maskId: 'upload-overlay',
          color: '#ededf1',
          opacity: 0.94
        },
      });
      bindEvents();
    },
    updateView = function() {
      $('.fileListing').empty();
      var updateRequest = $.get(context_url + '/file_view');
      updateRequest.done(function(data) {
        var $data = $(data);
        var $fileTable = $('.fileListing');
        var $historyTable = $('table.contentHistory');
        $fileTable.empty();
        $fileTable.html($('.fileListing tbody', $data));
        if ($historyTable.length > 0) {
          $($historyTable).empty();
          $historyTable.html($('table.contentHistory thead, table.contentHistory tbody', $data));
        }
        $(document).trigger("dndUploadViewUpdated", [$data]);
      });
      updateRequest.fail(function(data) {
        window.location.reload();
      });
      updateRequest.always(function(data) {
        close();
      });
    },
    close = function() {
      overlay.overlay().onClose = reset
      overlay.overlay().close();
    }
    reset = function() {
      dropzone.className = '';
      progress.reset();
      bindEvents();
      done = false;
      fail = false;
      dragging = 0;
    };

  self.init = init;
  return self;
}));

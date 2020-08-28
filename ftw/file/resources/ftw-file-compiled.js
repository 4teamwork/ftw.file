!function(e){"function"==typeof define&&define.amd?require(["jquery"],e):e(window.jQuery)}(function(e){e("#form-widgets-file input[type=radio]").change(function(){display=e("input#form-widgets-file-replace").is(":checked")?"none":"",e("#formfield-form-widgets-filename_override").css("display",display)})}),define("hideOverrideFilenameField",function(){}),function(e,n){"function"==typeof define&&define.amd?define("progress",[],n):e.progress=n()}("undefined"!=typeof self?self:this,function(){var e={},n=0,t=null,a=null,o=null,r=null,l={colors:{barColor:"#75ad0a",backColor:"#000000"},templates:{barGtHalf:"linear-gradient($nextdeg, $barColor 50% , transparent 50% , transparent),linear-gradient(270deg, $barColor 50% , $backColor 50% , $backColor)",barStHalf:"linear-gradient(90deg, $backColor 50% , transparent 50% , transparent),linear-gradient($nextdeg, $barColor 50% , $backColor 50% , $backColor)"}},i=function(e){if(!e)throw"InvalidArgumentException: "+e;d(e),s(n)},d=function(e){t=document.getElementById(e),a=document.createElement("div"),a.className="overlay",o=document.createElement("img"),o.id="tick",o.src="++resource++ftw.file.resources/tick.png",r=document.createElement("img"),r.id="fail",r.src="++resource++ftw.file.resources/fail.svg",t.appendChild(a),t.appendChild(o),t.appendChild(r),l.templates.barStHalf=l.templates.barStHalf.replace(/\$backColor/g,l.colors.backColor),l.templates.barStHalf=l.templates.barStHalf.replace(/\$barColor/g,l.colors.barColor),l.templates.barGtHalf=l.templates.barGtHalf.replace(/\$backColor/g,l.colors.backColor),l.templates.barGtHalf=l.templates.barGtHalf.replace(/\$barColor/g,l.colors.barColor)},s=function(e){if(!e&&0!==e)return n;if(isNaN(e))throw"InvalidArgumentException: "+e;if((e=Math.abs(Math.round(e)))>100)throw"InvalidArgumentException: "+e+" is larger than 100";n=e;var o;n<50?(o=90+3.6*n,t.style.backgroundImage=l.templates.barStHalf.replace("$nextdeg",o+"deg")):(o=3.6*(n-50)-90,t.style.backgroundImage=l.templates.barGtHalf.replace("$nextdeg",o+"deg")),a.innerHTML=n+"%"},f=function(){o.style.display="block"},c=function(){r.style.display="block"},u=function(){o.style.display="none",r.style.display="none",m(),n=0,s(n)},p=function(){t.style.display="inline-block"},m=function(){t.style.display="none"};return e.init=i,e.value=s,e.done=f,e.reset=u,e.show=p,e.hide=m,e.failure=c,e}),function(e,n){"function"==typeof define&&define.amd?define("uploader",["jquery","progress"],n):e.uploader=n(e.jQuery,e.progress)}("undefined"!=typeof self?self:this,function(e,n){var t={},a=null,o=0,r=!1,l=!1,i=null,d=null,s={filereader:null,dnd:null,formdata:null,progress:null},f=function(e){var t=s.formdata?new FormData:null;if(reset(),n.show(),a.className="uploading",s.formdata){t.append("file",e);var o=new XMLHttpRequest;o.open("POST",context_url+"/ajax-upload"),o.onload=function(){n.value(0)},s.progress&&(o.upload.onprogress=function(e){if(e.lengthComputable){var t=e.loaded/e.total*100|0;n.value(t)}}),o.onreadystatechange=function(){4==o.readyState&&200==o.status?(a.className="done",r=!0,n.done(),window.setTimeout(function(){m()},1e3)):4==o.readyState&&200!=o.status&&(a.className="fail",l=!0,n.failure(),window.setTimeout(function(){window.location.reload()},1e3))},o.send(t)}},c=function(){u(),s.dnd&&(e(document).on("dragenter",function(n){-1!==e.inArray("Files",n.dataTransfer.types)&&(o++,i.overlay().load(),n.preventDefault())}).on("dragleave",function(e){0===--o&&g()}).on("dragover",function(e){e.preventDefault()}),e(a).on("dragover",function(e){this.className=r?"done hover":"hover",this.className=l?"fail hover":"hover",e.preventDefault()}).on("dragleave",function(){this.className=r?"done":"",this.className=l?"fail":""}),document.addEventListener("drop",function(n){n.preventDefault(),$target=e(n.target),$target.is(e(a))||$target.parent().is(e(a))||g()}),a.addEventListener("drop",function(n){e(this).className="",f(n.dataTransfer.files[0]),n.preventDefault()}))},u=function(){e(a).off("dragover").off("dragleave").off("drop"),e(document).off("dragenter").off("dragleave").off("drop")},p=function(){e.event.props.push("dataTransfer"),a=document.getElementById("dropzone"),d=e("#dnd-file-replacement-hint"),n.init("uploadprogress"),s.filereader=!!window.FileReader,s.dnd="draggable"in document.createElement("span"),s.formdata=!!window.FormData,s.progress="upload"in new XMLHttpRequest,i=null,s.filereader&&s.dnd&&s.formdata||d.hide(),i=e("#dropzone").overlay({top:80,mask:{maskId:"upload-overlay",color:"#ededf1",opacity:.94}}),c()},m=function(){e(".fileListing").empty();var n=e.get(context_url+"/file_view");n.done(function(n){var t=e(n),a=e(".fileListing"),o=e("table.contentHistory");a.empty(),a.html(e(".fileListing tbody",t)),o.length>0&&(e(o).empty(),o.html(e("table.contentHistory thead, table.contentHistory tbody",t))),e(document).trigger("dndUploadViewUpdated",[t])}),n.fail(function(e){window.location.reload()}),n.always(function(e){g()})},g=function(){i.overlay().onClose=reset,i.overlay().close()};return reset=function(){a.className="",n.reset(),c(),r=!1,l=!1,o=0},t.init=p,t}),require(["hideOverrideFilenameField","progress","uploader"],function(e,n,t){}),define("main-bundle",function(){});
!function(e){"function"==typeof define&&define.amd?require(["jquery"],e):e(window.jQuery)}(function(e){e("#form-widgets-file input[type=radio]").change(function(){display=e("input#form-widgets-file-replace").is(":checked")?"none":"",e("#formfield-form-widgets-filename_override").css("display",display)})}),define("hideOverrideFilenameField",function(){}),function(e,n){"function"==typeof define&&define.amd?define("progress",[],n):e.progress=n()}("undefined"!=typeof self?self:this,function(){var e={},n=0,t=null,a=null,r=null,o=null,l={colors:{barColor:"#75ad0a",backColor:"#000000"},templates:{barGtHalf:"linear-gradient($nextdeg, $barColor 50% , transparent 50% , transparent),linear-gradient(270deg, $barColor 50% , $backColor 50% , $backColor)",barStHalf:"linear-gradient(90deg, $backColor 50% , transparent 50% , transparent),linear-gradient($nextdeg, $barColor 50% , $backColor 50% , $backColor)"}},i=function(e){if(!e)throw"InvalidArgumentException: "+e;d(e),s(n)},d=function(e){t=document.getElementById(e),a=document.createElement("div"),a.className="overlay",r=document.createElement("img"),r.id="tick",r.src="++resource++ftw.file.resources/tick.png",o=document.createElement("img"),o.id="fail",o.src="++resource++ftw.file.resources/fail.svg",t.appendChild(a),t.appendChild(r),t.appendChild(o),l.templates.barStHalf=l.templates.barStHalf.replace(/\$backColor/g,l.colors.backColor),l.templates.barStHalf=l.templates.barStHalf.replace(/\$barColor/g,l.colors.barColor),l.templates.barGtHalf=l.templates.barGtHalf.replace(/\$backColor/g,l.colors.backColor),l.templates.barGtHalf=l.templates.barGtHalf.replace(/\$barColor/g,l.colors.barColor)},s=function(e){if(!e&&0!==e)return n;if(isNaN(e))throw"InvalidArgumentException: "+e;if((e=Math.abs(Math.round(e)))>100)throw"InvalidArgumentException: "+e+" is larger than 100";n=e;var r;n<50?(r=90+3.6*n,t.style.backgroundImage=l.templates.barStHalf.replace("$nextdeg",r+"deg")):(r=3.6*(n-50)-90,t.style.backgroundImage=l.templates.barGtHalf.replace("$nextdeg",r+"deg")),a.innerHTML=n+"%"},f=function(){r.style.display="block"},u=function(){o.style.display="block"},c=function(){r.style.display="none",o.style.display="none",m(),n=0,s(n)},p=function(){t.style.display="inline-block"},m=function(){t.style.display="none"};return e.init=i,e.value=s,e.done=f,e.reset=c,e.show=p,e.hide=m,e.failure=u,e}),function(e,n){"function"==typeof define&&define.amd?require(["jquery","progress","jquery.recurrenceinput"],n):n(e.jQuery,e.progress)}("undefined"!=typeof self?self:this,function(e,n,t){var a=null,r=null,o=0,l=!1,i=!1,d=null,s=null,f=null,u={filereader:null,dnd:null,formdata:null,progress:null},c=function(t){var o=u.formdata?new FormData:null;reset(),n.show(),a.className="uploading",u.formdata&&(o.append("file",t),o.append("_authenticator",e('#dropzone [name="_authenticator"]',r).val()),f=new XMLHttpRequest,f.open("POST",context_url+"/ajax-upload"),f.onload=function(){n.value(0)},u.progress&&(f.upload.onprogress=function(e){if(e.lengthComputable){var t=e.loaded/e.total*100|0;n.value(t)}}),f.onreadystatechange=function(){4==f.readyState&&200==f.status?(a.className="done",l=!0,n.done(),window.setTimeout(function(){g()},1e3)):4==f.readyState&&200!=f.status&&(a.className="fail",i=!0,n.failure(),window.setTimeout(function(){window.location.reload()},1e3))},f.send(o))},p=function(){u.dnd&&(e(document).on("dragenter",function(n){-1!==e.inArray("Files",n.dataTransfer.types)&&(o++,d.overlay().load(),n.preventDefault())}).on("dragleave",function(e){0===--o&&y()}).on("dragover",function(e){e.preventDefault()}),e(a).on("dragover",function(e){this.className=l?"done hover":"hover",this.className=i?"fail hover":"hover",e.preventDefault()}).on("dragleave",function(){this.className=l?"done":"",this.className=i?"fail":""}),document.addEventListener("drop",function(n){n.preventDefault(),$target=e(n.target),$target.is(e(a))||$target.parent().is(e(a))||y()}),a.addEventListener("drop",function(n){e(this).className="",c(n.dataTransfer.files[0]),n.preventDefault()}))},m=function(){null!==(a=document.querySelector("body.portaltype-ftw-file-file #dropzone"))&&(r=e(a).parent(),e.event.props.push("dataTransfer"),s=e("#dnd-file-replacement-hint",r),n.init("uploadprogress"),u.filereader=!!window.FileReader,u.dnd="draggable"in document.createElement("span"),u.formdata=!!window.FormData,u.progress="upload"in new XMLHttpRequest,d=null,u.filereader&&u.dnd&&u.formdata||s.hide(),d=e(a).overlay({top:80,mask:{maskId:"upload-overlay",color:"#ededf1",opacity:.94},onClose:reset}),p())},g=function(){e(".fileListing",r).empty();var n=e.get(context_url+"/file_view");n.done(function(n){var t=e(n),a=e(".fileListing",r),o=e("table.contentHistory");a.empty(),a.html(e(".fileListing tbody",t)),o.length>0&&(e(o).empty(),o.html(e("table.contentHistory thead, table.contentHistory tbody",t))),e(document).trigger("dndUploadViewUpdated",[t])}),n.fail(function(e){window.location.reload()}),n.always(function(e){y()})},y=function(){d.overlay().close()};reset=function(){a.className="",n.reset(),l=!1,i=!1,o=0,null!==f&&(f.abort(),f=null)},e(m)}),define("uploader",function(){}),require(["hideOverrideFilenameField","progress","uploader"],function(e,n,t){}),define("main-bundle",function(){});
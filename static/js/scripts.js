function message(status, shake=false, id="") {
  if (shake) {
    $("#"+id).effect("shake", {direction: "right", times: 2, distance: 8}, 250);
  }
  document.getElementById("feedback").innerHTML = status;
  $("#feedback").show().delay(2000).fadeOut();
}

function error(type) {
  $("."+type).css("border-color", "#E14448");
}

var login = function() {
  if($("#login-user").val()){
    $.post({
      type: "POST",
      url: "/",
      data: {"username": $("#login-user").val(),
             "password": $("#login-pass").val()},
      success(response){
        var status = JSON.parse(response)["status"];
        if (status === "Login successful") { location.reload(); }
        else { error("login-input"); }
      }
    });
  }
};

$(document).ready(function() {

  $(document).on("click", "#login-button", login);
  $(document).keypress(function(e) {if(e.which === 13) {login();}});

  $(document).on("click", "#signup-button", function() {
    $.post({
      type: "POST",
      url: "/signup",
      data: {"username": $("#signup-user").val(),
             "password": $("#signup-pass").val(),
             "email": $("#signup-mail").val()},
      success(response) {
        var status = JSON.parse(response)["status"];
        if (status === "Signup successful") { location.reload(); }
        else { message(status, true, "signup-box"); }
      }
    });
  });

  $(document).on("click", "#save", function() {
    $.post({
      type: "POST",
      url: "/settings",
      data: {"username": $("#settings-user").val(),
             "password": $("#settings-pass").val(),
             "email": $("#settings-mail").val()},
      success(response){
        message(JSON.parse(response)["status"]);
      }
    });
  });
});

//document.querySelector( "form" ).addEventListener( "submit", function() {
$(document).on("click", "#addProject", function() {
    $.post({
      type: "POST",
      url: "/project",
      data: {"title": $("#title").val(),
             "description": $("#description").val()},
      success(response) {
        var status = JSON.parse(response)["status"];
        if (status === "Added") { location.reload(); }
        else { error("project-input"); }
      }
    });
});

var selectedOffer = "";

function selectCheck()
{
    ar = document.getElementById("getDescription").children;
    for (i = 0; i < ar.length; ++i){
        document.getElementById(ar[i].id).style.display = "none";
     }
    var e = document.getElementById("getTitle");
    var strUser = e.options[e.selectedIndex];
    if(strUser){
      selectedOffer = strUser.value + " " + document.getElementById(strUser.value).innerHTML;
      document.getElementById(strUser.value).style.display = "block";
    }
}

if(document.getElementById("getTitle")){
  document.getElementById("getTitle").onchange = function() {selectCheck()};
  selectCheck();
}

var inputCVs = {};
var finalFilesNames = "<b>Added files</b> :<br /> ";

var handleFileSelect = function(evt) {
    var files = evt.target.files;
    //var file = files[0];
    console.log(files);
    for (var i = 0; i < files.length; i++) {
    	//var file = files[i];
      (function(file) {
        var reader = new FileReader();
              if (files && file) {
                  //var reader = new FileReader();
                  console.log(file);
                  reader.onload = function(readerEvt) {
                      var binaryString = readerEvt.target.result;
                      var pdfData = atob(btoa(binaryString));

                      // Loaded via <script> tag, create shortcut to access PDF.js exports.
                      var pdfjsLib = window['pdfjs-dist/build/pdf'];
                      // The workerSrc property shall be specified.
                      pdfjsLib.GlobalWorkerOptions.workerSrc = '//mozilla.github.io/pdf.js/build/pdf.worker.js';
                      // Using DocumentInitParameters object to load binary data.
                      var loadingTask = pdfjsLib.getDocument({data: pdfData});
                      loadingTask.promise.then(function(pdf) {
                      console.log('PDF loaded');
                      var allPdfText = "";
                      console.log(file);
                      for (var j = 1; j <= pdf.numPages; j++) {
                        (function( j ) {
                            pdf.getPage(j).then(function(page) {
                              console.log('Page loaded');
                              page.getTextContent().then( function(textContent){
                                var finalArray = textContent.items.map(function (obj) {
                                  return obj.str;
                                });
                                allPdfText = allPdfText + finalArray.join(' ')+ " ";
                                if(j == pdf.numPages){
                                  inputCVs[file.name] = allPdfText;
                                  finalFilesNames = finalFilesNames + file.name + "<br />";
                                  document.getElementById("nbAddedFile").innerHTML = finalFilesNames.substring(0, finalFilesNames.length - 1);;
                                }
                              });
                            });
                          })( j );
                       }
                    }, function (reason) {
                      // PDF loading error
                      console.error(reason);
                    });

                  };

                  reader.readAsBinaryString(file);
              }
          })(files[i]);
    }
    console.log(inputCVs);
};

if (window.File && window.FileReader && window.FileList && window.Blob && document.getElementById('filePicker')) {
    document.getElementById('filePicker').addEventListener('change', handleFileSelect, false);
} else {
    console.log('The File APIs are not fully supported in this page.');
}

$(document).on("click", "#analyze", function() {
    $.post({
      type: "POST",
      url: "/analyze",
      data: {"CVs": inputCVs,
             "__offer__": selectedOffer},
      success(response) {
        var status = JSON.parse(response)["status"];
        var data = JSON.parse(response)["data"];
        if (status === "Added") { console.log(response); document.getElementById("results").innerHTML = data}
        else { error("project-input"); }
      }
    });
});

// Open or Close mobile & tablet menu
// https://github.com/jgthms/bulma/issues/856
$("#navbar-burger-id").click(function () {
  if($("#navbar-burger-id").hasClass("is-active")){
    $("#navbar-burger-id").removeClass("is-active");
    $("#navbar-menu-id").removeClass("is-active");
  }else {
    $("#navbar-burger-id").addClass("is-active");
    $("#navbar-menu-id").addClass("is-active");
  }
});

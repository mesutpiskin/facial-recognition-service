var train_data = {
  name: "",
  file: null
};

var recognize_data = {
  file: null
};

var message = null;
var active_section = null;

function render() {
  // clear form data

  $(".form-item input").val("");
  $(".tabs li").removeClass("active");
  $(".tabs li:first").addClass("active");

  active_section = "train-content";

  $("#" + active_section).show();
}
function update() {
  if (message) {
    // render message

    $(".message").html(
      '<p class="' +
        _.get(message, "type") +
        '">' +
        _.get(message, "message") +
        "</p>"
    );
  } else {
    $(".message").html("");
  }

  $("#train-content, #recognize-content").hide();
  $("#" + active_section).show();
}

$(document).ready(function() {
  // listen for file added

  $("#train #input-file").on("change", function(event) {
    //set file object to train_data
    train_data.file = _.get(event, "target.files[0]", null);
  });

  // listen for name change
  $("#name-field").on("change", function(event) {
    train_data.name = _.get(event, "target.value", "");
  });

  // listen tab item click on

  $(".tabs li").on("click", function(e) {
    var $this = $(this);

    active_section = $this.data("section");

    // remove all active class

    $(".tabs li").removeClass("active");

    $this.addClass("active");

    message = null;

    update();
  });

  // listen the form train submit

  $("#train").submit(function(event) {
    message = null;

    if (train_data.name && train_data.file) {
      // do send data to backend api

      var train_form_data = new FormData();

      train_form_data.append("name", train_data.name);
      train_form_data.append("file", train_data.file);

      axios
        .post("/api/train", train_form_data)
        .then(function(response) {
          message = {
            type: "success",
            message:
              _.get(response, "data")
          };

          train_data = { name: "", file: null };
          update();
        })
        .catch(function(error) {
          message = {
            type: "error",
            message: _.get(
              error,
              "response.data.error.message",
              "Hata"
            )
          };

          update();
        });
    } else {
      message = { type: "error", message: "İsim ve fotoğraf alanı zorunludur." };
    }

    update();
    event.preventDefault();
  });

  // listen for recognize file field change
  $("#recognize-input-file").on("change", function(e) {
    recognize_data.file = _.get(e, "target.files[0]", null);
  });
  // listen for recognition form submit
  $("#recognize").submit(function(e) {
    // call to backend
    var recog_form_data = new FormData();
    recog_form_data.append("file", recognize_data.file);

    axios
      .post("/api/recognize", recog_form_data)
      .then(function(response) {

        message = {
          type: "success",
          message:
            "<img width='720px' height='600px'  src='data:image/png;base64, "+response.data+"'/>"
        };

        recognize_data = { file: null };
        update();
      })
      .catch(function(err) {
        message = {
          type: "error",
          message: _.get(err, "response.data.error.message", "Hata")
        };

        update();
      });
    e.preventDefault();
  });

  // clear data form submit
  $("#clear").submit(function(e) {
    // call to backend
    axios
      .post("/api/clear")
      .then(function(response) {
        message = {
          type: "success",
          message: response.data
        };

    

        update();
      })
      .catch(function(err) {
        message = {
          type: "error",
          message: _.get(err, "response.data.error.message", "Hata")
        };
       
        update();
      });
    e.preventDefault();
  });

  $("#faces").submit(function(e) {
    // call to backend
    axios
      .post("/api/faces")
      .then(function(response) {
        message = {
          type: "success",
          message: response.data
        };

    

        update();
      })
      .catch(function(err) {
        message = {
          type: "error",
          message: _.get(err, "response.data.error.message", "Hata")
        };
       
        update();
      });
    e.preventDefault();
  });
  // render the app;
  render();
});

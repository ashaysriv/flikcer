$(document).ready(function() {
  $(".hide").hide();
  $('.input-button .loader-2').hide();
  $(".loader").show();
  $('#iterations-button').click(function() {
    $("html, body").animate({scrollTop: $('#iterations-button').offset().top - 200}, 500);
    $(".iteration").slideDown();
    $(".input-number-button .loader-2").hide();
  })
  $('#time-button').click(function() {
    $("html, body").animate({scrollTop: $('#time-button').offset().top - 200}, 500);
    $(".time-stamps").slideDown();
  })
  // $('.input-number-button').click(function() {
  //   $(".input-number-button .loader-2").show();
  //   $(".input-number-button img").hide();
  // })
})

let global_uuid;
let global_url;

$(document).ready(function() {
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    var activeTab = tabs[0];
    global_url = activeTab.url
    console.log(global_url)
  });

  $('#url-button').click(function() {
    $(".hide").hide();
    $(".loader").show();
    $("html, body").animate({scrollTop: $('#s1-inputs').offset().top}, 1000);
    $('#step-1 p').text("Reading YouTube URL")
    $('#step-2 p').text("Analysing Frames")
    $('#step-3 p').text("Detecting Possible Epilepsy Triggers")
    $('#time-stamps-list').empty();
    $(".s1-steps, #step-1").slideDown();
    
    let interval;

    console.log(global_url)

    function getUUID() {
      $.ajax({
        url: "https://flikcerapp.herokuapp.com/num_triggers/",
        method: "GET",
        dataType: "JSON",
        data: {
          password: 'featherx',
          url: global_url,
        },
        success: (data) => {
          console.log(data)
          global_uuid = data.uuid;
          interval = setInterval(() => updateData(data.uuid), 1000);
        },
        error: (e) => {
          console.error(e)
        }
      })
    }

    getUUID();

    function updateData(uuid_from_url) {
      $.ajax({
        url: "https://flikcerapp.herokuapp.com/num_triggers/poll/",
        method: "GET",
        dataType: "JSON",
        data: {
          password: 'featherx',
          uuid: uuid_from_url,
        },
        success: (data) => {
          console.log(data)
          if (data.status === "done" || data.status === "error") {
            clearInterval(interval);
          }
          setData(data);
        },
        error: (e) => {
          console.error(e)
        }
      })
    }

    function setData(data) {

      if (data.video_title === "exceeded") {
        $(".hide").slideUp()
        $("#size-alert").slideDown()
      }

      if (data.status === "error") {
        $(".hide").slideUp()
        $("#size-alert").text("An error occurred.")
        $("#size-alert").slideDown()
      }

      if (data.status === "downloading" || data.status === "done") {
        $("#step-1 .loader").hide();
        $("#step-1 img").show();
        $('#step-1 p').text('Loaded ' + data.video_title)
        $("#step-2").slideDown();
        $('#step-2 p').text('Analysing Frames ' + data.progress + " of " + data.num_frames)
      }

      if (data.progress > 0 && data.progress === data.num_frames) {
        $("#step-2 .loader").hide();
        $("#step-2 img").show();
        $('#step-2 p').text('Analysed Frames ' + data.progress + " of " + data.num_frames)
        $("#step-3").slideDown();
      }

      if (data.status === "done") {
        $("#step-3 .loader").hide();
        $("#step-3 img").show();
        $('#step-3 p').text("Detected Possible Epilepsy Triggers")
        $("#s1-result").slideDown();
        $('.result div').text(data.num_triggers)
        $("html, body").animate({scrollTop: $('#s1-result').offset().top}, 500);
        if (data.num_triggers > 0){
          $("#time-button").show()
          $("#iterations-button").show()
        }

        const array = data.dangerous_frames;

        $('#time-stamps-list').empty();

        for (let i = 0; i < array.length; i++) {
          const list = document.getElementById('time-stamps-list');
          const item = document.createElement('li');
          item.appendChild(document.createTextNode(array[i]));
          list.appendChild(item);
        }
      }
    }

  });
});
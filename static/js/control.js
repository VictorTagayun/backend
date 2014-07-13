var bot = new CoderBot()

$(document).on( "pagecontainershow", function(){
    ScaleContentToDevice();
    
    $(window).on("resize orientationchange", function(){
        ScaleContentToDevice();
    })
});

function ScaleContentToDevice(){
    scroll(0, 0);
    var content = $.mobile.getScreenHeight() - $(".ui-header").outerHeight() -         $(".ui-footer").outerHeight() - $(".ui-content").outerHeight() + $(".ui-content").height();
    $(".ui-content").height(content);
}

if($('#page-control')) {
$(document).on( "pageshow", '#page-control', function( event, ui ) {
      $('[href="#page-control"]').addClass( "ui-btn-active" );
      $('[href="#page-program"]').removeClass( "ui-btn-active" );
});

$(document).on( "pagecreate", '#page-control', function( event ) {
	if(('ontouchstart' in window) ||
     	   (navigator.maxTouchPoints > 0) ||
     	   (navigator.msMaxTouchPoints > 0)) {
       	        /* browser with either Touch Events of Pointer Events running on touch-capable device */	
		$('#b_forward')
	  	.on("touchstart", function (){console.log("start"); bot.forward(100,-1);})
	  	.on("touchend", function (){console.log("end"); bot.stop();});
		$('#b_backward')
	  	.on("touchstart", function (){bot.backward(100,-1);})
	  	.on("touchend", function (){bot.stop();});
		$('#b_left')
	  	.on("touchstart", function (){bot.left(60,-1);})
	  	.on("touchend", function (){bot.stop();});
		$('#b_right')
	  	.on("touchstart", function (){bot.right(60,-1);})
	  	.on("touchend", function (){bot.stop();});
	} else {
		$('#b_forward')
          	.on("mousedown", function (){bot.forward(100, -1);})
	  	.on("mouseup", function (){bot.stop();})
		$('#b_backward')
          	.on("mousedown", function (){bot.backward(100, -1);})
	  	.on("mouseup", function (){bot.stop();})
		$('#b_left')
	  	.on("mousedown", function (){bot.left(60,-1);})
	  	.on("mouseup", function (){bot.stop();})
		$('#b_right')
          	.on("mousedown", function (){bot.right(60, -1);})
	  	.on("mouseup", function (){bot.stop();})
	}
	$('#b_say').on("click", function (){
		var text = $('#i_say').val();
                bot.say(text);
	});
	$('.b_camera').on("click", function (){
		var param = $(this).attr('data-param');
		bot.set_handler(param);
                $('#f_stream').attr('src', $('#f_stream').attr('src'));
	});
	$('#b_halt').on("click", function (){
		if(confirm("Shutdown CoderBot?")){
			bot.halt();
		}
	});
});
}

$(document).on( "pagecreate", '#page-preferences', function( event ) {
	$('#f_config').on("submit", function (){
		var form_data = $(this).serialize();
                $.post(url='/config', form_data, success=function(){
                  alert("saved ok");
                  location.href="/";
                });
                return false;
	});
});

        Mousetrap.bind(['command+alt+s', 'ctrl+alt+k'], function(e) {
          $.mobile.pageContainer.pagecontainer('change', '#page-preferences');
          return false;
        });
        botStatus();

function botStatus() {
  $.ajax({url:'/bot/status',dataType:'json'})
  .done(function (data) {
    if(data.status == 'ok') {
      $('.s_bot_status').text('Online').removeClass('ui-icon-alert ui-btn-b').addClass('ui-icon-check ui-btn-a');
    } else {
      $('.s_bot_status').text('Offline').removeClass('ui-icon-check ui-btn-a').addClass('ui-icon-alert ui-btn-b');
    }})
  .error(function() {
    $('.s_bot_status').text('Offline').removeClass('ui-icon-check ui-btn-a').addClass('ui-icon-alert ui-btn-b');
  });
  setTimeout(botStatus, 1000);
}


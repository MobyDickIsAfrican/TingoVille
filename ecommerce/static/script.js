
var x;

$(document).on("click", ".img-responsive", function() {
    x= $(this).attr("id");
    var myImgSrc = document.getElementById(x).src;
    document.getElementById('IneverChange').src = myImgSrc;
});
var p;
$('btn').on("click",function(){
  $(document).ready(function(){
      $.ajax({
  	url: configuration['ecommerce']['ajax_view'],
  	cache: false,
  	type: "GET",
  	success: function(data){
      p=data;
  	}
           });
      });
});
 console.log(p)
if(p != null){
  $(document).ready(function(){
      $.ajax({
  	url: configuration['ecommerce']['ajax_view'],
  	cache: false,
  	type: "POST",
  	data: {"id": x, "var1":p[0].var1}
  	success: function(data){
  	},
  	beforeSend: function(xhr, settings){
  	    xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
  	}
      });
  });



}

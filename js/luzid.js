$(document).ready(function(){

	psyArchiveToggle();
	try{
		$('.lucid_post a>img, .lucid_page_gallery a>img, .lucid_page_zyu a>img').parent().magnificPopup({type:'image'});
	}catch(e){
		console.log(e);
	}

		$("#side_column .men").click(function () {
	    	$("#side_column").toggleClass('activ');
		  });

	if(location.hash){

		show_class = location.hash.substring(1);

		if($('.lucid_post.'+show_class)[0]){

			$('.lucid_post.'+show_class).fadeIn(400);

			if (show_class.substring(0, 6) == "title_") {
			    $('.lucid_post.'+show_class+' .lucid_more').show();
				$('.lucid_readmore').hide();
			}

		}else{

			$('.lucid_post').fadeIn(400);
		}

	}else{
		$('.lucid_post').fadeIn(400);
	}

	if(window.location.hash){
		var loc = window.location.hash.substring(1);
		if(loc.indexOf('lucid_cat_') == 0){
			lucid_show_cat(0, parseInt(loc.substring('lucid_cat_'.length))+1);
		}else if(loc.indexOf('title_') == 0){
			lucid_show_title(0, loc.substring('title_'.length));
		}else if(loc.indexOf('year_') == 0){
			lucid_show_date(0, loc.substring('year_'.length), 'year');
		}else if(loc.indexOf('yearmon_') == 0){
			lucid_show_date(0, loc.substring('yearmon_'.length), 'yearmon');
		}

	}
	$(document.body).animate({opacity: 1}, 500);
});

function lucid_more(self){
	
	var lmore =  $(self).parent().parent().find('.lucid_more');

  console.log(lmore);
	var isvis = lmore.is(':visible');

	$('.lucid_readmore').show();
	$('.lucid_content .lucid_more').hide();
	if(isvis){
		lmore.fadeOut(400);
	}else{
		lmore.fadeIn(400);
	}
	
}
function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

function check_location(hash){
	var cur_file = endsWith(location.href, '/')? 'index.html' : location.href.split("/")[location.href.split("/").length-1];
	if(cur_file !=LUCID_INDEX){
		location.href = location.href.replace(cur_file, LUCID_INDEX)+"#"+hash;
	}
}

function lucid_show_cat(self, cat_num){

  if(cat_num=="inner"){
    $('.lucid_cat_side').each(function(i, el){
      if(el.innerHTML.split(" ")[0]==self.innerHTML.split(" ")[0].toLowerCase()){
        //cat_num = parseInt(el.className.replace("lucid_cat_side_", "").replace("lucid_cat_side", "").replace(" ", ""))+1;
        cat_num = parseInt(el.getAttribute("num"));
        return;
      }
    });
    
  }

  if(cat_num=="inner") return;

	check_location('lucid_cat_'+(cat_num-1));
	
	$('.lucid_readmore').show();
	$('.lucid_post .lucid_more').hide();	
	if(cat_num){
		$('.lucid_post').hide();
		$('.lucid_post.lucid_cat_'+(cat_num-1)).fadeIn(400);
	}else{
		$('.lucid_post').fadeIn(400);
	}
}

function lucid_show_title(self, title){

		check_location('title_'+title);

		$('.lucid_post').hide();
		$('.lucid_post.title_'+title+' .lucid_more').show();
		$('.lucid_post.title_'+title).fadeIn(400);	
		$('.lucid_readmore').hide();
}

function lucid_show_date(self, dateval, datetype){

	check_location(datetype+'_'+dateval);

	$('.lucid_readmore').show();
	$('.lucid_post .lucid_more').hide();	

	$('.lucid_post').hide();
	$('.lucid_post.'+datetype+'_'+dateval).fadeIn(400);		
}

var LUCID_MENU_SCROLLER_SET = false;

function lucid_menu_toggle(self){

	var w = ($('#lucid_fixed_content').is(':visible'))? 100 : 300;
	if(w == 300){
		$('#lucid_fixed').width(w);
	}

	$('#lucid_fixed_content').fadeToggle(400, function(){

		if(w == 100){
			$('#lucid_fixed').width(w);
		}
	});

	if(!LUCID_MENU_SCROLLER_SET){
		$("#lucid_fixed_content").nanoScroller();

		LUCID_MENU_SCROLLER_SET = true;
	}
}

function psyArchiveToggle(){

  $('.psy_archive a.toggle').click(function(){

    var arch_elems = $(this).closest(".psy_archive")
      .children(".psy_archive_elems");
    var el_open = arch_elems.children(".el_open").html();
    var el_closed = arch_elems.children(".el_closed").html();

    if($(this).children('span').hasClass("toggle-open")){

      $(this).parent().children("ul").children("li")
        .hide(400, function(){

      });
      $(this).children('span')
        .addClass("toggle-closed")
        .removeClass("toggle-open").html(el_closed);

    }else{

      $(this).parent().children("ul").children("li")
        .show(400, function(){

      });
      $(this).children('span')
        .removeClass("toggle-closed")
        .addClass("toggle-open").html(el_open);

    }

  });

}



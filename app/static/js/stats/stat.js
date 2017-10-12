/**
 * Menu on click functions
 */
$(document).ready(function() {

        $(".btn-pref .btn").click(function () {
            if (this.id == 'topstats-tab'){
                $('#tab1').hide();
                $('#tab2').show();
                $('#tab2').addClass('active in');
                $('#tab1').removeClass('active in');
            }
            else if (this.id == 'standings-tab'){
                $('#tab2').hide();
                $('#tab1').show();
                $('#tab1').addClass('active in');
                $('#tab2').removeClass('active in');
            }
            $(".btn-pref .btn").removeClass("btn-info").addClass("btn-default");
            $(this).removeClass("btn-default").addClass("btn-info");
        });

});

/**
 * Main function to direct logic on menu click
 * @param league = league stats to load
 */
function load_stats(league) {
    close_menu();
    $('#errorAlert-2').hide();
    $('#errorAlert-1').hide();
    $('#league_logo').empty();
    var logo_path = logos_map(league);
    $('#league_logo').append('<img src="/static/logos/' + logo_path[0] + '">');
    $('#title').text(logo_path[1]);
    $('#load-league-1').text(logo_path[1]);
    $('#load-league-2').text(logo_path[1]);
    $('#current_league_name').text(league);

    load_data(league);
}


/**
 * Collapse menu onclick
 */
function close_menu() {
    $('#menu-button').removeClass();
    $('#menu-button').next().removeClass();
    $('#menu-button').next().css("display", "none");;
}

/**
 * Static content to be loaded through menu pick
 * @returns logo picture, league name
 */
function logos_map(league) {
    var logos = {
        'epl': ['epl-menu.jpg', 'Premier League'],
        'liga': ['liga-menu.png', 'La Liga'],
        'bundesliga': ['bundesliga-menu.png', 'Bundesliga'],
        'ligue1': ['ligue1-menu.png', 'Ligue 1'],
        'seriea': ['seriea-menu.png', 'Serie A']
    };

    return logos[league];
}

/**
 * AJAX request logic (called from Menu)
 */
function load_data(league) {
    if ($('#standings-tab').hasClass('btn-info')) {
        $('#standings_content').empty();
        $('#gif-tab1').show();
        $('#load-msg-2').show();
        AJAX_standings(league);
    }

    else if ($('#topstats-tab').hasClass('btn-info')) {
        $('#topstats_content').empty();
        $('#gif-tab2').show();
        $('#load-msg-1').show();
        AJAX_topstats(league);
    }
}

/**
 * AJAX request logic (called from Tab)
 */
function load_extra_tab(league){
    if ($('#standings-tab').hasClass('btn-info')) {
        $('#standings_content').empty();
        $('#load-msg-1').hide();
        $('#gif-tab1').show();
        AJAX_standings(league);
    }

    else if ($('#topstats-tab').hasClass('btn-info')) {
        $('#topstats_content').empty();
        $('#load-msg-2').hide();
        $('#gif-tab2').show();
        AJAX_topstats(league);
    }

}

/**
 * AJAX request for Standings
 */
function AJAX_standings(league){
    $.ajax({
            type: 'POST',
            url: '/stats/standings-ajax',
            data: {
                'league': league
            }
        })
            .done(function (data) {
                if (data.status == 400) {
                    $('#ajax-fail-1').show();            // Create an alert message
                }
                else {
                    console.log(data);
                    $('#standings_content').append(standings_tbody(data));
                    $('#gif-tab1').hide();
                }
            });
}

/**
 * AJAX request for Top Scorers & Assists
 */
function AJAX_topstats(league){
    $.ajax({
            type: 'POST',
            url: '/stats/topstats-ajax',
            data: {
                'league': league
            }
        })
            .done(function (data) {
                if (data.status == 400) {
                    $('#ajax-fail-2').show();
                }
                else {
                    console.log(data);
                    $('#topstats_content').append();
                    $('#gif-tab2').hide();
                }
            });
}

/**
 * JS function to generate Standings HTML table body
 */
function standings_tbody(data){
    var top = '<tr class="warning">'+
                    '<th style="width: 10px;"></th>' +
                    '<th style="width: 60px;">Team Name</th>' +
                    '<th style="width: 10%;">MP</th>' +
                    '<th style="width: 10%;">W&nbsp;</th>' +
                    '<th style="width: 10%;">D&nbsp;</th>' +
                    '<th style="width: 10%;">L&nbsp;</th>' +
                    '<th style="width: 10%;">GD</th>' +
                    '<th style="width: 10%;">Pts</th>' +
                    '<th style="width: 10%;">Form</th>' +
               '</tr>';

    var end = '<tr class="warning"><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>';

    var html = '';
    // console.log(data);
    var jsonData = JSON.parse(data);

    for (var key in jsonData) {
        if (jsonData.hasOwnProperty(key)) {

            if (key == '1' || key == '2' || key == '3'){
                html += '<tr class="success">';
            }
            else if (key == '18' || key == '19' || key == '20'){
                html += '<tr class="danger">';
            }
            else {
                html += '<tr>';
            }

            if ($(window).width() > 768) {
                html += '<td style="text-align:center;">' + jsonData[key].rank + '.</td>';
            }
            else {
                html += '<td style="padding-left:2px;padding-right:0px;">' + jsonData[key].rank + '.</td>';
            }

            html +=     '<td>' + jsonData[key].name + '</td>' +
                        '<td>' + jsonData[key].mp + '</td>' +
                        '<td>' + jsonData[key].w + '</td>' +
                        '<td>' + jsonData[key].d + '</td>' +
                        '<td>' + jsonData[key].l + '</td>' +
                        '<td>' + jsonData[key].gd + '</td>' +
                        '<td>' + jsonData[key].pts + '</td>' +
                        '<td><a onclick="showForm(\'' + jsonData[key].name + '\',\'' + jsonData[key].form + '\')" class="btn btn-xs" data-toggle="modal" data-target="#standingsModal" style="background: #22aba6;color: white;"><i class="menu-icon icon-bar-chart"></i> Show</a></td>' +
                    '</tr>';
        }
    }

    return '<tbody>' + top + html + end + '</tbody>';
}

/**
 * Helper function to render Team's form
 */
function showForm(title, form){
    $('#standingsModalLabel').text(title + "'s Form");
    $('#modal-content-form').html(modalBody(form));
}

/**
 * Helper function to showForm to generate Modal's HTML
 */
function modalBody(data){
    var html =  '<div class="row" style="margin-top:0px;text-align:center;padding-bottom:10px;">' +
                    '<div class="col-md-3 col-xs-3" style="padding-left: 0px;padding-right: 0px;">' +
                        '<span><strong> Date </strong></span>' +
                    '</div>' +
                    '<div class="col-md-8 col-xs-8" style="padding-left: 0px;padding-right: 0px;">' +
                        '<span><strong> Match Results </strong></span>' +
                    '</div>' +
                    '<div class="col-md-1 col-xs-1" style="padding-left: 0px;padding-right: 0px;">' +
                        '<span><strong></strong></span>' +
                    '</div>' +
                '</div>';

    var form = data.split(',');

    for(var i=0; i < form.length; i+=3) {
        html += '<div class="row" style="margin-top:0px;text-align:center;">' +
                    '<div class="col-md-3 col-xs-3" style="padding-bottom:5px;padding-left: 0px;padding-right: 0px;">' +
                        '<span>' + form[i + 2] + '</span>' +
                    '</div>' +
                    '<div class="col-md-8 col-xs-8" style="padding-bottom:5px;padding-left: 0px;padding-right: 0px;">' +
                        '<span>' + form[i + 1] + '</span>' +
                    '</div>' +
                    '<div class="col-md-1 col-xs-1" style="padding-bottom:5px;padding-left: 0px;padding-right: 0px;">' +
                        '<span>' + map_result(form[i]) + '</span>' +
                    '</div>' +
                '</div>';
    }

    return html;
}

/**
 * Helper function to modalBody to generate Win/Lose/Draw button UI
 */
function map_result(result){
    var form = {
        'L': '<a class="btn btn-xs" style="background: #d9534f;color: white;width:25px;">L</a>',
        'W': '<a class="btn btn-xs" style="background: #5cb85c;color: white;width:25px;">W</a>',
        'D': '<a class="btn btn-xs" style="background: #f0ad4e;color: white;width:25px;">D</a>'
    };

    return form[result];
}


/**
 * Menu
 */
(function($) {

  $.fn.menumaker = function(options) {

      var cssmenu = $(this), settings = $.extend({
        title: "Menu",
        format: "dropdown",
        sticky: false
      }, options);

      return this.each(function() {
        cssmenu.prepend('<div id="menu-button">' + settings.title + '</div>');
        $(this).find("#menu-button").on('click', function(){
          $(this).toggleClass('menu-opened');
          var mainmenu = $(this).next('ul');
          if (mainmenu.hasClass('open')) {
            mainmenu.hide().removeClass('open');
          }
          else {
            mainmenu.show().addClass('open');
            if (settings.format === "dropdown") {
              mainmenu.find('ul').show();
            }
          }
        });

        cssmenu.find('li ul').parent().addClass('has-sub');

        multiTg = function() {
          cssmenu.find(".has-sub").prepend('<span class="submenu-button"></span>');
          cssmenu.find('.submenu-button').on('click', function() {
            $(this).toggleClass('submenu-opened');
            if ($(this).siblings('ul').hasClass('open')) {
              $(this).siblings('ul').removeClass('open').hide();
            }
            else {
              $(this).siblings('ul').addClass('open').show();
            }
          });
        };

        if (settings.format === 'multitoggle') multiTg();
        else cssmenu.addClass('dropdown');

      });
  };
})(jQuery);

(function($){
    $(document).ready(function(){

        $(document).ready(function() {
          $("#cssmenu").menumaker({
            title: "Choose League / Competition",
            format: "multitoggle"
          });

        });


    });
})(jQuery);
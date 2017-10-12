/**
 * Helper Functions
 */

/*  Redirects the button click to the link page */
function create_fixtures_table(data, league_id, card_content) {
    var JSONdata = JSON.parse(data);                    // JSON content

    var jsonCount = Object.keys(JSONdata).length;

    var top =   '<div>' +
                    '<div class="table-responsive">' +
                        '<table class="table table-striped table-hover">';

    // loop through all JSON items
    var allContent = '';
    for (var x = 0; x < jsonCount; x++){

        // Hide all of the future fixtures (hide each tables while giving them a unique id to be displayed if necessary)
        if (x != 0) {
            var table_top = '<div class="table-responsive" style="display: none;" id="' + league_id + x + '">' +
                                '<table class="table table-striped table-hover">';
        }

        // Provide fixture's game date (weekday date month)
        var thead = '<thead><tr class="info"><th colspan="4">' + JSONdata[x][0].game_date + '</th></tr></thead>'

        var game = '';
        for (var i = 0; i < JSONdata[x][0].content.length; i++) {
            game +=            '<tr>' +
                                    '<td style="width: 15%;">' + JSONdata[x][0].content[i][0] + '</td>' +
                                    '<td style="text-align: right;width: 30%;">' + JSONdata[x][0].content[i][2] + '<img src=' + JSONdata[x][0].content[i][1] + ' width="22" height="22" style="margin-left: 5px;"></td>' +
                                    '<td style="width: 10%;text-align: center;">vs.</td>' +
                                    '<td><img src="' + JSONdata[x][0].content[i][4] + '" width="22" height="22" style="margin-right: 5px;">' + JSONdata[x][0].content[i][3] + '</td>' +
                                '</tr>';
        }

        // yellow line separator with button to display next fixtures (Next Game Week)
        if (x != jsonCount - 1){
            if (!card_content){
                var nxt_fixtures = '<tr class="warning" style="text-align: center;">' +
                                        '<td></td><td></td>' +
                                            '<td style="padding: 3px 0px 3px 0px;">' +
                                            '</td>' +
                                        '<td></td>' +
                                    '</tr>' +
                                '</table>' +
                            '</div>' +
                            '<div style="text-align: center;">';

                if (x == 0){
                    var nxt_btn =   '<a id="' + league_id + '-btn' + x + '" onclick="showNext(\'' + league_id + (x+1) + '\',\'' + league_id + '-btn' + x + '\', \'' + league_id + '-btn' + (x+1) + '\')" class="btn btn-sm" style="background: #22aba6;color: white;">' +
                                        '<i class="icon-calendar-plus-o"></i> More Fixtures' +
                                    '</a>'+
                                '</div> ';
                } else {
                    var nxt_btn =   '<a id="' + league_id + '-btn' + x + '" onclick="showNext(\'' + league_id + (x+1) + '\',\'' + league_id + '-btn' + x + '\', \'' + league_id + '-btn' + (x+1) + '\')" class="btn btn-sm" style="background: #22aba6;color: white;display: none;">' +
                                        '<i class="icon-calendar-plus-o"></i> More Fixtures' +
                                    '</a>'+
                                '</div> ';
                }
                next_fixtures = nxt_fixtures + nxt_btn;

            }
            else{
                var next_fixtures = '<tr class="warning" style="text-align: center;">' +
                                        '<td></td><td></td><td></td><td></td>' +
                                    '</tr>' +
                                '</table>' +
                            '</div>';
            }
        }

        else{
            var next_fixtures = '<tr class="warning"><td></td><td></td><td></td><td></td></tr></table></div>';

        }

        if (x >= 1) {
            allContent += table_top + thead + game + next_fixtures;
        }
        else {
            allContent += thead + game + next_fixtures;
        }
    }

    var bottom =        '</table>' +
                    '</div>' +
                '</div>';

    return top + allContent + bottom;

}


function rotateCard(btn, league, league_id){
    var $card = $(btn).closest('.card-container');
    if($card.hasClass('hover')){
        $card.removeClass('hover');
    } else {
        $card.addClass('hover');
    }

    load_league_table(league, league_id, false);
}

function showNext(fixture_id, btn_id, next_btn_id){
    $('#' + btn_id).hide();
    $('#' + next_btn_id).show();
    $('#' + fixture_id).show();
}

function load_league_table(league, league_id, load_modal, league_name) {
    $.ajax({
        type: 'POST',
        url: '/stats/fixtures-ajax',
        data: {
            league: league
        }
    })
        .done(function (response) {
            if (response.error) {
                $('#loading-' + league_id).hide();
                $('#errorAlert-' + league_id).show();

            }
            else {
                console.log(JSON.parse(response).error);

                if (!load_modal) {
                    // Load first fixtures into card
                    $('#loading-' + league_id).hide();
                    if (!JSON.parse(response).error) {
                        $('#' + league_id).append(create_fixtures_table(response, league_id, true));
                        $('#btn-activate-modal-' + league_id).show();
                    }
                    else {
                        $('#errorAlert-' + league_id).show();
                    }
                }
                else{
                    // Load data into modal
                    $('#fixtures-modal-content').empty();
                    $('#fixturesModalLabel').empty();

                    if (!response.error) {
                        $('#fixtures-modal-content').append(create_fixtures_table(response, league_id, false));
                        $('#fixturesModalLabel').html('<i class="icon-calendar" id="modalTitle"></i>' +
                            '<b>&nbsp;&nbsp;' + league_name + '</b>');
                    }
                    else {
                        $('#errorAlert-' + league_id).show();
                    }
                }

            }
        });
}
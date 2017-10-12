/**
 *
 * On page load, get livestreams match data from cached REST API
 *
 */
jQuery(document).ready(function($) {

    $.ajax({
        type: 'GET',
        url: '/livestreams-ajax'
    })
            .done(function (data) {
                $('#livestream_badge').text(data.size);
                $('#gmt_time_load').text(data.gmt_time);
                $('#globalWrapper').css('background-image', 'url(' + '/static/images/champions-wall.jpg' + ')');

                if (data.size == 0) {
                    $('#loading-gif').hide();
                    $('#streams_content').show();
                    console.log('No Streams');
                }
                else {
                    console.log(data);
                    $('#streams_body').append(build_stream_cards(data.list, data.size));
                    $('#streams_content').show();
                    $('#loading-gif').hide();
                    reload_time();
                }
            })
});


/**
 * Reloads the GMT time every minute
 */
function reload_time(){
    setInterval(function() {
        $.ajax({
                type: 'POST',
                url: '/gmt-ajax'
            })
                .done(function (data) {
                    console.log(data);
                    $('#gmt_time_load').empty();
                    $('#gmt_time_load').text(data.gmt_time);
                });
            }, 60000);
}


/**
 * Split array of keys into lists of size 3
 * @param keys_list
 * @returns list of key lists (size 3)
 */
function partion_array_in_rows(keys_list) {
    var groupSize = 3;
    var groups = [];

    while (keys_list.length > 0)
        groups.push(keys_list.splice(0, groupSize));

    return groups;
}


/**
 *  Build livestreams cards on page load
 *
 *  Live Stream card modal HTML template
     *  <div class="modal fade" id="stream_id" tabindex="-1" role="dialog" aria-labelledby="streamLabel_id" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header" style="padding: 15px 15px 5px 15px;">
                        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">×</span><span class="sr-only">Close</span></button>
                        <h5 class="modal-title" id="streamLabel_id"></h5>
                    </div>
                    <div class="modal-body" id="links_id" style="padding: 10px;"></div>
                    <div class="modal-footer" style="margin-top:0px;padding: 3px;">
                        <button type="button" class="btn btn-md" data-dismiss="modal" style="width: 100%;background-color:#22aba6;">
                            <i class="icon-close"></i> Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
 *  Live Stream card HTML template
     *  <div class="col-md-4">
            <div class="card card-signup">
                <div class="header header-success text-center">
                    <h4>Home Team vs Away Team</h4>
                </div>
                <div class="content" style="text-align: center;">
                    <span>League/Competition</span><br>
                    <span>Date</span><br>
                    <span>Started x minutes ago. / Starts in .. minutes.</span>
                </div>
                <div class="footer text-center" style="padding-top: 20px">
                    <button class="btn btn-success">Find them Streams</button>
                </div>
            </div>
        </div>
 */
function build_stream_cards(list, size) {
    var data = '';                                      // HTML created
    var jsonData = JSON.parse(list);                    // JSON content

    var keys = [];
    for (var k in jsonData) keys.push(k);               // get all the keys of JSON

    var grouped_keys = partion_array_in_rows(keys);             // Keys of each lists split into arrays of size 3
    var num_rows = Math.ceil(size / 3);

    for (var i=0; i < num_rows; i++) {                          // Iterate through each rows
        /* Build the rows HTML structure */
        if (i==0) {                                             // different padding for UI
            data += '<div class="row mobile-card-row" style="padding-top:30px;">\n';
        }
        else {
            data += '<div class="row mobile-card-row" style="padding-top:100px;">\n';
        }

        for (var x=0; x < 3; x++) {                             // create up to 3 stream cards per row
            /* Build the stream cards HTML structure */
            try {
                var game_badge = build_status_badge(jsonData[grouped_keys[i][x]][0]['status']);
                data += <!-- Stream Card modal -->
                        '<div class="modal fade" id="stream_' + jsonData[grouped_keys[i][x]][0]['submission_id'] + '" tabindex="-1" role="dialog" aria-labelledby="streamLabel_' + jsonData[grouped_keys[i][x]][0]['submission_id'] + '" aria-hidden="true">\n' +
                            '<div class="modal-dialog">\n' +
                                '<div class="modal-content">\n' +
                                    '<div class="modal-header" style="padding: 15px 15px 5px 15px;">\n' +
                                        '<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">×</span><span class="sr-only">Close</span></button>\n' +
                                        '<h5 class="modal-title" id="streamLabel_' + jsonData[grouped_keys[i][x]][0]['submission_id'] + '" style="text-align:center;">' + jsonData[grouped_keys[i][x]][0]['stream_name'] + '</h5>\n' +
                                        '<div style="text-align:center;"><span><a target="_blank" href="http://reddit.com/' + jsonData[grouped_keys[i][x]][0]['submission_id'] + '" >Reddit Post</a></span></div>' +
                                    '</div>\n' +
                                    '<div class="modal-body" id="links_' + jsonData[grouped_keys[i][x]][0]['submission_id'] + '" style="padding: 10px;"></div>\n' +
                                    '<div class="modal-footer" style="margin-top:0px;padding: 3px;">\n' +
                                        '<button type="button" class="btn btn-md" data-dismiss="modal" style="width: 100%;background-color:#22aba6;">\n' +
                                            '<i class="icon-close"></i> Close\n' +
                                        '</button>\n' +
                                    '</div>\n' +
                                '</div>\n' +
                            '</div>\n' +
                        '</div>\n' +

                        <!-- Stream card -->
                        '<div class="col-md-4 mobile-card-padding">\n' +
                            '<div class="card card-signup">\n' +
                                '<div class="header header-success text-center">\n' +
                                    '<strong style="margin-top:0px;margin-bottom:0px;">' + $.trim(jsonData[grouped_keys[i][x]][0]['stream_name'].replace('\.','').split('vs')[0]) + '</strong>\n' +  // [0] is to access the data in the nested list#
                                    '<br>\n' +
                                    '<span>vs</span>\n' +
                                    '<br>\n' +
                                    '<strong style="margin-top:0px;margin-bottom:0px;">' + $.trim(jsonData[grouped_keys[i][x]][0]['stream_name'].replace('\.','').split('vs')[1]) + '</strong>\n' +  // [0] is to access the data in the nested list#
                                '</div>\n' +
                                '<div class="content" style="text-align: center;padding-left:0px;padding-right:0px;">\n' +
                                    '<span>' + jsonData[grouped_keys[i][x]][0]['competition'] + '</span>' + '<br>\n' +
                                    '<span>' + jsonData[grouped_keys[i][x]][0]['stream_time'] + '</span>' + '<br>\n' +
                                    game_badge +
                                '</div>\n' +
                                '<div class="footer text-center" style="padding-top: 15px">\n' +
                                    '<button class="btn btn-success btn-sm" style="margin-bottom:20px;padding-top:8px;text-transform:uppercase;" data-toggle="modal" data-target="#stream_' + jsonData[grouped_keys[i][x]][0]['submission_id'] + '" ' +
                                        'onclick="find_stream_links(\'' + jsonData[grouped_keys[i][x]][0]['submission_id'] + '\')">' + "Find  Streams" +
                                    '</button>\n' +
                                '</div>\n' +
                            '</div>\n' +
                        '</div>\n';

            } catch(e){
                console.log('Type Error Caught: Card is empty');
            }
        }
        data += '</div>\n';
    }
    return data;
}


/**
 * Builds the status badge for each game
 * @param status - "Live", "Expired", "Not Started"
 * @returns HTML for each badge
 */
function build_status_badge(status){
    var badge_html = '';

    if (status == "Live"){
        badge_html += '<span class="label label-success">' + status + '</span>\n';
    }
    else if (status == "Expired" || status == "Likely Expired") {
        badge_html += '<span class="label label-danger">' + status + '</span>\n';
    }
    else if (status == "Not Started"){
        badge_html += '<span class="label label-warning">' + status + '</span>\n';
    }

    return badge_html;
}


/**
 * Open stream modal with it's links
 */
function find_stream_links(post_id) {
    if ($('#links_' + post_id).children().length > 0) {
        console.log('Modal content has already made!');
    }
    else {
        $.ajax({
            type: 'POST',
            url: '/livestreams/link',
            data: {
                post_id: post_id
            }
        })
            .done(function (data) {
                if (data.error) {
                    console.log('ERROR');
                }
                else {
                    $('#links_' + post_id).append(build_modals_ui(data.links));     // build the links table
                }
            })
    }
}


/**
 * create the modal table of stream links
 * @param links - JSON string with stream links
 */
function build_modals_ui(links){
    var links_table = '';
    var jsonData = JSON.parse(links);

    links_table += '<div class="row" style="padding-left:20px;padding-right:20px;">' +
                        '<table class="table table-striped">' +
                            '<thead>' +
                                '<tr>' +
                                    '<th class="text-center" style="width:30%;">Upvotes</th>' +
                                    '<th style="width:70%;">Stream Links</th>' +
                                '</tr>' +
                            '</thead>' +
                            '<tbody>';

    for (var key in jsonData) {
        if (jsonData.hasOwnProperty(key)) {
            links_table +=      '<tr>' +
                                    '<td class="text-center">' +
                                        '<i class="icon-arrow-up"></i>' + jsonData[key][0].upvotes +
                                    '</td>' +
                                    '<td>' +
                                        '<a target="_blank" href="' + jsonData[key][0].stream_link + '">' + jsonData[key][0].stream_title +
                                    '</td>' +
                                '</tr>';
        }
    }

    links_table +=          '</tbody>' +
                        '</table>' +
                    '</div>';

    return links_table;
}

jQuery(document).ready(function($) {
    /**
     * AJAX request to load bootstrap table with match highlights content
     */

    $.ajax({
		type: 'POST',
		url: '/highlights-ajax'
	})
        .done(function (data) {
			if (data.error) {
				$('#loading-gif').hide();
				$('#errorAlert').show();
			}
			else {
			    console.log(data);
                $('#highlights-ajax-load').append(prettify_table(data.list));
                initialize_table();
                $('#content').show();

                /**
                 *  Code runs only if on a desktop:
                 *      - Load social links: ProductHunt, Github
                 *      - Loads background image
                */
                if ($(window).width() > 768) {
                    $('#globalWrapper').css('background-image', 'url(' + '/static/images/champions-wall.jpg' + ')');
                    $('#load-social-links').html('<iframe class="" style="position: absolute;right: 0;margin-left: 5px;margin-top:10px;" src="https://ghbtns.com/github-btn.html?user=jctissier&repo=Euro2016_TerminalApp&type=star&count=true" frameborder="0" scrolling="0" width="110px" height="30px" allowtransparency="true"></iframe>' +
                    '<iframe class="" style="padding-top:10px;position: absolute;right:0;margin-top:30px;" src="https://yvoschaap.com/producthunt/counter.html#href=https%3A%2F%2Fwww.producthunt.com%2Fr%2F8729ce4250f30f%2F67210&layout=wide" width="110" height="65" scrolling="no" frameborder="0" allowtransparency="true"></iframe>');
                }
                $('#loading-gif').hide();
            }
        });
});


/**
 *
 * Helper Functions
 *
*/


/**
 * Redirects the button click to the links page & passes parameters
 */
function click_link(btn_id, title, competition, date){
    window.open("/link" + "?post_id=" + btn_id + "&title=" + title + "&comp=" + competition + "&date=" + date, '_blank');
}


/**
 * Opens new tab to specific Reddit post
 */
function open_reddit_post(href){
    window.open(href, '_blank');
}


/**
 * Inserts formatted highlights content into the bootstrap table
 * @returns HTML content of the table
 */
function prettify_table(list) {
	var data = '';
    var jsonData = JSON.parse(list);                    // JSON content

    for (var key in jsonData) {
        if (jsonData.hasOwnProperty(key)) {

            data += '<tr>' +
                        '<td>' +
                                 '<div style="text-align: center;">' +
                                    '<button type="button" class="btn btn-medseagreen btn-xs" style="line-height: 1.7;padding-top: 2px;width: 32px;height: 25.5px;color: #3cb371;" ' +
                                    'onclick="click_link(\'' + jsonData[key][0].submission_id + '\',\'' + jsonData[key][0].highlight_name[0] + '  vs  '
                                    + jsonData[key][0].highlight_name[1] + '\',\'' + jsonData[key][0].highlight_league + '\',\'' + jsonData[key][0].game_date + '\')">' +
                                    '<b><i class="icon-play" style="padding-left: 2px;"></i></b>' +
                                    '</button>' +
                                '</div> ' +
                        '</td>' +
                        '<td><p style=\"text-align: right;color: blue;font-size: 14px;margin-bottom: 0px;\">' + jsonData[key][0].highlight_name[0] + '</p></td>' +
                        '<td><p style=\"text-align: center;color: #22aba6;font-size: 14px;margin-bottom: 0px;\" onclick="open_reddit_post(\'http://reddit.com/' + jsonData[key][0].submission_id + '\')">' +
                            '&nbsp;&nbsp;&nbsp;&nbsp;vs&nbsp;&nbsp;&nbsp;&nbsp;</p></td>' +
                        '<td><p style=\"text-align: left;color: red;font-size: 14px;margin-bottom: 0px;\">' + jsonData[key][0].highlight_name[1] + '</p></td>' +
                        '<td>' + jsonData[key][0].highlight_league + '</td>' +
                        '<td><b>' + jsonData[key][0].game_date + '</b></td>' +
                    '</tr>';
        }
    }

    return data;
}


/**
 * Initialize Bootstrap table
 */
function initialize_table() {
    var $table = $('#fresh-table');

    $().ready(function(){
        $table.bootstrapTable({
            toolbar: ".toolbar",

            search: true,
            // showToggle: true,                // remove other mode
            striped: true,
            pagination: true,
            pageSize: 17,

            // icons: {
            //     toggle: 'icon-th-list',
            // }
        });

        $(window).resize(function () {
            $table.bootstrapTable('resetView');
        });

    });

}
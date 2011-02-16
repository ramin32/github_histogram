$(document).ready(function(){
    function set_username() {
        url = '/weekly_commits/' + $('#username_field').val();
        window.location = url;
    }

    $('#username_field').keyup(function(e) {
        if(e.keyCode == 13) {
            set_username();
        }
    });

    $('#update_button').click(function() {
        if(!$('#username_field').val()){
            alert('Username may not be empty.');
        }
        else {
            set_username();
        }
    });

});

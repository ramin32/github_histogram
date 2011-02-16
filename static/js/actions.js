$(document).ready(function(){
    $('#update_button').click(function() {
        if(!$('#username_field').val())
            alert('Username may not be empty.');
        else 
        {
            var url = '/weekly_commits/' + $('#username_field').val();
            window.location = url;
        }
    });
    
});

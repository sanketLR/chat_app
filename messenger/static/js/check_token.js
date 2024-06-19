function checkToken() {
    if (localStorage.getItem('accessToken') == null) {

        window.location = "http://127.0.0.1:8000/api/messenger/signIn/";

    }
}
checkToken();

$(document).ready(function () {

    const accessToken = localStorage.getItem("accessToken");

    $.ajax({
        url: 'http://127.0.0.1:8000/api/messenger/CheckToken/',
        type: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        },
        dataType: 'json',
        success: function (data) {
            if (data.code === 200) {
                console.log("response 200");
            } else {
                window.location.href = "http://127.0.0.1:8000/api/messenger/signIn/";
            }

            if (data.code === 400) {
                console.log("400 come");
            }
        },
        error: function (error) {
            console.error('Error:', error.message);
            window.location.href = "http://127.0.0.1:8000/api/messenger/signIn/";

        }
    });

});
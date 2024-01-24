function checkToken(){
    if ( localStorage.getItem('accessToken') == null) {
       
        window.location = "http://127.0.0.1:8000/api/messenger/signIn/";
        
    }
}
checkToken();
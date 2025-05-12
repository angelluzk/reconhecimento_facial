document.addEventListener("DOMContentLoaded", () => {
    const usuarioEmail = getCookie("usuario_email");
    if (usuarioEmail) {
        window.location.href = "/dashboard";
    }
});

function getCookie(name) {
    let cookieArr = document.cookie.split(";");
    for (let i = 0; i < cookieArr.length; i++) {
        let cookie = cookieArr[i].trim();
        if (cookie.startsWith(name + "=")) {
            return cookie.substring(name.length + 1);
        }
    }
    return "";
}
// Redirect to requested path
var link = document.createElement('a');
try {
    var share_path = window.location.hash.substring(1);
    if (share_path.charAt(0) != '/') share_path = '/' + share_path;
    link.href = share_path;
} catch(e) {
    link.href = '/';
}
window.location = link;

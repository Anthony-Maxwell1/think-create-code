// Included by templates/artwork/render.html
function inIframe () {
    try {
        return window.self !== window.top;
    } catch (e) {
        console.warn(e);
        return true;
    }
}

docReady(function() {
    // If this page was loaded in an iframe, it's ok to run the processingjs code
    if (inIframe()) {

        // Show the rendered div
        var safe = document.getElementById('artwork-rendered');
        safe.style.display = "block";

        // Set the script contents                
        var script = document.getElementById('script-preview');
        script.innerHTML = scriptCode; // defined by including page

        // Run processingJS
        Processing.reload();
    }
    // Otherwise, just show the code, and a warning message.
    else {
        // Show the inlined code and warning message
        var unsafe = document.getElementById('artwork-not-rendered');
        unsafe.style.display = "block";
    }
});


// time of of the last AJAX request; controls whether a warm-up ping will be sent when
// putting the focus to the search input or not
var lastCallTs = 0;

// invokes a "ping" URI at the backend, potentially waking up the Lambda and thus avoiding
// a cold start upon the actual search request
function warmUp(x) {
    var now = new Date().getTime();

    if (now - lastCallTs > 14 * 60 * 1000) {
        const XHR = new XMLHttpRequest();
        XHR.open( "GET", searchUrl + "ping");
        XHR.setRequestHeader( 'X-API-Key', apiKey );
        XHR.send();

        lastCallTs = now;
    }
}

// executes the query
function sendData(FD) {
    if (FD.get('q').replace(/\s/g, "").length == 0) {
        return;
    }

    const XHR = new XMLHttpRequest();

    var parameters = [];
    for (var pair of FD.entries()) {
        parameters.push(encodeURIComponent(pair[0]) + '=' + encodeURIComponent(pair[1]));
    }

    XHR.addEventListener( "load", function(event) {
        document.getElementById( "inputSearch" ).disabled = false;
        document.getElementById( "buttonSubmitSearch" ).disabled = false;
        document.getElementById( "iconSearch" ).classList="fa fa-search";
        document.getElementById( "inputSearchMobile" ).disabled = false;
        document.getElementById( "buttonSubmitSearchMobile" ).disabled = false;
        document.getElementById( "iconSearchMobile" ).classList="fa fa-search";

        if (event.target.status != 200) {
            var results = '<div class="search-results"><h1 class="title">Uh oh</h1>';
            results += "<p>A technical error occurred; Please try again later.";
            results += "</div>";

            document.getElementById( "main-content" ).innerHTML = results;
        }
        else {
            var jsonResponse = JSON.parse(event.target.responseText);
            var results = '<div class="search-results"><h1 class="title">Search Results</h1>';

            if (jsonResponse["results"].length > 0) {
                for (var result of jsonResponse["results"]) {
                    results +=
                        '<div class="post">' +
                            '<div class="meta">' +
                                result["publicationdate"] +
                            "</div>" +
                            '<h4 class="summary"><a href="' + result["uri"] + '">' + result["title"] + "</a></h4>" +
                            '<div><span class="description">' +
                                result["fragment"] +
                            "</span></div>" +
                        "</div>";
                }
            }
            else {
                results += '<div class="post">No results found</div>';
            }

            // window.history.pushState("", "", "/search/");

            results += "</div>";
        }

        document.getElementById( "main-content" ).innerHTML = results;
    });

    XHR.addEventListener( "error", function( event ) {
        document.getElementById( "inputSearch" ).disabled = false;
        document.getElementById( "buttonSubmitSearch" ).disabled = false;
        document.getElementById( "iconSearch" ).classList="fa fa-search";
        document.getElementById( "inputSearchMobile" ).disabled = false;
        document.getElementById( "buttonSubmitSearchMobile" ).disabled = false;
        document.getElementById( "iconSearchMobile" ).classList="fa fa-search";

        var results = '<div class="search-results"><h1 class="title">Uh oh</h1>';
        results += "<p>A technical error occurred; Please try again later.";
        results += "</div>";

        document.getElementById( "main-content" ).innerHTML = results;

        console.log('Request failed:' + event);
    });

    XHR.open( "GET", searchUrl + "search?" + parameters.join('&'));
    XHR.setRequestHeader( 'X-API-Key', apiKey );
    XHR.send();

    document.getElementById( "inputSearch" ).disabled = true;
    document.getElementById( "buttonSubmitSearch" ).disabled = true;
    document.getElementById( "iconSearch" ).classList="fa fa-spinner";
    document.getElementById( "inputSearchMobile" ).disabled = true;
    document.getElementById( "buttonSubmitSearchMobile" ).disabled = true;
    document.getElementById( "iconSearchMobile" ).classList="fa fa-spinner";

    lastCallTs = new Date().getTime();
}

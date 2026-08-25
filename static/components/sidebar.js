$(function() {
    $("#sidebar-placeholder").load("/static/components/sidebar.html", function() {
        const path = window.location.pathname;
        let activeId = "nav-dashboard";
        
        if (path.includes("/insight")) activeId = "nav-insight";
        else if (path.includes("/forecast")) activeId = "nav-forecast";
        else if (path.includes("/chat")) activeId = "nav-chat";
        
        $(`#${activeId}`).addClass("active");
    });
});
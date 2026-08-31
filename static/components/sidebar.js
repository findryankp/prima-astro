$(function() {
    $("#sidebar-placeholder").load("/static/components/sidebar.html", function() {
        const path = window.location.pathname;
        let activeId = "nav-dashboard";
        
        if (path.includes("/insight")) activeId = "nav-insight";
        else if (path.includes("/forecast")) activeId = "nav-forecast";
        else if (path.includes("/chat")) activeId = "nav-chat";
        
        $(`#${activeId}`).addClass("active");

        // Populate user data from Auth session
        if (typeof Auth !== "undefined") {
            const user = Auth.getUser();
            if (user) {
                if (user.name) $("#sidebar-user-name").text(user.name);
                if (user.role) $("#sidebar-user-role").text(user.role);
                if (user.avatar) $("#sidebar-user-avatar").text(user.avatar);
            }
        }
    });
});
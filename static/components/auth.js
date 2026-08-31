/**
 * Prima Astro - Authentication Handler
 * Credentials: User: admin | Pass: admin
 */

const AUTH_STORAGE_KEY = "astro_auth_session";

const Auth = {
    isAuthenticated: function() {
        try {
            const session = localStorage.getItem(AUTH_STORAGE_KEY);
            if (!session) return false;
            const parsed = JSON.parse(session);
            return parsed && parsed.isLoggedIn === true;
        } catch (e) {
            return false;
        }
    },

    getUser: function() {
        try {
            const session = localStorage.getItem(AUTH_STORAGE_KEY);
            if (!session) return null;
            return JSON.parse(session);
        } catch (e) {
            return null;
        }
    },

    login: function(username, password) {
        if (username === "admin" && password === "admin") {
            const sessionData = {
                isLoggedIn: true,
                username: "admin",
                name: "Administrator",
                role: "Sparepart Manager",
                avatar: "👨‍💼",
                loginTime: new Date().toISOString()
            };
            localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(sessionData));
            return { success: true };
        } else {
            return { 
                success: false, 
                message: "Username atau Password salah! (Gunakan: admin / admin)" 
            };
        }
    },

    logout: function() {
        localStorage.removeItem(AUTH_STORAGE_KEY);
        window.location.href = "/login";
    },

    protectPage: function() {
        const isLoginPage = window.location.pathname.includes("/login");
        const authenticated = this.isAuthenticated();

        if (!authenticated && !isLoginPage) {
            window.location.href = "/login";
        } else if (authenticated && isLoginPage) {
            window.location.href = "/";
        }
    }
};

// Auto-run protection check on script execution
Auth.protectPage();

import { createRouter, createWebHistory } from 'vue-router'
import LoginScreen from '../views/LoginScreen.vue'
import RegisterScreen from '../views/RegisterScreen.vue'
import BookingScreen from '../views/BookingScreen.vue'
import HistoryScreen from '../views/HistoryScreen.vue'
import MechanicDashboard from '../views/MechanicDashboard.vue'
import GarageListScreen from '../views/GarageListScreen.vue'
import AppointmentScreen from '../views/AppointmentScreen.vue'
import ProfileScreen from '../views/ProfileScreen.vue'
import PersonalInfoScreen from '../views/PersonalInfoScreen.vue'
import SettingsScreen from '../views/SettingsScreen.vue'
import TermsScreen from '../views/TermsScreen.vue'
import PrivacyScreen from '../views/PrivacyScreen.vue'
import MechanicProfileScreen from '../views/MechanicProfileScreen.vue'

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginScreen },
    { path: '/booking', component: BookingScreen },
    { path: '/register', component: RegisterScreen },
    { path: '/history', component: HistoryScreen },
    { path: '/mechanic', component: MechanicDashboard },
    { path: '/garages', component: GarageListScreen },
    { path: '/appointment', component: AppointmentScreen },
    { path: '/profile', component: ProfileScreen },
    { path: '/profile/info', component: PersonalInfoScreen },
    { path: '/settings', component: SettingsScreen },
    { path: '/terms', component: TermsScreen },
    { path: '/privacy', component: PrivacyScreen },
    { path: '/mechanic/profile', component: MechanicProfileScreen },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Route Guards
router.beforeEach((to, from, next) => {
    const userStr = localStorage.getItem('user');
    let isAuthenticated = false;
    let isMechanic = false;

    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            isAuthenticated = !!user.username;
            isMechanic = user.is_mechanic;
        } catch (e) { }
    }

    const publicPages = ['/login', '/register'];
    const authRequired = !publicPages.includes(to.path);

    // Redirect to login if auth is required but not logged in
    if (authRequired && !isAuthenticated) {
        return next('/login');
    }

    // Redirect away from login/register if already logged in
    if (!authRequired && isAuthenticated) {
        return next('/booking'); // Default authenticated route
    }

    // Protect mechanic dashboard
    if (to.path === '/mechanic' && !isMechanic) {
        return next('/booking'); // Redirect back to customer view
    }

    next();
});

export default router

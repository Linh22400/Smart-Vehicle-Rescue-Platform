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
import MechanicServicesScreen from '../views/MechanicServicesScreen.vue'
import OfflineScreen from '../views/OfflineScreen.vue'

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
    { path: '/mechanic/services', component: MechanicServicesScreen },
    { path: '/offline', component: OfflineScreen },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Bảo vệ route — kiểm tra đăng nhập và phân quyền trước mỗi điều hướng
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

    const publicPages = ['/login', '/register', '/offline'];
    const authRequired = !publicPages.includes(to.path);

    // Chuyển về login nếu chưa đăng nhập nhưng route yêu cầu auth
    if (authRequired && !isAuthenticated) {
        return next('/login');
    }

    // Đã đăng nhập thì không cho vào trang login/register (nhưng cho phép vào /offline)
    if (!authRequired && isAuthenticated && to.path !== '/offline') {
        return next('/booking'); // Route mặc định sau khi đăng nhập
    }

    // Bảo vệ tất cả route thợ — chỉ tài khoản is_mechanic mới vào được
    if (to.path.startsWith('/mechanic') && !isMechanic) {
        return next('/booking'); // Khách hàng bị chuyển về màn hình đặt xe
    }

    next();
});

export default router

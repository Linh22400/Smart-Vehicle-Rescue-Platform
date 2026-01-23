import { createRouter, createWebHistory } from 'vue-router'
import LoginScreen from '../views/LoginScreen.vue'
import RegisterScreen from '../views/RegisterScreen.vue'
import BookingScreen from '../views/BookingScreen.vue'
import HistoryScreen from '../views/HistoryScreen.vue'
import MechanicDashboard from '../views/MechanicDashboard.vue'
import GarageListScreen from '../views/GarageListScreen.vue'
import AppointmentScreen from '../views/AppointmentScreen.vue'

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginScreen },
    { path: '/booking', component: BookingScreen },
    { path: '/register', component: RegisterScreen },
    { path: '/history', component: HistoryScreen },
    { path: '/mechanic', component: MechanicDashboard },
    { path: '/garages', component: GarageListScreen },
    { path: '/appointment', component: AppointmentScreen }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Catalog from '@/views/Catalog.vue'
import SupplierDetail from '@/views/SupplierDetail.vue'
import Register from '@/views/Register.vue'
import Login from '@/views/Login.vue'
import Favorites from '@/views/Favorites.vue'
import Cart from '@/views/Cart.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'Home', component: Home },
    { path: '/catalog', name: 'Catalog', component: Catalog },
    { path: '/suppliers/:id', name: 'SupplierDetail', component: SupplierDetail },
    { path: '/register', name: 'Register', component: Register },
    { path: '/login', name: 'Login', component: Login },
    { path: '/favorites', name: 'Favorites', component: Favorites },
    { path: '/cart', name: 'Cart', component: Cart },
  ],
})

export default router
import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Catalog from '@/views/Catalog.vue'
import SupplierDetail from '@/views/SupplierDetail.vue'
import Register from '@/views/Register.vue'
import Login from '@/views/Login.vue'
import Favorites from '@/views/Favorites.vue'
import Cart from '@/views/Cart.vue'
import Profile from '@/views/Profile.vue'
import Features from '@/views/Features.vue'
import Reviews from '@/views/Reviews.vue'
import MyProducts from '@/views/MyProducts.vue'
import MyOrders from '@/views/MyOrders.vue'
import SupplierOrders from '@/views/SupplierOrders.vue'
import { useAuthStore } from '@/data/authStore'

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
    { path: '/profile', name: 'Profile', component: Profile },
    { path: '/features', name: 'Features', component: Features },
    { path: '/reviews', name: 'Reviews', component: Reviews },
    {
      path: '/my-products',
      name: 'MyProducts',
      component: MyProducts,
      meta: { requiresRole: 'SUPPLIER' }
    },
    {
      path: '/my-orders',
      name: 'MyOrders',
      component: MyOrders,
      meta: { requiresRole: 'BUYER' }
    },
    {
      path: '/supplier-orders',
      name: 'SupplierOrders',
      component: SupplierOrders,
      meta: { requiresRole: 'SUPPLIER' }
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresRole) {
    if (!authStore.token) {
      return '/login'
    }
    if (authStore.user?.role !== to.meta.requiresRole) {
      return '/'
    }
  }
})

export default router

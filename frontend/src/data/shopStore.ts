import { reactive } from 'vue'
import type { Product } from './mockProducts'
import type { Supplier } from './mockSuppliers'

type CartItem = {
  product: Product
  quantityKg: number
}

const state = reactive({
  favoriteProducts: [] as Product[],
  favoriteSuppliers: [] as Supplier[],
  cartItems: [] as CartItem[],
})

export function useShopStore() {
  const toggleFavoriteProduct = (product: Product) => {
    const index = state.favoriteProducts.findIndex((p) => p.id === product.id)
    if (index >= 0) {
      state.favoriteProducts.splice(index, 1)
    } else {
      state.favoriteProducts.push(product)
    }
  }

  const toggleFavoriteSupplier = (supplier: Supplier) => {
    const index = state.favoriteSuppliers.findIndex((s) => s.id === supplier.id)
    if (index >= 0) {
      state.favoriteSuppliers.splice(index, 1)
    } else {
      state.favoriteSuppliers.push(supplier)
    }
  }

  const isProductFavorite = (productId: number) =>
    state.favoriteProducts.some((p) => p.id === productId)

  const isSupplierFavorite = (supplierId: number) =>
    state.favoriteSuppliers.some((s) => s.id === supplierId)

  const addToCart = (product: Product, quantityKg: number) => {
    if (quantityKg <= 0) return
    const existing = state.cartItems.find((item) => item.product.id === product.id)
    if (existing) {
      existing.quantityKg += quantityKg
    } else {
      state.cartItems.push({ product, quantityKg })
    }
  }

  const setCartQuantity = (productId: number, quantityKg: number) => {
    const item = state.cartItems.find((i) => i.product.id === productId)
    if (!item) return
    if (quantityKg <= 0) {
      state.cartItems = state.cartItems.filter((i) => i.product.id !== productId)
    } else {
      item.quantityKg = quantityKg
    }
  }

  const removeFromCart = (productId: number) => {
    state.cartItems = state.cartItems.filter((i) => i.product.id !== productId)
  }

  return {
    state,
    toggleFavoriteProduct,
    toggleFavoriteSupplier,
    isProductFavorite,
    isSupplierFavorite,
    addToCart,
    setCartQuantity,
    removeFromCart,
  }
}


<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'

type ChatListItem = {
  id: number
  user1_id: number
  user2_id: number
  created_at: string
  user1?: { id: number; email: string } | null
  user2?: { id: number; email: string } | null
  last_message?: { content: string; created_at: string } | null
}

type MessageItem = {
  id: number
  sender_id: number
  content: string
  created_at: string
  sender?: { id: number; email: string } | null
}

type ChatItem = {
  id: number
  messages: MessageItem[]
  user1_id: number
  user2_id: number
  user1?: { id: number; email: string } | null
  user2?: { id: number; email: string } | null
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const chats = ref<ChatListItem[]>([])
const activeChat = ref<ChatItem | null>(null)
const messageText = ref('')
const loading = ref(false)
const loadingChat = ref(false)
const sending = ref(false)
const error = ref('')

const me = computed(() => authStore.user?.id ?? null)

const otherUser = (chat: ChatListItem | ChatItem) => {
  if (!me.value) return null
  const candidate = chat.user1_id === me.value ? chat.user2 : chat.user1
  return candidate ?? null
}

const loadChats = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await api.get('/chats')
    chats.value = response.data || []

    const firstChat = chats.value[0]
    if (!activeChat.value && firstChat) {
      await openChat(firstChat.id)
    }
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Не удалось загрузить список чатов'
  } finally {
    loading.value = false
  }
}

const openChat = async (chatId: number) => {
  loadingChat.value = true
  error.value = ''

  try {
    const response = await api.get(`/chats/${chatId}`)
    activeChat.value = response.data
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Не удалось открыть чат'
  } finally {
    loadingChat.value = false
  }
}

const sendMessage = async () => {
  if (!activeChat.value || !messageText.value.trim() || sending.value) return
  sending.value = true
  error.value = ''

  try {
    await api.post(`/chats/${activeChat.value.id}/messages`, { content: messageText.value.trim() })
    messageText.value = ''
    await openChat(activeChat.value.id)
    await loadChats()
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Не удалось отправить сообщение'
  } finally {
    sending.value = false
  }
}

const createChat = async (userId: number) => {
  if (!userId) return

  try {
    const response = await api.post('/chats', { user2_id: userId })
    await loadChats()
    await openChat(response.data.id)
    router.replace({ query: {} })
  } catch (err: any) {
    if (err.response?.status === 409 || err.response?.data?.detail?.includes('exists') || err.response?.data?.detail?.includes('существует')) {
      await loadChats()
      const existingChat = chats.value.find(c => c.user1_id === userId || c.user2_id === userId)
      if (existingChat) {
        await openChat(existingChat.id)
      }
      router.replace({ query: {} })
    } else {
      error.value = err?.response?.data?.detail || 'Не удалось создать чат'
    }
  }
}

const formatDate = (value: string) =>
  new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  await loadChats()

  if (route.query.userId) {
    const userId = Number(route.query.userId)
    if (userId) {
      const existingChat = chats.value.find(c => c.user1_id === userId || c.user2_id === userId)
      if (existingChat) {
        await openChat(existingChat.id)
        router.replace({ query: {} })
      } else {
        await createChat(userId)
      }
    }
  }
})
</script>

<template>
  <main class="chat-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Чат</p>
        <h1>Диалоги с контрагентами</h1>
        <p class="hero-lead">Выберите чат из списка или перейдите в чат со страницы поставщика.</p>
      </div>
    </section>

    <div v-if="error" class="error-box">{{ error }}</div>

    <div class="chat-layout">
      <aside class="sidebar">
        <h2>Чаты</h2>
        <div v-if="loading" class="state-box">Загрузка...</div>
        <button
          v-for="chat in chats"
          :key="chat.id"
          class="chat-item"
          :class="{ active: activeChat?.id === chat.id }"
          @click="openChat(chat.id)"
        >
          <strong>{{ otherUser(chat)?.email || `Чат #${chat.id}` }}</strong>
          <span>{{ chat.last_message?.content || 'Нет сообщений' }}</span>
        </button>
      </aside>

      <section class="conversation">
        <div v-if="loadingChat" class="state-box">Открываем чат...</div>
        <div v-else-if="!activeChat" class="state-box">Выберите чат слева.</div>
        <template v-else>
          <header class="conversation-head">
            <div>
              <h2>{{ otherUser(activeChat)?.email || `Чат #${activeChat.id}` }}</h2>
              <p>{{ activeChat.messages.length }} сообщений</p>
            </div>
          </header>

          <div class="messages">
            <article
              v-for="message in activeChat.messages"
              :key="message.id"
              class="message"
              :class="{ 'message--own': message.sender_id === me }"
            >
              <div class="message-head">
                <strong>{{ message.sender?.email || `Пользователь #${message.sender_id}` }}</strong>
                <time>{{ formatDate(message.created_at) }}</time>
              </div>
              <p>{{ message.content }}</p>
            </article>
          </div>

          <div class="composer">
            <textarea v-model="messageText" rows="3" placeholder="Введите сообщение"></textarea>
            <button class="primary-btn" :disabled="sending" @click="sendMessage">
              {{ sending ? 'Отправка...' : 'Отправить' }}
            </button>
          </div>
        </template>
      </section>
    </div>
  </main>
</template>

<style scoped>
.chat-page {
  display: grid;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  color: var(--sl-ink);
}

/* ===== ШАПКА ===== */
.hero {
  padding: clamp(1.25rem, 3vw, 2rem);
  border-bottom: 1px solid var(--sl-line);
}

.eyebrow {
  margin: 0 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.hero h1 {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

.hero-lead {
  margin: 0.75rem 0 0;
  max-width: 60ch;
  color: var(--sl-muted);
}

.error-box {
  margin: 1rem clamp(1.25rem, 3vw, 2rem) 0;
  padding: 0.9rem 1rem;
  color: #b3261e;
  background: #fbeaea;
  border: 1px solid rgba(179, 38, 30, 0.3);
  font-weight: 600;
}

/* ===== РАСКЛАДКА ===== */
.chat-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  margin: clamp(1.25rem, 3vw, 2rem);
  gap: 1px;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

/* ===== СПИСОК ЧАТОВ ===== */
.sidebar {
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #fff;
}

.sidebar h2 {
  margin: 0;
  padding: 1rem 1.25rem;
  font-family: inherit;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-muted);
  border-bottom: 1px solid var(--sl-line);
}

.chat-item {
  position: relative;
  display: grid;
  gap: 0.25rem;
  width: 100%;
  min-width: 0;
  text-align: left;
  padding: 0.9rem 1.25rem;
  border: none;
  border-bottom: 1px solid var(--sl-line);
  border-radius: 0;
  background: #fff;
  color: var(--sl-ink);
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.chat-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--sl-leaf);
  transform: scaleY(0);
  transition: transform 0.2s ease;
}

.chat-item:hover {
  background: var(--sl-paper);
}

.chat-item:hover::before {
  transform: scaleY(1);
}

.chat-item strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--sl-muted);
  font-size: 0.85rem;
}

.chat-item.active,
.chat-item.active:hover {
  background: var(--sl-ink);
  color: #fff;
}

.chat-item.active::before {
  transform: scaleY(1);
  background: var(--sl-lime);
}

.chat-item.active span {
  color: rgba(255, 255, 255, 0.7);
}

.chat-item:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: -2px;
}

/* ===== ДИАЛОГ ===== */
.conversation {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 320px;
  background: #fff;
}

.conversation-head {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.conversation-head h2 {
  margin: 0;
  font-size: 1.05rem;
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

.conversation-head p {
  margin: 0.3rem 0 0;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 520px;
  overflow: auto;
  padding: 1.25rem;
  background: var(--sl-paper);
}

.message {
  align-self: flex-start;
  max-width: min(78%, 560px);
  padding: 0.75rem 0.95rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  color: var(--sl-ink);
}

.message--own {
  align-self: flex-end;
  background: var(--sl-ink);
  border-color: var(--sl-ink);
  color: #fff;
}

.message-head {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.25rem 1rem;
  margin-bottom: 0.35rem;
  font-size: 0.78rem;
  color: var(--sl-muted);
}

.message-head strong {
  overflow-wrap: anywhere;
}

.message--own .message-head {
  color: var(--sl-lime);
}

.message p {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.composer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: stretch;
  border-top: 1px solid var(--sl-line);
}

.composer textarea {
  width: 100%;
  min-width: 0;
  resize: vertical;
  border: none;
  border-radius: 0;
  padding: 0.9rem 1.25rem;
  background: #fff;
}

.primary-btn {
  border: 1px solid var(--sl-ink);
  border-radius: 0;
  padding: 0.7rem 1.4rem;
  background: var(--sl-ink);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.primary-btn:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.primary-btn:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

.primary-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.state-box {
  padding: 1rem 1.25rem;
  color: var(--sl-muted);
}

.conversation > .state-box {
  flex: 1;
  display: grid;
  place-items: center;
  text-align: center;
  background: var(--sl-paper);
}

@media (max-width: 900px) {
  .chat-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .sidebar {
    max-height: 260px;
    overflow: auto;
  }
}

@media (max-width: 520px) {
  .chat-layout {
    margin: 1rem;
  }

  .message {
    max-width: 90%;
  }

  .composer {
    grid-template-columns: minmax(0, 1fr);
  }

  .composer textarea {
    border-bottom: 1px solid var(--sl-line);
  }

  .composer .primary-btn {
    width: 100%;
  }
}
</style>

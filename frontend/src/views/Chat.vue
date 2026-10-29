<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import { AppAvatar, AppButton, AppIcon, EmptyState, ErrorState, LoadingState, PageHeader } from '@/components/ui'
import { formatDate, pluralize } from '@/utils/format'

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

/* ── UI-состояние ──────────────────────────────── */
/** На узких экранах видна одна панель: список или диалог */
const showConversation = ref(false)
const initialLoaded = ref(false)
const chatQuery = ref('')
const messagesRef = ref<HTMLElement | null>(null)

const chatTitle = (chat: ChatListItem | ChatItem) => otherUser(chat)?.email || `Чат #${chat.id}`

const filteredChats = computed(() => {
  const q = chatQuery.value.trim().toLowerCase()
  if (!q) return chats.value
  return chats.value.filter((chat) =>
    [chatTitle(chat), chat.last_message?.content].some((v) => (v ?? '').toLowerCase().includes(q)),
  )
})

const dayKey = (value: string) => {
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? '' : d.toDateString()
}

const dayLabel = (value: string) => {
  const key = dayKey(value)
  if (!key) return '—'
  const today = new Date()
  const yesterday = new Date()
  yesterday.setDate(today.getDate() - 1)
  if (key === today.toDateString()) return 'Сегодня'
  if (key === yesterday.toDateString()) return 'Вчера'
  return formatDate(value, 'long')
}

/** Время в списке диалогов: сегодня — часы, иначе дата */
const listTime = (value: string | undefined) => {
  if (!value) return ''
  return dayKey(value) === new Date().toDateString() ? formatDate(value, 'time', '') : formatDate(value, 'short', '')
}

const messageGroups = computed(() => {
  const groups: { key: string; label: string; date: string; messages: MessageItem[] }[] = []
  for (const message of activeChat.value?.messages ?? []) {
    const key = dayKey(message.created_at)
    const last = groups[groups.length - 1]
    if (last && last.key === key) {
      last.messages.push(message)
    } else {
      groups.push({ key, label: dayLabel(message.created_at), date: message.created_at, messages: [message] })
    }
  }
  return groups
})

const messageCount = computed(() => activeChat.value?.messages.length ?? 0)

const selectChat = (chatId: number) => {
  showConversation.value = true
  if (activeChat.value?.id !== chatId) openChat(chatId)
}

const backToList = () => {
  showConversation.value = false
}

const onComposerKeydown = (event: KeyboardEvent) => {
  if (event.key !== 'Enter' || event.shiftKey || event.isComposing) return
  event.preventDefault()
  sendMessage()
}

const scrollToBottom = async () => {
  await nextTick()
  const el = messagesRef.value
  if (el) el.scrollTop = el.scrollHeight
}

watch(
  () => [activeChat.value?.id, messageCount.value],
  () => scrollToBottom(),
)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  await loadChats()
  initialLoaded.value = true

  if (route.query.userId) {
    const userId = Number(route.query.userId)
    if (userId) {
      showConversation.value = true
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
  <div class="chat-page">
    <PageHeader
      eyebrow="Сообщения"
      title="Диалоги с контрагентами"
      description="Выберите чат из списка или перейдите в чат со страницы поставщика."
    />

    <div v-if="error && chats.length > 0" class="chat-alert" role="alert">
      <AppIcon name="alert-circle" :size="18" />
      <span>{{ error }}</span>
    </div>

    <LoadingState v-if="!initialLoaded && loading" variant="skeleton" :rows="5" label="Загружаем диалоги…" />

    <ErrorState
      v-else-if="error && chats.length === 0"
      :message="error"
      :retrying="loading"
      @retry="loadChats"
    />

    <div v-else-if="chats.length === 0" class="ui-card ui-card--pad">
      <EmptyState
        icon="message"
        title="Диалогов пока нет"
        :description="
          authStore.user?.role === 'SUPPLIER'
            ? 'Когда покупатель напишет вам со страницы каталога, диалог появится здесь.'
            : 'Откройте карточку поставщика в каталоге и начните переписку — диалог появится здесь.'
        "
      >
        <AppButton v-if="authStore.user?.role !== 'SUPPLIER'" to="/catalog" icon="store">Открыть каталог</AppButton>
      </EmptyState>
    </div>

    <div v-else class="messenger ui-card" :class="{ 'is-conversation': showConversation }">
      <!-- ===== СПИСОК ДИАЛОГОВ ===== -->
      <aside class="dialogs" aria-label="Список диалогов">
        <div class="dialogs__head">
          <h2 class="dialogs__title">
            Чаты <span class="dialogs__count ui-num">{{ chats.length }}</span>
          </h2>
          <div class="dialogs__search">
            <AppIcon name="search" :size="16" class="dialogs__search-icon" />
            <label for="chat-search" class="sr-only">Поиск по диалогам</label>
            <input id="chat-search" v-model="chatQuery" type="search" placeholder="Поиск по диалогам" autocomplete="off" />
          </div>
        </div>

        <ul v-if="filteredChats.length" class="dialogs__list">
          <li v-for="chat in filteredChats" :key="chat.id">
            <button
              type="button"
              class="dialog"
              :class="{ 'is-active': activeChat?.id === chat.id }"
              :aria-current="activeChat?.id === chat.id ? 'true' : undefined"
              @click="selectChat(chat.id)"
            >
              <AppAvatar :name="otherUser(chat)?.email" :size="40" :tone="activeChat?.id === chat.id ? 'accent' : 'brand'" />
              <span class="dialog__body">
                <span class="dialog__top">
                  <span class="dialog__name">{{ chatTitle(chat) }}</span>
                  <time
                    v-if="chat.last_message?.created_at"
                    class="dialog__time ui-num"
                    :datetime="chat.last_message.created_at"
                  >
                    {{ listTime(chat.last_message.created_at) }}
                  </time>
                </span>
                <span class="dialog__preview" :class="{ 'is-empty': !chat.last_message?.content }">
                  {{ chat.last_message?.content || 'Нет сообщений' }}
                </span>
              </span>
            </button>
          </li>
        </ul>
        <div v-else class="dialogs__empty">
          <EmptyState compact icon="search" title="Ничего не найдено" description="Попробуйте изменить запрос.">
            <AppButton variant="ghost" size="sm" @click="chatQuery = ''">Сбросить</AppButton>
          </EmptyState>
        </div>
      </aside>

      <!-- ===== ПЕРЕПИСКА ===== -->
      <section class="conversation" aria-label="Переписка">
        <div v-if="loadingChat && !activeChat" class="conversation__state">
          <LoadingState label="Открываем чат…" />
        </div>

        <div v-else-if="!activeChat" class="conversation__state">
          <EmptyState
            icon="message"
            title="Диалог не выбран"
            description="Выберите чат из списка слева, чтобы увидеть переписку."
          />
        </div>

        <template v-else>
          <header class="conversation__head">
            <AppButton
              class="conversation__back"
              variant="ghost"
              size="sm"
              icon="arrow-left"
              icon-only
              label="К списку диалогов"
              @click="backToList"
            />
            <AppAvatar :name="otherUser(activeChat)?.email" :size="40" tone="accent" />
            <div class="conversation__who">
              <h2 class="conversation__name">{{ chatTitle(activeChat) }}</h2>
              <p class="conversation__meta">
                <span class="ui-num">{{ messageCount }}</span>
                {{ pluralize(messageCount, ['сообщение', 'сообщения', 'сообщений']) }}
              </p>
            </div>
            <span v-if="loadingChat" class="conversation__meta" role="status">Обновляем…</span>
          </header>

          <div ref="messagesRef" class="messages" role="log" aria-live="polite" aria-label="Сообщения">
            <div v-if="messageCount === 0" class="messages__empty">
              <EmptyState compact icon="message" title="Сообщений пока нет" description="Напишите первое сообщение собеседнику." />
            </div>

            <section v-for="group in messageGroups" :key="group.key" class="day">
              <p class="day__label">
                <time :datetime="group.date">{{ group.label }}</time>
              </p>
              <article
                v-for="message in group.messages"
                :key="message.id"
                class="bubble"
                :class="{ 'bubble--own': message.sender_id === me }"
              >
                <span class="sr-only">
                  {{ message.sender_id === me ? 'Вы' : message.sender?.email || `Пользователь #${message.sender_id}` }}:
                </span>
                <p class="bubble__text">{{ message.content }}</p>
                <time class="bubble__time ui-num" :datetime="message.created_at">
                  {{ formatDate(message.created_at, 'time') }}
                </time>
              </article>
            </section>
          </div>

          <form class="composer" @submit.prevent="sendMessage">
            <label for="chat-message" class="sr-only">Сообщение</label>
            <textarea
              id="chat-message"
              v-model="messageText"
              class="composer__input"
              rows="1"
              placeholder="Введите сообщение"
              aria-describedby="chat-message-hint"
              @keydown="onComposerKeydown"
            ></textarea>
            <AppButton
              type="submit"
              icon="send"
              icon-only
              label="Отправить"
              :loading="sending"
              :disabled="!messageText.trim()"
            />
            <p id="chat-message-hint" class="composer__hint">Enter — отправить, Shift+Enter — новая строка</p>
          </form>
        </template>
      </section>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  display: grid;
  gap: 1.5rem;
  min-width: 0;
}

/* ===== РАСКЛАДКА ===== */
.messenger {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  height: clamp(520px, calc(100vh - var(--header-h) - 12rem), 760px);
  overflow: hidden;
}

/* ===== СПИСОК ===== */
.dialogs {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  border-right: 1px solid var(--c-border);
  background: var(--c-surface);
}

.dialogs__head {
  display: grid;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid var(--c-border);
}

.dialogs__title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--fs-lg);
}

.dialogs__count {
  padding: 0.05rem 0.5rem;
  border-radius: var(--r-full);
  background: var(--c-surface-sunken);
  color: var(--c-text-2);
  font-size: var(--fs-xs);
  font-weight: 700;
  letter-spacing: 0;
}

.dialogs__search {
  position: relative;
}

.dialogs__search-icon {
  position: absolute;
  top: 50%;
  left: 0.8rem;
  transform: translateY(-50%);
  color: var(--c-muted);
  pointer-events: none;
}

.dialogs__search input {
  min-height: 40px;
  padding-left: 2.3rem;
  font-size: var(--fs-sm);
}

.dialogs__list {
  flex: 1;
  margin: 0;
  padding: 0.4rem;
  overflow-y: auto;
  list-style: none;
}

.dialogs__empty {
  padding: 1rem;
}

.dialog {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.7rem 0.75rem;
  border: none;
  border-radius: var(--r-md);
  background: transparent;
  text-align: left;
  transition: background var(--dur) var(--ease);
}

.dialog:hover {
  background: var(--c-surface-2);
}

.dialog.is-active {
  background: var(--c-brand-50);
  box-shadow: inset 3px 0 0 var(--c-accent);
}

.dialog__body {
  flex: 1;
  display: grid;
  gap: 0.15rem;
  min-width: 0;
}

.dialog__top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}

.dialog__name {
  overflow: hidden;
  font-weight: 700;
  font-size: var(--fs-sm);
  color: var(--c-text);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog__time {
  flex-shrink: 0;
  color: var(--c-muted);
  font-size: var(--fs-xs);
}

.dialog__preview {
  overflow: hidden;
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog__preview.is-empty {
  color: var(--c-muted);
  font-style: italic;
}

/* ===== ПЕРЕПИСКА ===== */
.conversation {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  background: var(--c-surface-2);
}

.chat-alert {
  display: flex;
  align-items: center;
  border-radius: var(--r-md);
  gap: 0.5rem;
  padding: 0.7rem 1rem;
  background: var(--c-danger-bg);
  color: var(--c-danger-600);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.conversation__state {
  flex: 1;
  display: grid;
  place-items: center;
  padding: 1.5rem;
}

.conversation__head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid var(--c-border);
  background: var(--c-surface);
}

.conversation__back {
  display: none;
}

.conversation__who {
  flex: 1;
  display: grid;
  min-width: 0;
}

.conversation__name {
  overflow: hidden;
  font-size: var(--fs-md);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation__meta {
  color: var(--c-muted);
  font-size: var(--fs-xs);
}

/* сообщения */
.messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 1rem clamp(0.85rem, 2.5vw, 1.5rem) 1.25rem;
}

.messages__empty {
  display: grid;
  place-items: center;
  height: 100%;
}

.day {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.day + .day {
  margin-top: 0.75rem;
}

.day__label {
  position: sticky;
  top: 0;
  z-index: 1;
  align-self: center;
  margin: 0.25rem 0 0.5rem;
  padding: 0.2rem 0.7rem;
  border: 1px solid var(--c-border);
  border-radius: var(--r-full);
  background: var(--c-surface);
  color: var(--c-muted);
  font-size: var(--fs-xs);
  font-weight: 700;
}

.bubble {
  align-self: flex-start;
  max-width: min(75%, 560px);
  padding: 0.55rem 0.85rem 0.4rem;
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg) var(--r-lg) var(--r-lg) var(--r-xs);
  background: var(--c-surface);
  color: var(--c-text);
  box-shadow: var(--sh-xs);
}

.bubble--own {
  align-self: flex-end;
  border-color: var(--c-brand-800);
  border-radius: var(--r-lg) var(--r-lg) var(--r-xs) var(--r-lg);
  background: var(--c-brand-800);
  color: var(--c-surface);
}

.bubble__text {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  line-height: 1.45;
}

.bubble__time {
  display: block;
  margin-top: 0.15rem;
  color: var(--c-muted);
  font-size: 0.6875rem;
  text-align: right;
}

.bubble--own .bubble__time {
  color: var(--c-brand-100);
}

/* поле ввода */
.composer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 0.35rem 0.6rem;
  padding: 0.85rem 1rem 0.7rem;
  border-top: 1px solid var(--c-border);
  background: var(--c-surface);
}

.composer__input {
  min-height: 44px;
  max-height: 160px;
  resize: none;
  field-sizing: content;
}

.composer__hint {
  grid-column: 1 / -1;
  color: var(--c-muted);
  font-size: var(--fs-xs);
}

/* ===== ОДНА ПАНЕЛЬ НА УЗКИХ ЭКРАНАХ ===== */
@media (max-width: 860px) {
  .messenger {
    grid-template-columns: minmax(0, 1fr);
    height: calc(100dvh - var(--header-h) - 6rem);
    min-height: 480px;
  }

  .dialogs {
    border-right: none;
  }

  .messenger.is-conversation .dialogs,
  .messenger:not(.is-conversation) .conversation {
    display: none;
  }

  .conversation__back {
    display: inline-flex;
  }

  .conversation__head {
    padding: 0.7rem 0.75rem;
  }

  .bubble {
    max-width: 85%;
  }

  .composer__hint {
    display: none;
  }
}
</style>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

defineProps<{
  modelValue: boolean
  title?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const close = () => emit('update:modelValue', false)

onMounted(() => {
  const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      close()
    }
  }

  window.addEventListener('keydown', handleKeydown)

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
  })
})
</script>

<template>
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
    @click="close"
  >
    <div
      class="bg-white rounded-lg w-full max-w-lg p-6 relative"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      @click="$event.stopPropagation()"
    >
      <button
        class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 hover:cursor-pointer hover:bg-gray-200 w-6 h-6 rounded-sm"
        @click="close"
        aria-label="Close"
      >
        ✕
      </button>

      <h3 v-if="title" id="modal-title" class="text-lg font-semibold mb-4 text-gray-800">
        {{ title }}
      </h3>

      <div class="text-gray-700">
        <slot />
      </div>

      <div class="mt-6">
        <slot name="footer">
          <button
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 hover:cursor-pointer"
            @click="close"
          >
            Close
          </button>
        </slot>
      </div>
    </div>
  </div>
</template>

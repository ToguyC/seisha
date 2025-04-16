<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const toggle = () => {
  isOpen.value = !isOpen.value
}

const close = () => {
  isOpen.value = false
}

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: scale(1);
}
</style>

<template>
  <div class="relative inline-block text-left z-50" ref="dropdownRef">
    <!-- Trigger Button -->
    <div @click="toggle" class="cursor-pointer select-none">
      <slot name="trigger" />
    </div>

    <!-- Dropdown Menu -->
    <transition
      name="fade"
      enter-active-class="transition duration-150 ease-out"
      leave-active-class="transition duration-100 ease-in"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 z-50 mt-2 w-48 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black/5 focus:outline-none"
      >
        <slot />
      </div>
    </transition>
  </div>
</template>

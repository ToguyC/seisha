<script setup lang="ts">
import axios from 'axios';
import { onMounted, ref } from 'vue';

const data = ref(null);

onMounted(() => {
  axios.get("http://localhost:8000/tournament/1")
    .then(response => {
      data.value = response.data;
    })
    .catch(error => {
      console.error("Error fetching data:", error);
    });
})
</script>

<template>
  <main>
    {{ data }}
  </main>
</template>

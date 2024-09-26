<template>
  <div id="app">
    <h1>Chatbot</h1>
    <div v-for="msg in messages" :key="msg.id" class="message">
      <span :class="msg.role">{{ msg.content }}</span>
    </div>
    <div>
      <input v-model="userInput" @keyup.enter="sendMessage" placeholder="Type a message..." />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      userInput: '',
      messages: [
        { id: 0, role: 'assistant', content: '有什么可以帮您的？' }
      ],
      max_length: 512,
    };
  },
  methods: {
    sendMessage() {
      if (this.userInput.trim()) {
        this.messages.push({ id: this.messages.length + 1, role: 'user', content: this.userInput });
        fetch(`http://192.168.10.225:5000/chat`, {  // 路由名与后端一致
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: this.userInput }],
          max_length: this.max_length
        })
      })
      .then(response => response.json())
      .then(data => {
        this.messages.push({ id: this.messages.length + 1, role: 'assistant', content: data.response });
      })
      .catch(error => console.error('Error:', error));
      this.userInput = '';
      }
    }
  }
}
</script>

<style>
.message {
  margin-bottom: 10px;
}
.user {
  color: blue;
}
.assistant {
  color: green;
}
</style>
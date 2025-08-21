document.addEventListener('DOMContentLoaded', () => {
  const chatbox = document.getElementById('chatbox');
  const userInput = document.getElementById('userInput');
  const sendBtn = document.getElementById('sendBtn');

  let conversationId = null;

  sendBtn.addEventListener('click', sendMessage);
  userInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendMessage();
  });

  function appendMessage(role, content) {
    const bubble = document.createElement('div');
    bubble.className = role === 'user'
      ? 'text-right text-blue-600'
      : 'text-left text-green-700';
    bubble.innerText = content;
    chatbox.appendChild(bubble);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage('user', message);
    userInput.value = '';

    try {
      const response = await fetch('/chatbot/api/get-response/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          conversation_id: conversationId,
        }),
      });

      const data = await response.json();

      if (data.status === 'ok') {
        conversationId = data.conversation_id;
        appendMessage('ai', data.ai_message);
      } else {
        appendMessage('ai', `❌ Error: ${data.error_message}`);
      }
    } catch (err) {
      console.error(err);
      appendMessage('ai', '❌ Something went wrong. Please try again later.');
    }
  }
});

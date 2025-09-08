document.addEventListener("DOMContentLoaded", function() {
    const chatBox = document.getElementById("chat-box");
    const promptInput = document.getElementById("prompt-input");
    const sendButton = document.getElementById("send-button");
    const charCounter = document.getElementById("char-counter");
    let sessionId = null;

    // Function to start a new session
    async function startSession() {
        try {
            const response = await fetch('/start_session', {
                method: 'POST',
            });
            if (!response.ok) throw new Error('Session start failed');
            const data = await response.json();
            sessionId = data.session_id;
        } catch (error) {
            console.error('Error starting session:', error);
            appendMessage('Системная ошибка', 'Не удалось начать сессию. Пожалуйста, обновите страницу.', 'bot');
        }
    }

    // Function to append a message to the chat box
    function appendMessage(sender, text, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');

        const avatar = document.createElement('div');
        avatar.classList.add('message-avatar');
        if (type === 'user') {
            avatar.classList.add('user-avatar');
        } else {
            avatar.classList.add('bot-avatar');
            avatar.textContent = 'ЮГ'; // Short for ЮрГид
        }

        const content = document.createElement('div');
        content.classList.add('message-content');

        const senderElement = document.createElement('div');
        senderElement.classList.add('message-sender');
        senderElement.textContent = sender;

        const textElement = document.createElement('div');
        textElement.classList.add('message-text');
        textElement.textContent = text;

        content.appendChild(senderElement);
        content.appendChild(textElement);
        messageElement.appendChild(avatar);
        messageElement.appendChild(content);

        // Insert message at the top of the chat box (like a timeline)
        chatBox.insertBefore(messageElement, chatBox.firstChild);
    }

    // Function to show typing indicator
    function showThinkingIndicator() {
        const thinkingElement = document.createElement('div');
        thinkingElement.id = 'thinking';
        thinkingElement.classList.add('message');
        thinkingElement.innerHTML = '<div class="message-avatar bot-avatar">ЮГ</div><div class="message-content"><div class="message-sender">ЮрГид KZ</div><div class="message-text thinking">печатает...</div></div>';
        chatBox.insertBefore(thinkingElement, chatBox.firstChild);
    }

    // Function to remove typing indicator
    function removeThinkingIndicator() {
        const thinkingElement = document.getElementById('thinking');
        if (thinkingElement) {
            thinkingElement.remove();
        }
    }

    // Function to send a message
    async function sendMessage() {
        const prompt = promptInput.value.trim();
        if (prompt === '' || sessionId === null) return;

        appendMessage('Вы', prompt, 'user');
        promptInput.value = '';
        updateCharCounter();
        showThinkingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt, session_id: sessionId }),
            });

            removeThinkingIndicator();

            if (!response.ok) throw new Error('Chat request failed');

            const data = await response.json();
            appendMessage('ЮрГид KZ', data.response, 'bot');

        } catch (error) {
            console.error('Error during chat:', error);
            removeThinkingIndicator();
            appendMessage('ЮрГид KZ', 'Произошла ошибка при обработке вашего запроса.', 'bot');
        }
    }

    // Function to update character counter
    function updateCharCounter() {
        const remaining = 140 - promptInput.value.length;
        charCounter.textContent = remaining;
        charCounter.style.color = remaining < 10 ? 'red' : '#888';
    }

    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    promptInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    promptInput.addEventListener('input', updateCharCounter);

    // Initialize
    startSession();
    updateCharCounter();
});
// --- Setup ---
const userId     = Number(localStorage.getItem('currentUserId'));
const chatUserId = Number(localStorage.getItem('chatUserId'));
const chatUsername = localStorage.getItem('chatUsername') || 'Chat';

// Load messages from localStorage or start empty
let messages = JSON.parse(localStorage.getItem(`messages_${userId}_${chatUserId}`)) || [];

// --- On Page Load ---
window.addEventListener('load', () => {

    // Redirect if not logged in
    if (!localStorage.getItem('isLoggedIn') || !userId) {
        window.location.href = 'index.html';
        return;
    }

    // Show who we're chatting with
    document.getElementById('chatWith').textContent = chatUsername;

    // Show saved messages
    displayMessages();

    // Connect to WebSocket
    
    const ws = new WebSocket(`ws://localhost:${API_PORT}/ws/${userId}`);
    window.ws = ws;

    // When a message arrives from the backend
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.sender_id) {
            messages.push(data);
            save();
            displayMessages();
        }
    };
});

// --- Send Message ---
function sendMessage() {
    const input = document.getElementById('messageInput');
    const text  = input.value.trim();
    if (!text) return;

    const msg = {
        sender_id  : userId,
        receiver_id: chatUserId,
        message    : text,
        timestamp  : new Date().toLocaleString()
    };

    // Send to backend
    window.ws.send(JSON.stringify(msg));

    // Show immediately without waiting for server
    messages.push(msg);
    save();
    displayMessages();

    input.value = '';
}

// --- Show Messages on Screen ---
function displayMessages() {
    const area = document.getElementById('messagesArea');
    area.innerHTML = '';

    messages.forEach(msg => {
        const isMe = Number(msg.sender_id) === userId;
        
        const raw = msg.created_at ?? msg.sent_at ?? null;
        const date = raw ? new Date(raw) : new Date();
        const time = isNaN(date) ? 'now' : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const row = document.createElement('div');
        row.className = `msg-row ${isMe ? 'mine' : ''}`;
        row.innerHTML = `
            <div class="avatar ${isMe ? 'me' : 'them'}">
                ${isMe ? 'Me' : chatUsername.slice(0, 2).toUpperCase()}
            </div>
            <div class="bubble-group">
                ${!isMe ? `<span class="sender-name">${chatUsername}</span>` : ''}
                <div class="bubble ${isMe ? 'mine' : 'them'}">${msg.message}</div>
                <span class="timestamp">${time}</span>
            </div>
        `;
        area.appendChild(row);
    });

    area.scrollTop = area.scrollHeight;
}


// ✅ Add this after displayMessages() in window load
async function loadMessagesFromServer() {
    //const res = await fetch(`/messages/${userId}/${chatUserId}`);
    const data = await res.json();
    if (Array.isArray(data)) {
        messages = data;
        save();
        displayMessages();
    }
}
loadMessagesFromServer();


// --- Save messages to localStorage ---
function save() {
    localStorage.setItem(`messages_${userId}_${chatUserId}`, JSON.stringify(messages));
}
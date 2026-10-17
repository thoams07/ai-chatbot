
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chat = document.getElementById("chat");
const sendBtn = document.getElementById("send-btn");

const messages = [];

function addMessage(text, role) {
    const bubble = document.createElement("div");
    bubble.className = `message ${role}`;
    bubble.textContent = text;
    chat.appendChild(bubble);
    chat.scrollTop = chat.scrollHeight;
    return bubble;
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const text = input.value.trim();
    if (!text || sendBtn.disabled) return;

    addMessage(text, "user");
    messages.push({ role: "user", content: text });

    input.value = "";
    sendBtn.disabled = true;

    const loading = addMessage("Thinking...", "bot");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ messages })
        });

        const data = await response.json();
        loading.remove();

        if (!response.ok) {
            addMessage(data.error || "Something went wrong.", "bot");
            messages.pop();
            return;
        }

        addMessage(data.reply, "bot");

        messages.push({
            role: "assistant",
            content: data.reply
        });

    } catch (error) {
        loading.remove();
        addMessage(
            "Cannot connect to the server. Please try again.",
            "bot"
        );
        messages.pop();
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
});

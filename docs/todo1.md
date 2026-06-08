# 🧩 TODO 1 — Give the chatbot a memory

A bare LLM call is **stateless** — the model sees only what you send in that one request and
remembers nothing afterwards. So how does a chatbot "remember" your name from three turns ago?

**It doesn't — you do.** The trick is to keep a running list of every message (yours and the
model's) and *re-send the whole list* on every turn. The growing `self.history` list **is** the
memory. The model re-reads the entire conversation each time and continues from there.

### What to implement
Fill in `Chatbot.send(user_message)` so that it:
1. **Appends** the user's message to `self.history` as `{"role": "user", "content": user_message}`.
2. **Calls** the API with the *entire* history: `client.messages.create(model=MODEL,
   max_tokens=MAX_TOKENS, system=self.system, messages=self.history)`.
3. **Extracts** the text with the `text_of(...)` helper.
4. **Appends** the reply to `self.history` as `{"role": "assistant", "content": reply}` — this is
   the step that makes the *next* turn aware of this one.
5. **Returns** the reply.

> 💡 Forget step 4 and the bot becomes an amnesiac — every turn would start from scratch.

## ✅ Solution

Replace the placeholder cell with this, then run the **`✅ TODO 1 check`** cell:

```python
class Chatbot:
    """A multi-turn chatbot. The 'memory' is just a growing list of messages we resend."""

    def __init__(self, system: str = "You are a helpful assistant."):
        self.system = system
        self.history: list[dict] = []

    def send(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=self.system,
            messages=self.history,  # the entire conversation, every time
        )

        reply = text_of(response)

        # Here is where the history of the conversation is maintained via appending the response this turn
        self.history.append({"role": "assistant", "content": reply})

        return reply
```

_Generated from the complete notebook — this is the exact reference implementation._

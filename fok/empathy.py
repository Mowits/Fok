
def empathic_response(user: str, text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["tired", "exhausted", "sleepy", "yorgun", "bitkin", "uykusuz"]):
        return f"{user}, would you like to rest a bit? I can also remind you to drink water."
    if any(k in t for k in ["sad", "upset", "bad", "uzgun", "moralim bozuk", "kotu"]):
        return f"{user}, I am sorry you feel this way. I am here for you. Want to try a short breathing exercise?"
    if any(k in t for k in ["happy", "good", "great", "mutlu", "iyi", "harika"]):
        return f"{user}, that is great to hear. Do you want me to do anything else for you today?"
    return f"{user}, understood. How can I help you?"

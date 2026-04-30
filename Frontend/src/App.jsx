import { useState, useEffect, useRef } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);

  const bottomRef = useRef(null);

  // AI Ka Jawab Awaaz Mein
  const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "hi-IN";
    utterance.rate = 1;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  };

  // Mic Start Karo
  const startListening = async () => {
    setListening(true);
    try {
      const response = await fetch("http://localhost:8000/listen");
      const data = await response.json();
      if (data.text) {
        sendMessage(data.text);
      }
    } catch (err) {
      console.log("Voice Error:", err);
    }
    setListening(false);
  };

  const sendMessage = async (textToSend) => {
    const finalText = textToSend || input;
    if (!finalText.trim()) return;

    const userMsg = { role: "user", content: finalText };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: finalText }),
      });
      const data = await response.json();
      const aiMsg = { role: "ai", content: data.reply };
      setMessages((prev) => [...prev, aiMsg]);
      speak(data.reply);
    } catch (err) {
      const errMsg = {
        role: "ai",
        content: "Backend se connect nahi ho paya!",
      };
      setMessages((prev) => [...prev, errMsg]);
    }

    setLoading(false);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch("http://localhost:8000/proactive");
        const data = await res.json();
        if (data.message) {
          const aiMsg = { role: "ai", content: data.message };
          setMessages((prev) => [...prev, aiMsg]);
          speak(data.message);
        }
      } catch (err) {
        console.log("Proactive check error:", err);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={styles.container}>
      <div style={styles.chatBox} ref={bottomRef}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={msg.role === "user" ? styles.userMsg : styles.aiMsg}
          >
            <strong>{msg.role === "user" ? "You" : "AI"}</strong>
            <p>{msg.content}</p>
          </div>
        ))}
        {loading && <p style={styles.aiMsg}>AI soch raha hai...</p>}
      </div>

      <div style={styles.inputArea}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Kuch bhi pooch ya mic dabao..."
        />
        {/* Mic Button */}
        <button
          style={{
            ...styles.button,
            background: listening ? "#ff0000" : "#4CAF50",
          }}
          onClick={startListening}
        >
          {listening ? "🔴 Sun Raha Hai..." : "🎙️ Bolo"}
        </button>
        <button style={styles.button} onClick={() => sendMessage()}>
          Bhejo
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    background: "#1a1a2e",
    color: "white",
  },
  chatBox: {
    flex: 1,
    overflowY: "auto",
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  userMsg: {
    background: "#16213e",
    padding: "10px",
    borderRadius: "10px",
    alignSelf: "flex-end",
    maxWidth: "70%",
  },
  aiMsg: {
    background: "#0f3460",
    padding: "10px",
    borderRadius: "10px",
    alignSelf: "flex-start",
    maxWidth: "70%",
  },
  inputArea: { display: "flex", padding: "20px", gap: "10px" },
  input: {
    flex: 1,
    padding: "10px",
    borderRadius: "8px",
    border: "none",
    fontSize: "16px",
  },
  button: {
    padding: "10px 20px",
    background: "#e94560",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
};

export default App;

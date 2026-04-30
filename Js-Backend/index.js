const express = require("express");
const app = express();
app.use(express.json());

app.post("/chat", async (req, res) => {
  const userMessage = req.body.message;

  const response = await fetch("http://localhost:11434/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "mistral",
      messages: [{ role: "user", content: userMessage }],
      stream: false,
    }),
  });

  const data = await response.json();
  res.json({ reply: data.message.content });
});

app.get("/", (req, res) => {
  res.send("Server Running");
});

app.listen(3000, () => console.log("AI chal raha hai! Port 3000"));

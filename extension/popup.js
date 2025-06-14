function formatMarkdown(text) {
  return text
    .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang = "javascript", code) => {
      return `
        <div class="code-block">
          <button class="copy-btn">📋</button>
          <pre class="rounded"><code class="language-${lang}">${Prism.highlight(
        code,
        Prism.languages[lang] || Prism.languages.javascript,
        lang
      )}</code></pre>
        </div>`;
    })
    .replace(/\n/g, "<br>");
}

document.getElementById("sendBtn").addEventListener("click", async () => {
  const input = document.getElementById("queryInput");
  const chat = document.getElementById("chatContainer");
  const query = input.value.trim();

  if (!query) return;

  const avatar = document.getElementById("botAvatar");
  avatar.src = "assets/siri.gif";

  chat.innerHTML += `<div class="message user">${query}</div>`;
  chat.scrollTop = chat.scrollHeight;
  input.value = "";

  try {
    const res = await fetch("http://localhost:8000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: query }),
    });

    let data = await res.json();

    if (typeof data === "string") {
      try {
        data = JSON.parse(data);
      } catch {
        throw new Error("Invalid JSON format");
      }
    }

    avatar.src = "assets/assistant.png";

    const answer = formatMarkdown(data.Answer || "Error: No response.");
    const section = data.Section ;
    const sub = data.Sub_section;
    const link = data.url;
    const code = data.Code
      ? `<pre class="bg-dark text-light p-2 rounded mt-2"><code>${data.Code}</code></pre>`
      : "";

    let meta = "";
    if (section && sub && link) {
      meta = `
    <span class="meta">
      <strong>Section:</strong> ${section} |
      <strong>Sub:</strong> ${sub} |
      <a href="${link}" target="_blank">🔗 Link</a>
    </span>
  `;
    }
    chat.innerHTML += `
  <div class="message bot">
    <div>${answer}</div>
    ${code}
    ${meta}
  </div>
`;

    chat.scrollTop = chat.scrollHeight;
  } catch (err) {
    chat.innerHTML += `<div class="message bot">❌ Server error. Try again later.</div>`;
    console.error(err);
  }
});

document.querySelectorAll(".copy-btn").forEach((btn) => {
  btn.onclick = () => {
    const code = btn.nextElementSibling.textContent;
    navigator.clipboard.writeText(code);
    btn.textContent = "✅";
    setTimeout(() => (btn.textContent = "📋"), 1000);
  };
});

// Inject floating icon
const icon = document.createElement("img");
icon.src = chrome.runtime.getURL("assets/siri.gif");
icon.id = "chaidocs-float-btn";
document.body.appendChild(icon);

// Inject chat container
const chatIframe = document.createElement("iframe");
chatIframe.src = chrome.runtime.getURL("popup.html");
chatIframe.style.cssText = `
  position: fixed;
  bottom: 80px;
  right: 20px;
  width: 380px;
  height: 500px;
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  z-index: 9999;
  display: none;
`;
document.body.appendChild(chatIframe);

// Toggle chat visibility
icon.addEventListener("click", () => {
  chatIframe.style.display = chatIframe.style.display === "none" ? "block" : "none";
});

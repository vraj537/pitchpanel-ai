// PitchPanel Ai — Chat App (Django backend + Gemini)

const AGENTS = {
  investor: { label: "Investor Agent", icon: "ri-briefcase-4-fill", color: "text-warning" },
  customer: { label: "Skeptical Customer Agent", icon: "ri-user-voice-fill", color: "text-info" },
  competitor: { label: "Competitor Agent", icon: "ri-sword-fill", color: "text-danger" },
  verdict: { label: "Panel Verdict", icon: "ri-scales-3-fill", color: "text-success" },
};

const ChatTemplates = {
  userMsg(text) {
    return `
      <div class="chat-message user-message">
        <div class="message-avatar"><i class="ri-user-3-fill fs-4"></i></div>
        <div class="message-content"><div class="message-bubble">${text}</div></div>
      </div>`;
  },
  agentMsg(key, htmlBody) {
    const a = AGENTS[key];
    return `
      <div class="chat-message ai-message">
        <div class="message-avatar"><i class="${a.icon} ${a.color} fs-4"></i></div>
        <div class="message-content">
          <div class="fw-bold ${a.color} fs-13 mb-1">${a.label}</div>
          <div class="message-bubble">${htmlBody}</div>
        </div>
      </div>`;
  },
  typing(id, key) {
    const a = AGENTS[key];
    return `
      <div class="chat-message ai-message" id="${id}">
        <div class="message-avatar"><i class="${a.icon} ${a.color} fs-4"></i></div>
        <div class="message-content">
          <div class="fw-bold ${a.color} fs-13 mb-1">${a.label}</div>
          <div class="message-bubble typing-bubble">
            <div class="typing-indicator"><span></span><span></span><span></span></div>
          </div>
        </div>
      </div>`;
  },
};

class PitchPanelChat {
  constructor() {
    this.dom = {
      input: document.getElementById("chatInput"),
      sendBtn: document.getElementById("sendBtn"),
      msgList: document.getElementById("chatMessageList"),
      container: document.getElementById("chatContainer"),
      headerTitle: document.getElementById("chatHeaderTitle"),
      historyList: document.getElementById("chatHistoryList"),
    };
    if (!this.dom.input || !this.dom.container) return;

    this.activePitchId = null;
    const emptyStateEl = document.getElementById("emptyChatState");
    this.emptyStateHTML = emptyStateEl ? emptyStateEl.outerHTML : "";

    this.bindEvents();
    window.startNewChat = () => this.startNewChat();
  }

  bindEvents() {
    this.dom.input.addEventListener("input", () => this.autoResize());
    this.dom.input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    this.dom.sendBtn.addEventListener("click", () => this.sendMessage());

    if (this.dom.historyList) {
      this.dom.historyList.querySelectorAll(".chat-history-item").forEach((el) => {
        el.addEventListener("click", (e) => {
          e.preventDefault();
          this.loadPitch(el.dataset.url, el.dataset.pitchId);
        });
      });
    }
  }

  autoResize() {
    const el = this.dom.input;
    el.style.height = "auto";
    el.style.height = el.value.trim() === "" ? "auto" : el.scrollHeight + "px";
  }

  escapeStr(str) {
    const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" };
    return String(str).replace(/[&<>'"]/g, (c) => map[c]);
  }

  textToHtml(text) {
    if (!text) return "<p class='mb-0'></p>";
    return text
      .split(/\n{2,}/)
      .map((para) => `<p class="mb-2">${this.escapeStr(para).replace(/\n/g, "<br>")}</p>`)
      .join("");
  }

  appendMsg(html) {
    this.dom.msgList.insertAdjacentHTML("beforeend", html);
  }

  scrollBottom() {
    this.dom.container.scrollTo({ top: this.dom.container.scrollHeight, behavior: "smooth" });
  }

  async sendMessage() {
    const idea = this.dom.input.value.trim();
    if (!idea) return;

    const emptyState = document.getElementById("emptyChatState");
    if (emptyState) emptyState.remove();

    this.appendMsg(ChatTemplates.userMsg(this.escapeStr(idea)));
    this.dom.input.value = "";
    this.autoResize();
    if (this.dom.headerTitle) {
      this.dom.headerTitle.textContent = idea.length > 40 ? idea.slice(0, 40) + "…" : idea;
    }
    this.scrollBottom();

    const order = ["investor", "customer", "competitor", "verdict"];
    order.forEach((key) => this.appendMsg(ChatTemplates.typing("typing-" + key, key)));
    this.scrollBottom();

    let result;
    try {
      const res = await fetch(window.PITCHPANEL_CONFIG.submitUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": window.PITCHPANEL_CONFIG.csrfToken,
        },
        body: JSON.stringify({ idea }),
      });
      result = await res.json();
      if (!res.ok) throw new Error(result.error || "Request failed (" + res.status + ")");
    } catch (err) {
      order.forEach((key) => {
        const el = document.getElementById("typing-" + key);
        if (el) el.remove();
      });
      this.appendMsg(
        ChatTemplates.agentMsg(
          "verdict",
          `<p class="mb-0 text-danger">${this.escapeStr(
            err.message || "Something went wrong reaching the AI panel. Please try again in a moment."
          )}</p>`
        )
      );
      this.scrollBottom();
      console.error(err);
      return;
    }

    order.forEach((key) => {
      const el = document.getElementById("typing-" + key);
      if (el) el.remove();
      this.appendMsg(ChatTemplates.agentMsg(key, this.textToHtml(result[key] || "")));
    });
    this.scrollBottom();

    this.activePitchId = result.id;
    this.prependHistoryItem(result.id, idea);
  }

  prependHistoryItem(id, idea) {
    if (!this.dom.historyList) return;
    const emptyMsg = document.getElementById("historyEmptyMsg");
    if (emptyMsg) emptyMsg.remove();

    const label = idea.length > 34 ? idea.slice(0, 34) + "…" : idea;
    const a = document.createElement("a");
    a.href = "#";
    a.className = "chat-history-item active";
    a.dataset.pitchId = id;
    a.dataset.url = `/ai-chat/pitch/${id}/`;
    a.innerHTML = `<i class="ri-chat-3-line me-2"></i> ${this.escapeStr(label)}`;
    a.addEventListener("click", (e) => {
      e.preventDefault();
      this.loadPitch(a.dataset.url, id);
    });

    this.dom.historyList.querySelectorAll(".chat-history-item").forEach((el) => el.classList.remove("active"));
    this.dom.historyList.prepend(a);
  }

  async loadPitch(url, id) {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error("Could not load pitch");
      const data = await res.json();

      this.activePitchId = data.id;
      this.dom.msgList.innerHTML = "";
      this.appendMsg(ChatTemplates.userMsg(this.escapeStr(data.idea)));
      this.appendMsg(ChatTemplates.agentMsg("investor", this.textToHtml(data.investor)));
      this.appendMsg(ChatTemplates.agentMsg("customer", this.textToHtml(data.customer)));
      this.appendMsg(ChatTemplates.agentMsg("competitor", this.textToHtml(data.competitor)));
      this.appendMsg(ChatTemplates.agentMsg("verdict", this.textToHtml(data.verdict)));

      if (this.dom.headerTitle) {
        this.dom.headerTitle.textContent = data.idea.length > 40 ? data.idea.slice(0, 40) + "…" : data.idea;
      }
      this.dom.historyList.querySelectorAll(".chat-history-item").forEach((el) => {
        el.classList.toggle("active", el.dataset.pitchId === String(id));
      });
      this.scrollBottom();
    } catch (err) {
      console.error("Could not load pitch:", err);
    }
  }

  startNewChat() {
    this.activePitchId = null;
    this.dom.msgList.innerHTML = this.emptyStateHTML;
    if (this.dom.headerTitle) this.dom.headerTitle.textContent = "New Pitch";
    if (this.dom.historyList) {
      this.dom.historyList.querySelectorAll(".chat-history-item").forEach((el) => el.classList.remove("active"));
    }
  }
}

document.addEventListener("DOMContentLoaded", () => new PitchPanelChat());

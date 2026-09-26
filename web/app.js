const API_URL = "https://ds-ai-wtqr.onrender.com";

const translations = {
  en: {
    subtitle: "Ask questions, search for information, and chat with DS-Ai.",
    placeholder: "Ask Nova anything..."
  },

  hi: {
    subtitle: "सवाल पूछें, जानकारी खोजें और Nova AI से चैट करें।",
    placeholder: "Nova से कुछ पूछें..."
  },

  gu: {
    subtitle: "પ્રશ્નો પૂછો, માહિતી શોધો અને DS-Ai સાથે ચેટ કરો.",
    placeholder: "Nova ને કંઈપણ પૂછો..."
  },

  pt: {
    subtitle: "Faça perguntas, pesquise informações e converse com a Nova AI.",
    placeholder: "Pergunte qualquer coisa à Nova..."
  },

  de: {
    subtitle: "Stelle Fragen, suche nach Informationen und chatte mit Nova AI.",
    placeholder: "Frag Nova etwas..."
  }
};

const language = document.getElementById("language");
const message = document.getElementById("message");
const messages = document.getElementById("messages");

language.addEventListener("change", () => {
  const selectedLanguage = translations[language.value];

  if (selectedLanguage) {
    document.getElementById("subtitle").textContent =
      selectedLanguage.subtitle;

    message.placeholder =
      selectedLanguage.placeholder;
  }
});


document.getElementById("chatForm").addEventListener(
  "submit",
  async (e) => {

    e.preventDefault();

    const text = message.value.trim();

    if (!text) {
      return;
    }

    addMessage(text, "user");

    message.value = "";

    try {

      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            message: text,
            language: language.value
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Server error"
        );
      }

      addMessage(data.reply, "bot");

    } catch (error) {

      console.error(error);

      addMessage(
        "Nova could not connect to the server.",
        "bot"
      );
    }
  }
);


function addMessage(text, type) {

  const element = document.createElement("div");

  element.className = `message ${type}`;

  element.textContent = text;

  messages.appendChild(element);

  messages.scrollTop =
    messages.scrollHeight;
}


document.getElementById("reportForm").addEventListener(
  "submit",
  async (e) => {

    e.preventDefault();

    const report =
      document.getElementById("reportMessage")
        .value
        .trim();

    const page =
      document.getElementById("reportPage")
        .value
        .trim();

    const status =
      document.getElementById("reportStatus");

    if (!report) {
      return;
    }

    try {

      const response = await fetch(
        `${API_URL}/report`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            message: report,
            page: page || "website"
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Report error"
        );
      }

      status.textContent =
        "Thanks! Your report was sent.";

      document.getElementById("reportForm").reset();

    } catch (error) {

      console.error(error);

      status.textContent =
        "Could not send the report.";
    }
  }
);
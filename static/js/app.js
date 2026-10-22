(() => {
  const $ = (selector) => document.querySelector(selector);
  const textInput = $("#text-input");
  const languageSelect = $("#language-select");
  const voiceList = $("#voice-list");
  const generateButton = $("#generate-button");
  const speedRange = $("#speed-range");
  const audio = $("#audio-element");
  let config = null;
  let toastTimer = null;
  let previewAudio = null;
  let previewRequest = 0;

  function showToast(message) {
    const toast = $("#toast");
    toast.textContent = message;
    toast.classList.add("visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 2800);
  }

  async function readError(response) {
    try {
      const body = await response.json();
      return body.error || "Something went wrong. Please try again.";
    } catch (_error) {
      return "Something went wrong. Please try again.";
    }
  }

  function updateVoiceList() {
    const language = languageSelect.value;
    const voices = (config?.voices?.[language] || []).filter((voice) => voice.enabled);
    voiceList.replaceChildren();
    if (!voices.length) {
      const empty = document.createElement("p");
      empty.className = "voice-empty";
      empty.textContent = "No verified voices available yet.";
      voiceList.append(empty);
      $("#voice-gender").textContent = "Not available yet";
      $("#voice-count").textContent = "0 voices";
      return;
    }
    const saved = localStorage.getItem(`polyvoice.voice.${language}`);
    const selectedId = saved && voices.some((voice) => voice.id === saved) ? saved : voices[0].id;
    voices.forEach((voice) => {
      const row = document.createElement("div");
      row.className = `voice-row${voice.id === selectedId ? " selected" : ""}`;
      row.setAttribute("role", "option");
      row.setAttribute("aria-selected", String(voice.id === selectedId));
      const choose = document.createElement("button");
      choose.className = "voice-choice-button";
      choose.type = "button";
      choose.textContent = voice.name;
      choose.addEventListener("click", () => selectVoice(voice.id));
      const gender = document.createElement("span");
      gender.className = "voice-row-gender";
      gender.textContent = voice.gender === "Female" ? "F" : "M";
      const preview = document.createElement("button");
      preview.className = "voice-preview-button";
      preview.type = "button";
      preview.disabled = !config.preview_available;
      preview.title = config.preview_available ? `Preview ${voice.name}` : "Voice preview will be available after engine setup";
      preview.setAttribute("aria-label", `Preview ${voice.name}`);
      preview.innerHTML = '<svg viewBox="0 0 18 18" aria-hidden="true"><path d="m6.2 4.3 7.2 4.2-7.2 4.2V4.3Z"/></svg>';
      preview.addEventListener("click", () => previewVoice(voice.id));
      row.append(choose, gender, preview);
      voiceList.append(row);
    });
    updateVoiceMetadata(selectedId);
  }

  function selectVoice(voiceId) {
    localStorage.setItem(`polyvoice.voice.${languageSelect.value}`, voiceId);
    updateVoiceList();
  }

  function currentVoiceId() {
    const language = languageSelect.value;
    const voices = (config?.voices?.[language] || []).filter((voice) => voice.enabled);
    const saved = localStorage.getItem(`polyvoice.voice.${language}`);
    return voices.some((voice) => voice.id === saved) ? saved : voices[0]?.id || "";
  }

  function updateVoiceMetadata(selectedId = currentVoiceId()) {
    const language = languageSelect.value;
    const selected = (config?.voices?.[language] || []).find((voice) => voice.id === selectedId);
    $("#voice-gender").textContent = selected ? `${selected.gender} voice` : "No voice selected";
    const count = (config?.voices?.[language] || []).filter((voice) => voice.enabled).length;
    $("#voice-count").textContent = `${count} ${count === 1 ? "voice" : "voices"}`;
  }

  async function previewVoice(voiceId) {
    const requestId = ++previewRequest;
    if (previewAudio) previewAudio.pause();
    previewAudio = null;
    audio.pause();
    try {
      const response = await fetch("/api/preview", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language: languageSelect.value, voice: voiceId }),
      });
      if (!response.ok) throw new Error(await readError(response));
      const result = await response.json();
      if (requestId !== previewRequest) return;
      const sample = new Audio(result.audio_url);
      previewAudio = sample;
      sample.addEventListener("ended", () => { if (previewAudio === sample) previewAudio = null; });
      await previewAudio.play();
    } catch (error) { showToast(error.message); }
  }

  function stopPreview() {
    previewRequest += 1;
    if (previewAudio) previewAudio.pause();
    previewAudio = null;
  }

  async function loadConfig() {
    const response = await fetch("/api/config", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("Could not load application settings.");
    config = await response.json();
    const enabledLanguages = config.languages.filter((language) => language.enabled);
    const disabledLanguages = config.languages.filter((language) => !language.enabled);
    languageSelect.replaceChildren();
    enabledLanguages.forEach((language) => languageSelect.add(new Option(language.label, language.id)));
    if (disabledLanguages.length) {
      const group = document.createElement("optgroup");
      group.label = "Not available yet";
      disabledLanguages.forEach((language) => {
        const option = new Option(`${language.label} — verification pending`, language.id);
        option.disabled = true;
        group.append(option);
      });
      languageSelect.add(group);
    }
    updateVoiceList();
    generateButton.disabled = !config.synthesis_available;
    $("#engine-status").textContent = config.status_message;
    const note = config.languages.find((language) => language.id === languageSelect.value && !language.enabled);
    $("#language-note").textContent = note?.note || "This language is not available yet.";
    $("#language-note").hidden = !note;
  }

  textInput.addEventListener("input", () => {
    $("#char-count").textContent = textInput.value.length.toLocaleString();
    $("#input-error").hidden = true;
  });

  languageSelect.addEventListener("change", () => {
    stopPreview();
    updateVoiceList();
    const unavailable = config?.languages?.find((language) => language.id === languageSelect.value && !language.enabled);
    $("#language-note").textContent = unavailable?.note || "This language is not available yet.";
    $("#language-note").hidden = !unavailable;
  });
  speedRange.addEventListener("input", () => {
    const speed = Number(speedRange.value);
    $("#speed-value").value = `${speed.toFixed(1)}×`;
    const percent = ((speed - 0.5) / 1) * 100;
    speedRange.style.background = `linear-gradient(to right, var(--accent) ${percent}%, #393a3e ${percent}%)`;
  });

  generateButton.addEventListener("click", async () => {
    const text = textInput.value.trim();
    if (!text) {
      $("#input-error").textContent = "Enter some text before generating audio.";
      $("#input-error").hidden = false;
      textInput.focus();
      return;
    }
    const original = generateButton.querySelector(".generate-label").textContent;
    generateButton.disabled = true;
    generateButton.querySelector(".generate-label").textContent = "PREPARING AUDIO…";
    $("#engine-status").textContent = "Preparing speech. This can take a moment.";
    try {
      const response = await fetch("/api/generate", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language: languageSelect.value, voice: currentVoiceId(), speed: Number(speedRange.value) }),
      });
      if (!response.ok) throw new Error(await readError(response));
      const result = await response.json();
      stopPreview();
      audio.src = result.audio_url;
      $("#download-link").href = result.download_url || result.audio_url;
      $("#player-section").hidden = false;
      audio.load();
      audio.play();
      $("#engine-status").textContent = "Audio is ready.";
    } catch (error) {
      showToast(error.message);
      $("#engine-status").textContent = config?.status_message || "Audio could not be generated.";
    } finally {
      generateButton.disabled = !config?.synthesis_available;
      generateButton.querySelector(".generate-label").textContent = original;
    }
  });

  function formatTime(seconds) {
    if (!Number.isFinite(seconds)) return "0:00";
    const minutes = Math.floor(seconds / 60);
    const remainder = Math.floor(seconds % 60).toString().padStart(2, "0");
    return `${minutes}:${remainder}`;
  }
  const playButton = $("#play-button");
  playButton.addEventListener("click", () => { if (audio.paused) { stopPreview(); audio.play(); } else audio.pause(); });
  $("#restart-button").addEventListener("click", () => { stopPreview(); audio.currentTime = 0; audio.play(); });
  $("#seek-range").addEventListener("input", (event) => {
    if (Number.isFinite(audio.duration)) audio.currentTime = (Number(event.target.value) / 1000) * audio.duration;
  });
  $("#volume-range").addEventListener("input", (event) => { audio.volume = Number(event.target.value); });
  audio.volume = 0.85;
  audio.addEventListener("play", () => playButton.classList.add("is-playing"));
  audio.addEventListener("pause", () => playButton.classList.remove("is-playing"));
  audio.addEventListener("ended", () => playButton.classList.remove("is-playing"));
  audio.addEventListener("timeupdate", () => {
    $("#elapsed-time").textContent = formatTime(audio.currentTime);
    if (Number.isFinite(audio.duration) && audio.duration > 0) {
      const progress = audio.currentTime / audio.duration;
      $("#seek-range").value = Math.round(progress * 1000);
      $("#timeline-fill").style.width = `${progress * 100}%`;
    }
  });
  audio.addEventListener("loadedmetadata", () => { $("#duration-time").textContent = formatTime(audio.duration); });
  window.addEventListener("beforeunload", stopPreview);

  loadConfig().catch((error) => {
    $("#engine-status").textContent = error.message;
    showToast(error.message);
  });
})();

const form = document.getElementById("songForm");
const errorBox = document.getElementById("errorBox");
const resetButton = document.getElementById("resetButton");
const bpmInput = document.getElementById("bpm");
const bpmValue = document.getElementById("bpmValue");
const presetGrid = document.getElementById("presetGrid");
const tagSections = document.getElementById("tagSections");
const selectedTagSummary = document.getElementById("selectedTagSummary");
const randomTagsButton = document.getElementById("randomTagsButton");
const clearTagsButton = document.getElementById("clearTagsButton");
const soundTagsInput = document.getElementById("soundTags");

const tagGroups = {
  mood: {
    label: "Mood",
    items: {
      calm: "잔잔한",
      dreamy: "몽환적인",
      nostalgic: "향수 어린",
      cozy: "포근한",
      melancholic: "쓸쓸한",
      hopeful: "희망적인",
      uplifting: "희망찬",
      romantic: "로맨틱한",
      energetic: "에너지 넘침",
    },
  },
  genre: {
    label: "Genre",
    items: {
      lofi: "로파이",
      chillhop: "칠합",
      "city pop": "시티팝",
      "neo soul": "네오소울",
      synthwave: "신스웨이브",
      "acoustic pop": "어쿠스틱 팝",
      "indie folk": "인디 포크",
      "future bass": "퓨처베이스",
    },
  },
  instrument: {
    label: "Instrument",
    items: {
      piano: "피아노",
      "electric piano": "일렉 피아노",
      "acoustic guitar": "통기타",
      "jazz guitar": "재즈 기타",
      "warm bass": "웜 베이스",
      "analog synth": "아날로그 신스",
      strings: "스트링",
      saxophone: "색소폰",
    },
  },
  groove: {
    label: "Groove & Texture",
    items: {
      "steady 4/4": "스테디 4/4",
      "slow swing": "슬로우 스윙",
      "half-time beat": "하프타임",
      "groovy funk": "그루비 펑크",
      "room reverb": "룸 리버브",
      "tape saturation": "테이프 새츄레이션",
      "city ambience": "도시 사운드",
      "soft distortion": "소프트 디스토션",
    },
  },
};

const presets = [
  {
    name: "공부용 Lofi",
    concept: "집중이 필요한 오후, 조용히 흐르는 공부용 로파이",
    situation: "카페 작업",
    emotion: "담담함",
    genre: "Lo-fi pop",
    vocal: "없음",
    language: "가사 없음",
    bpm: 72,
    tags: ["calm", "lofi", "piano", "warm bass", "steady 4/4", "room reverb"],
  },
  {
    name: "비오는 날 감성",
    concept: "비 오는 밤 창가에서 오래된 마음을 정리하는 노래",
    situation: "새벽 감성",
    emotion: "쓸쓸함",
    genre: "City pop",
    vocal: "여성 보컬",
    language: "한국어",
    bpm: 88,
    tags: ["melancholic", "dreamy", "city pop", "electric piano", "slow swing", "city ambience"],
  },
  {
    name: "드라이브 Chill",
    concept: "늦은 밤 도로 위를 부드럽게 달리는 드라이브 음악",
    situation: "여행",
    emotion: "희망적",
    genre: "Synthwave",
    vocal: "남성 보컬",
    language: "영어",
    bpm: 104,
    tags: ["uplifting", "synthwave", "analog synth", "warm bass", "steady 4/4", "room reverb"],
  },
  {
    name: "어쿠스틱 새출발",
    concept: "조용한 아침, 다시 시작하는 마음을 담은 어쿠스틱 팝",
    situation: "새로운 시작",
    emotion: "따뜻함",
    genre: "Acoustic pop",
    vocal: "여성 보컬",
    language: "한국어",
    bpm: 96,
    tags: ["cozy", "hopeful", "acoustic pop", "acoustic guitar", "strings", "steady 4/4"],
  },
  {
    name: "몽환 R&B",
    concept: "새벽 공기처럼 부드럽고 몽환적인 R&B 트랙",
    situation: "새벽 감성",
    emotion: "몽환적",
    genre: "R&B",
    vocal: "듀엣",
    language: "한국어와 영어 혼합",
    bpm: 82,
    tags: ["dreamy", "romantic", "neo soul", "electric piano", "warm bass", "half-time beat"],
  },
  {
    name: "운동 EDM",
    concept: "짧고 강하게 몰입되는 운동용 에너지 트랙",
    situation: "운동",
    emotion: "에너지 넘침",
    genre: "EDM",
    vocal: "코러스 중심",
    language: "영어",
    bpm: 128,
    tags: ["energetic", "future bass", "analog synth", "soft distortion", "groovy funk", "steady 4/4"],
  },
];

const selectedTags = new Set();

const outputMap = {
  style_prompt: "stylePrompt",
  lyrics: "lyrics",
  song_title: "songTitle",
  youtube_title: "youtubeTitle",
  youtube_description: "youtubeDescription",
  youtube_tags: "youtubeTags",
  thumbnail_text: "thumbnailText",
};

const endpoints = {
  prompt: "/generate-prompt",
  lyrics: "/generate-lyrics",
  package: "/generate-package",
};

function getFormData() {
  return {
    concept: form.concept.value,
    situation: form.situation.value,
    emotion: form.emotion.value,
    genre: form.genre.value,
    vocal: form.vocal.value,
    language: form.language.value,
    bpm: form.bpm.value,
    duration: form.duration.value,
    sound_tags: [...selectedTags],
    sound_texture: [...form.querySelectorAll('input[name="texture"]:checked')].map((input) => input.value),
    extra: form.extra.value,
  };
}

function findTagLabel(tag) {
  for (const group of Object.values(tagGroups)) {
    if (group.items[tag]) {
      return group.items[tag];
    }
  }

  return tag;
}

function syncSelectedTags() {
  const tags = [...selectedTags];
  soundTagsInput.value = tags.join(", ");
  selectedTagSummary.textContent = tags.length
    ? tags.map((tag) => `${findTagLabel(tag)} (${tag})`).join(", ")
    : "선택된 태그 없음";
}

function renderTags() {
  tagSections.innerHTML = "";

  Object.entries(tagGroups).forEach(([, group]) => {
    const section = document.createElement("section");
    section.className = "tag-group";

    const title = document.createElement("div");
    title.className = "tag-group-title";
    title.textContent = group.label;

    const list = document.createElement("div");
    list.className = "tag-chip-list";

    Object.entries(group.items).forEach(([value, label]) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = `tag-chip${selectedTags.has(value) ? " selected" : ""}`;
      chip.textContent = label;
      chip.addEventListener("click", () => {
        if (selectedTags.has(value)) {
          selectedTags.delete(value);
        } else {
          selectedTags.add(value);
        }
        renderTags();
        syncSelectedTags();
      });
      list.appendChild(chip);
    });

    section.append(title, list);
    tagSections.appendChild(section);
  });

  syncSelectedTags();
}

function renderPresets() {
  presetGrid.innerHTML = "";

  presets.forEach((preset) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "preset-card";
    button.textContent = preset.name;
    button.addEventListener("click", () => applyPreset(preset));
    presetGrid.appendChild(button);
  });
}

function setSelectValue(select, value) {
  const option = [...select.options].find((item) => item.value === value || item.textContent === value);
  if (option) {
    select.value = option.value;
  }
}

function applyPreset(preset) {
  form.concept.value = preset.concept;
  setSelectValue(form.situation, preset.situation);
  setSelectValue(form.emotion, preset.emotion);
  setSelectValue(form.genre, preset.genre);
  setSelectValue(form.vocal, preset.vocal);
  setSelectValue(form.language, preset.language);
  form.bpm.value = preset.bpm;
  bpmValue.textContent = preset.bpm;
  selectedTags.clear();
  preset.tags.forEach((tag) => selectedTags.add(tag));
  renderTags();
}

function pickRandomTags() {
  const allTags = Object.values(tagGroups).flatMap((group) => Object.keys(group.items));
  const shuffled = [...allTags].sort(() => Math.random() - 0.5);
  selectedTags.clear();
  shuffled.slice(0, 8).forEach((tag) => selectedTags.add(tag));
  renderTags();
}

function setLoading(isLoading, activeButton = null) {
  document.querySelectorAll("button").forEach((button) => {
    button.disabled = isLoading;
  });

  if (activeButton) {
    activeButton.dataset.originalText = activeButton.textContent;
    activeButton.textContent = isLoading ? "생성 중..." : activeButton.dataset.originalText;
  }
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function hideError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function formatValue(key, value) {
  if (key === "youtube_tags" && Array.isArray(value)) {
    return value.map((tag) => `#${String(tag).replace(/^#/, "").trim()}`).join(" ");
  }

  if (Array.isArray(value)) {
    return value.join(", ");
  }

  return value || "";
}

function renderResult(data) {
  Object.entries(outputMap).forEach(([key, elementId]) => {
    const element = document.getElementById(elementId);
    element.textContent = formatValue(key, data[key]);
  });
}

async function generate(action, button) {
  hideError();
  setLoading(true, button);

  try {
    const response = await fetch(endpoints[action], {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(getFormData()),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "생성 요청에 실패했습니다.");
    }

    renderResult(data);
  } catch (error) {
    showError(error.message || "알 수 없는 오류가 발생했습니다.");
  } finally {
    const originalText = button.dataset.originalText;
    setLoading(false);
    if (originalText) {
      button.textContent = originalText;
    }
  }
}

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => {
    generate(button.dataset.action, button);
  });
});

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const target = document.getElementById(button.dataset.copy);
    const text = target.textContent.trim();

    if (!text) {
      showError("복사할 내용이 아직 없습니다.");
      return;
    }

    await navigator.clipboard.writeText(text);
    const originalText = button.textContent;
    button.textContent = "완료";
    setTimeout(() => {
      button.textContent = originalText;
    }, 900);
  });
});

resetButton.addEventListener("click", () => {
  form.reset();
  selectedTags.clear();
  renderTags();
  bpmValue.textContent = bpmInput.value;
  hideError();
  Object.values(outputMap).forEach((elementId) => {
    document.getElementById(elementId).textContent = "";
  });
});

bpmInput.addEventListener("input", () => {
  bpmValue.textContent = bpmInput.value;
});

randomTagsButton.addEventListener("click", pickRandomTags);

clearTagsButton.addEventListener("click", () => {
  selectedTags.clear();
  renderTags();
});

renderPresets();
renderTags();

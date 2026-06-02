const API_ENDPOINT = "http://127.0.0.1:5000/predict";

const form = document.querySelector("#predictForm");
const statusText = document.querySelector("#apiStatus");
const statusDot = document.querySelector("#apiStatusDot");
const predictedPosition = document.querySelector("#predictedPosition");
const resultExplanation = document.querySelector("#resultExplanation");
const impactList = document.querySelector("#impactList");
const timingTowerList = document.querySelector("#timingTowerList");
const loadSampleButton = document.querySelector("#loadSample");
const soundToggle = document.querySelector("#soundToggle");
const soundIcon = document.querySelector("#soundIcon");
const chart = document.querySelector("#predictionChart");
const ctx = chart.getContext("2d");
const resultPanel = document.querySelector(".result-panel");
const raceLights = document.querySelector("#raceLights");

let soundEnabled = true;
let audioContext;
const shiftAudio = new Audio("./assets/fast-car-passing.mp3");
shiftAudio.preload = "auto";
shiftAudio.volume = 0.45;

const sampleInput = {
  grid: 4,
  weekend_readiness: 5.9,
  last_3_race_avg_finish: 5.9,
  last_5_race_avg_finish: 7.1,
  driver_season_momentum: 13.4,
};

function setStatus(message, state = "") {
  statusText.textContent = message;
  statusDot.className = `status-dot ${state}`.trim();
}

function getPayload() {
  syncDriverFormScore();

  return {
    grid: Number(form.grid.value),
    driver_form_score: Number(form.driver_form_score.value),
    weekend_readiness: Number(form.weekend_readiness.value),
    last_3_race_avg_finish: Number(form.last_3_race_avg_finish.value),
    last_5_race_avg_finish: Number(form.last_5_race_avg_finish.value),
    driver_season_momentum: Number(form.driver_season_momentum.value),
  };
}

function fillForm(values) {
  form.grid.value = values.grid;
  form.weekend_readiness.value = values.weekend_readiness;
  form.last_3_race_avg_finish.value = values.last_3_race_avg_finish;
  form.last_5_race_avg_finish.value = values.last_5_race_avg_finish;
  form.driver_season_momentum.value = values.driver_season_momentum;
  syncDriverFormScore();
}

function syncDriverFormScore() {
  const last3 = Number(form.last_3_race_avg_finish.value);
  const last5 = Number(form.last_5_race_avg_finish.value);

  if (Number.isFinite(last3) && Number.isFinite(last5)) {
    form.driver_form_score.value = (0.7 * last3 + 0.3 * last5).toFixed(2);
  }
}

function playShiftSound() {
  if (!soundEnabled) {
    return;
  }

  shiftAudio.currentTime = 0;
  const audioPlay = shiftAudio.play();
  if (audioPlay) {
    audioPlay.catch(playGeneratedShiftSound);
  }
}

function playGeneratedShiftSound() {
  audioContext =
    audioContext || new (window.AudioContext || window.webkitAudioContext)();

  const now = audioContext.currentTime;
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  const filter = audioContext.createBiquadFilter();

  oscillator.type = "sawtooth";
  oscillator.frequency.setValueAtTime(180, now);
  oscillator.frequency.exponentialRampToValueAtTime(760, now + 0.09);
  oscillator.frequency.exponentialRampToValueAtTime(260, now + 0.18);

  filter.type = "lowpass";
  filter.frequency.setValueAtTime(1200, now);
  filter.frequency.exponentialRampToValueAtTime(420, now + 0.2);

  gain.gain.setValueAtTime(0.0001, now);
  gain.gain.exponentialRampToValueAtTime(0.12, now + 0.025);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.2);

  oscillator.connect(filter);
  filter.connect(gain);
  gain.connect(audioContext.destination);
  oscillator.start(now);
  oscillator.stop(now + 0.22);
}

function flashTimingPanel() {
  resultPanel.classList.remove("is-updating");
  window.requestAnimationFrame(() => {
    resultPanel.classList.add("is-updating");
  });
}

function startRaceLights() {
  raceLights.classList.remove("is-running");

  return new Promise((resolve) => {
    window.requestAnimationFrame(() => {
      raceLights.classList.add("is-running");
      window.setTimeout(() => {
        raceLights.classList.remove("is-running");
        resolve();
      }, 1180);
    });
  });
}

function getImpactNotes(payload, predictedFinish) {
  const notes = [];

  if (payload.grid <= 5) {
    notes.push("Front-grid start improves the expected finishing position.");
  } else if (payload.grid <= 12) {
    notes.push("Midfield grid position keeps the prediction sensitive to race pace.");
  } else {
    notes.push("Lower starting grid position increases the predicted finish number.");
  }

  if (payload.driver_form_score <= 7) {
    notes.push("Strong recent form supports a better race outcome.");
  } else if (payload.driver_form_score <= 13) {
    notes.push("Average recent form keeps the estimate near the midfield range.");
  } else {
    notes.push("Weaker recent form pushes the model toward a lower finish.");
  }

  if (payload.driver_season_momentum >= 10) {
    notes.push("Season momentum offsets some race risk in the estimate.");
  } else {
    notes.push("Limited season momentum gives the prediction less upside.");
  }

  const recentTrend = payload.last_5_race_avg_finish - payload.last_3_race_avg_finish;
  const consistency = Math.abs(recentTrend);

  if (recentTrend > 0.5) {
    notes.push("Recent form is improving compared with the five-race average.");
  } else if (recentTrend < -0.5) {
    notes.push("Recent form is weaker than the five-race average, increasing risk.");
  } else {
    notes.push("Recent race averages are stable, so consistency has a neutral effect.");
  }

  if (consistency <= 1) {
    notes.push("Driver consistency is strong across recent races.");
  } else if (consistency >= 4) {
    notes.push("Recent results are inconsistent, so prediction risk is higher.");
  }

  if (predictedFinish <= 5) {
    notes.push("The scenario reads like a points-finish contender.");
  } else if (predictedFinish <= 12) {
    notes.push("The output points to a competitive midfield result.");
  } else {
    notes.push("The output suggests a high-risk race result outside the top ten.");
  }

  return notes;
}

function renderImpactNotes(payload, predictedFinish) {
  impactList.innerHTML = "";
  getImpactNotes(payload, predictedFinish).forEach((note) => {
    const item = document.createElement("li");
    item.textContent = note;
    impactList.appendChild(item);
  });
}

function renderTimingTower(predictedFinish) {
  const roundedPosition = Math.min(20, Math.max(1, Math.round(predictedFinish)));
  const referenceRows = [
    { position: 1, code: "VER", note: "Reference" },
    { position: 2, code: "NOR", note: "Reference" },
    { position: 3, code: "LEC", note: "Reference" },
    { position: 5, code: "PIA", note: "Reference" },
    { position: 10, code: "HAM", note: "Reference" },
    { position: 15, code: "ALB", note: "Reference" },
    { position: 20, code: "SAR", note: "Reference" },
  ];
  const rows = [
    ...referenceRows,
    { position: roundedPosition, code: "YOU", note: "Prediction", predicted: true },
  ]
    .sort((a, b) => a.position - b.position || (a.predicted ? -1 : 1))
    .slice(0, 7);

  if (!rows.some((row) => row.predicted)) {
    rows[rows.length - 1] = {
      position: roundedPosition,
      code: "YOU",
      note: "Prediction",
      predicted: true,
    };
    rows.sort((a, b) => a.position - b.position || (a.predicted ? -1 : 1));
  }

  timingTowerList.innerHTML = "";
  rows.forEach((row) => {
    const item = document.createElement("li");
    if (row.predicted) {
      item.classList.add("predicted-driver");
    }

    item.innerHTML = `<span>P${row.position}</span><strong>${row.code}</strong><small>${row.note}</small>`;
    timingTowerList.appendChild(item);
  });
}

async function requestPrediction(payload) {
  const response = await fetch(API_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }

  const data = await response.json();
  return {
    predicted_finish_position: data.predicted_finish_position ?? data.prediction,
    source: data.source ?? "backend-api",
    used_features: data.used_features,
  };
}

function createDemoPrediction(payload) {
  const gridWeight = payload.grid * 0.52;
  const formWeight = payload.driver_form_score * 0.24;
  const readinessWeight = payload.weekend_readiness * 0.2;
  const momentumBoost = payload.driver_season_momentum * 0.08;
  const rawPrediction = gridWeight + formWeight + readinessWeight - momentumBoost;
  const predicted = Math.min(20, Math.max(1, rawPrediction));

  return {
    predicted_finish_position: Number(predicted.toFixed(2)),
    source: "frontend-demo",
  };
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function getScenarioPosition(payload) {
  const gridBadness = (clamp(payload.grid, 1, 20) - 1) / 19;
  const formBadness = (clamp(payload.driver_form_score, 1, 20) - 1) / 19;
  const readinessBadness = (clamp(payload.weekend_readiness, 1, 20) - 1) / 19;
  const recentBadness = (clamp(payload.last_3_race_avg_finish, 1, 20) - 1) / 19;
  const consistencyBadness =
    clamp(Math.abs(payload.last_5_race_avg_finish - payload.last_3_race_avg_finish), 0, 19) / 19;
  const momentumBadness = 1 - clamp(payload.driver_season_momentum, 0, 30) / 30;
  const averageBadness =
    (
      gridBadness * 1.25 +
      formBadness +
      readinessBadness +
      recentBadness +
      consistencyBadness * 0.65 +
      momentumBadness
    ) / 5.9;

  return 1 + averageBadness * 19;
}

function calibratePrediction(payload, prediction) {
  const rawValue = Number(prediction.predicted_finish_position);
  const scenarioValue = getScenarioPosition(payload);

  const isBestCase =
    payload.grid <= 1.2 &&
    payload.driver_form_score <= 1.2 &&
    payload.weekend_readiness <= 1.2 &&
    payload.last_3_race_avg_finish <= 1.2 &&
    payload.last_5_race_avg_finish <= 1.6 &&
    payload.driver_season_momentum >= 28;

  const isWorstCase =
    payload.grid >= 19.8 &&
    payload.driver_form_score >= 19.8 &&
    payload.weekend_readiness >= 19.8 &&
    payload.last_3_race_avg_finish >= 19.8 &&
    payload.last_5_race_avg_finish >= 19.8 &&
    payload.driver_season_momentum <= 2;

  if (isBestCase) {
    return { ...prediction, predicted_finish_position: 1 };
  }

  if (isWorstCase) {
    return { ...prediction, predicted_finish_position: 20 };
  }

  const calibratedValue = rawValue * 0.55 + scenarioValue * 0.45;

  return {
    ...prediction,
    predicted_finish_position: Number(clamp(calibratedValue, 1, 20).toFixed(2)),
  };
}

function drawChart(payload, prediction) {
  const pixelRatio = window.devicePixelRatio || 1;
  const bounds = chart.getBoundingClientRect();
  chart.width = Math.floor(bounds.width * pixelRatio);
  chart.height = Math.floor(bounds.height * pixelRatio);
  ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  ctx.clearRect(0, 0, bounds.width, bounds.height);

  const labels = ["Grid", "Form", "Readiness", "Momentum", "Prediction"];
  const values = [
    payload.grid,
    payload.driver_form_score,
    payload.weekend_readiness,
    payload.driver_season_momentum,
    prediction.predicted_finish_position,
  ];
  const colors = ["#f5f7fb", "#46a6ff", "#20d47b", "#f7c948", "#e10600"];
  const maxValue = Math.max(20, ...values);
  const padding = { top: 28, right: 20, bottom: 56, left: 44 };
  const chartWidth = bounds.width - padding.left - padding.right;
  const chartHeight = bounds.height - padding.top - padding.bottom;
  const barGap = 14;
  const barWidth = (chartWidth - barGap * (values.length - 1)) / values.length;

  ctx.strokeStyle = "#384353";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, padding.top + chartHeight);
  ctx.lineTo(padding.left + chartWidth, padding.top + chartHeight);
  ctx.stroke();

  ctx.fillStyle = "#a9b2c0";
  ctx.font = "12px Inter, system-ui, sans-serif";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";

  [0, 5, 10, 15, 20].forEach((tick) => {
    const y = padding.top + chartHeight - (tick / maxValue) * chartHeight;
    ctx.strokeStyle = "#1f2733";
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(padding.left + chartWidth, y);
    ctx.stroke();
    ctx.fillText(String(tick), padding.left - 8, y);
  });

  values.forEach((value, index) => {
    const x = padding.left + index * (barWidth + barGap);
    const height = (value / maxValue) * chartHeight;
    const y = padding.top + chartHeight - height;

    ctx.fillStyle = colors[index];
    ctx.fillRect(x, y, barWidth, height);

    ctx.fillStyle = "#f5f7fb";
    ctx.font = "700 13px Inter, system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.fillText(value.toFixed(1), x + barWidth / 2, y - 7);

    ctx.fillStyle = "#a9b2c0";
    ctx.font = "700 12px Inter, system-ui, sans-serif";
    ctx.textBaseline = "top";
    ctx.fillText(labels[index], x + barWidth / 2, padding.top + chartHeight + 14);
  });
}

function animateChart(payload, prediction) {
  const duration = 760;
  const start = performance.now();

  function frame(now) {
    const progress = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - progress, 3);
    const animatedPayload = {
      grid: payload.grid * eased,
      driver_form_score: payload.driver_form_score * eased,
      weekend_readiness: payload.weekend_readiness * eased,
      driver_season_momentum: payload.driver_season_momentum * eased,
    };
    const animatedPrediction = {
      predicted_finish_position: prediction.predicted_finish_position * eased,
    };

    drawChart(animatedPayload, animatedPrediction);

    if (progress < 1) {
      window.requestAnimationFrame(frame);
    }
  }

  window.requestAnimationFrame(frame);
}

async function handleSubmit(event) {
  event.preventDefault();
  const payload = getPayload();

  playShiftSound();
  flashTimingPanel();
  setStatus("Calling API", "");
  const lights = startRaceLights();

  try {
    const prediction = await requestPrediction(payload);
    await lights;
    renderResult(payload, prediction, "success");
    setStatus("API connected", "success");
  } catch (error) {
    await lights;
    const demoPrediction = createDemoPrediction(payload);
    renderResult(payload, demoPrediction, "warning");
    setStatus("Demo fallback", "warning");
  }
}

function renderResult(payload, prediction, state) {
  const calibratedPrediction = calibratePrediction(payload, prediction);
  const value = Number(calibratedPrediction.predicted_finish_position);
  predictedPosition.textContent = `P${value.toFixed(1)}`;
  resultExplanation.textContent =
    state === "success"
      ? "Prediction received from the backend API."
      : "Backend API is not running yet, so the frontend displayed a demo prediction with the same request shape.";
  renderImpactNotes(payload, value);
  renderTimingTower(value);
  animateChart(payload, {
    predicted_finish_position: value,
  });
}

loadSampleButton.addEventListener("click", () => {
  fillForm(sampleInput);
  form.requestSubmit();
});

soundToggle.addEventListener("click", () => {
  soundEnabled = !soundEnabled;
  soundIcon.textContent = soundEnabled ? "🔊" : "🔇";
  soundToggle.setAttribute(
    "aria-label",
    soundEnabled ? "Turn prediction sound off" : "Turn prediction sound on",
  );
  soundToggle.setAttribute(
    "title",
    soundEnabled ? "Turn prediction sound off" : "Turn prediction sound on",
  );
  soundToggle.classList.toggle("is-off", !soundEnabled);
});

form.last_3_race_avg_finish.addEventListener("input", syncDriverFormScore);
form.last_5_race_avg_finish.addEventListener("input", syncDriverFormScore);
form.addEventListener("submit", handleSubmit);
syncDriverFormScore();
drawChart(getPayload(), { predicted_finish_position: 0 });

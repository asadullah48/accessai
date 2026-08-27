// AccessAI Interactive Controller & Bilingual Localization

let currentLang = 'en';

const TRANSLATIONS = {
  en: {
    badgeTitle: "WCAG 2.2 AAA Real-Time Agent",
    statusLive: "Accessibility Daemon Active (:8015)",
    heroTitle: "Real-Time Audio Description & Broadcast Accessibility",
    heroSubtitle: "Coordinate StreamAgent, NarratorAgent, and ComplianceAgent to generate zero-collision live audio descriptions and spatial sound summaries for visually impaired users with WCAG 2.2 AAA certification.",
    metric1Label: "Stream Latency",
    metric1Sub: "Real-Time Ingestion",
    metric2Label: "Accessibility Standard",
    metric2Sub: "Section 508 & ADA Level",
    metric3Label: "Dialogue Collision",
    metric3Sub: "Strict Silence Gap Fitting",
    metric4Label: "Contrast Ratio",
    metric4Sub: "Target >= 7.0 for AAA",
    studioTitle: "Live Media Accessibility Studio",
    studioDesc: "Simulate live video stream frame ingestion, inspect on-screen visual entities and silence gap budgets, synthesize SSML speech markup, and review automated WCAG 2.2 AAA compliance audits.",
    lblPresets: "Select Live Broadcast Scenario:",
    lblScene: "Scene Category",
    lblEntities: "Visual Salience & Entities (comma-separated)",
    lblOcr: "On-Screen Text OCR",
    lblSilenceGap: "Available Inter-Dialogue Silence Gap",
    btnExecuteDescribe: "🎙️ Generate Live Audio Description & Audit",
    titleAudioTrack: "Live Audio Description Stream",
    lblSpokenDesc: "Spoken Audio Description (Earcon Track):",
    lblSsml: "SSML Speech Synthesis Stream:",
    lblAuditLog: "WCAG 2.2 AAA Compliance Audit:"
  },
  ar: {
    badgeTitle: "وكيل الإتاحة الفورية WCAG 2.2 AAA",
    statusLive: "محرك إتاحة الوصول نشط (:8015)",
    heroTitle: "الوصف الصوتي الفوري وإتاحة البث الرقمي الشامل",
    heroSubtitle: "تنسيق جهود وكيل البث، ووكيل الوصف الصوتي، ووكيل الامتثال لتوليد أوصاف صوتية فورية خالية من التداخل للمستخدمين ضعاف وفاقدي البصر مع اعتماد WCAG 2.2 AAA.",
    metric1Label: "زمن استجابة البث",
    metric1Sub: "معالجة فورية للمشاهد",
    metric2Label: "معيار إمكانية الوصول",
    metric2Sub: "متوافق مع Section 508 و ADA",
    metric3Label: "تداخل الحوار الصوتي",
    metric3Sub: "تطابق تام مع فترات الصمت",
    metric4Label: "نسبة تباين النص",
    metric4Sub: "المستهدف >= 7.0 لمستوى AAA",
    studioTitle: "استوديو إتاحة الوصول للبث المباشر",
    studioDesc: "محاكاة معالجة إطارات الفيديو المباشر، واستخراج النصوص الظاهرة، وصياغة وسوم SSML للوصف الصوتي، والتدقيق الآلي لمعايير WCAG 2.2 AAA.",
    lblPresets: "اختر سيناريو البث المباشر:",
    lblScene: "تصنيف المشهد المرئي",
    lblEntities: "العناصر المرئية البارزة (مفصولة بفواصل)",
    lblOcr: "النصوص الظاهرة على الشاشة (OCR)",
    lblSilenceGap: "فترة الصمت المتاحة بين الحوارات",
    btnExecuteDescribe: "🎙️ توليد الوصف الصوتي وتدقيق المعايير",
    titleAudioTrack: "مسار الوصف الصوتي المباشر",
    lblSpokenDesc: "النص المنطوق للوصف الصوتي:",
    lblSsml: "كود النطق الصوتي القياسي (SSML):",
    lblAuditLog: "تدقيق معايير الإتاحة العالمية (WCAG 2.2 AAA):"
  }
};

const SCENARIOS = [
  {
    name: "🎓 Keynote Presentation: Enterprise AI Growth",
    scene: "Keynote Presentation",
    entities: "Presenter gesturing at slide, Bar chart showing revenue growth, Audience clapping",
    ocr: "Q4 Enterprise AI Growth: +142% YoY",
    gap: 3.5
  },
  {
    name: "🚀 Rocket Launch Broadcast: Orbital Docking",
    scene: "Spacecraft Telemetry Feed",
    entities: "Falcon spacecraft aligning with orbital station docking ring, Thrusters firing gently",
    ocr: "Docking Port Velocity 0.2 m/s",
    gap: 4.0
  },
  {
    name: "🏥 Surgical Robotics Training: Micro-Incision",
    scene: "Robotic Surgical Procedure",
    entities: "Robotic arm positioning laser scalpel, Heart rate monitor pulse wave",
    ocr: "Tissue Depth 1.2mm • Vitals Stable",
    gap: 3.0
  },
  {
    name: "⚽ Live Football Broadcast: Counterattack Goal",
    scene: "Sports Broadcast Stadium View",
    entities: "Forward sprinting past defender, Striking ball into top right corner of net",
    ocr: "GOAL! Manchester 2 - 1 Madrid (88')",
    gap: 2.5
  }
];

function init() {
  renderPresets();
  loadScenario(0);
}

function toggleLanguage() {
  currentLang = currentLang === 'en' ? 'ar' : 'en';
  document.documentElement.lang = currentLang;
  document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
  document.getElementById('langLabel').innerText = currentLang === 'en' ? 'العربية' : 'English';

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (TRANSLATIONS[currentLang][key]) {
      el.innerText = TRANSLATIONS[currentLang][key];
    }
  });
}

function renderPresets() {
  const container = document.getElementById('scenarioButtons');
  container.innerHTML = '';
  SCENARIOS.forEach((sc, idx) => {
    const btn = document.createElement('button');
    btn.className = 'preset-btn';
    btn.innerText = sc.name;
    btn.onclick = () => loadScenario(idx);
    container.appendChild(btn);
  });
}

function loadScenario(idx) {
  const sc = SCENARIOS[idx];
  document.getElementById('sceneInput').value = sc.scene;
  document.getElementById('entitiesInput').value = sc.entities;
  document.getElementById('ocrInput').value = sc.ocr;
  document.getElementById('gapRange').value = sc.gap;
  document.getElementById('gapVal').innerText = `${sc.gap}s`;
}

function updateGapLabel(val) {
  document.getElementById('gapVal').innerText = `${val}s`;
}

async function runAccessibilityStream() {
  const btn = document.getElementById('describeBtn');
  const scene = document.getElementById('sceneInput').value.trim();
  const entities = document.getElementById('entitiesInput').value.split(',').map(s => s.trim());
  const ocr = document.getElementById('ocrInput').value.trim();
  const gap = parseFloat(document.getElementById('gapRange').value);

  btn.disabled = true;
  btn.innerText = "Analyzing Live Stream -> Generating Description...";

  try {
    const res = await fetch('/api/v1/accessibility/describe-stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        frame_id: `FRM-${Date.now()}`,
        timestamp_ms: 18400,
        scene_category: scene,
        visual_entities: entities,
        on_screen_ocr: ocr,
        inter_dialogue_gap_sec: gap
      })
    });

    const data = await res.json();
    renderStreamResult(data);

  } catch (err) {
    document.getElementById('audioText').innerText = `Error: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.innerText = TRANSLATIONS[currentLang].btnExecuteDescribe;
  }
}

function renderStreamResult(data) {
  const badge = document.getElementById('complianceBadge');
  if (data.audit.is_compliant) {
    badge.className = 'badge badge-success';
    badge.innerText = `WCAG 2.2 AAA COMPLIANT (${data.audit.compliance_score}%)`;
  } else {
    badge.className = 'badge badge-danger';
    badge.innerText = `COLLISION DETECTED (${data.audit.compliance_score}%)`;
  }

  // Spoken Description Text
  document.getElementById('audioText').innerText = `"${data.description.description_text}" (Est. Speech: ${data.description.estimated_speech_sec}s)`;

  // SSML Markup
  document.getElementById('ssmlStream').innerText = data.description.ssml_markup;

  // Audit List
  const list = document.getElementById('auditList');
  list.innerHTML = '';
  data.audit.audit_notes.forEach(note => {
    const li = document.createElement('li');
    li.innerText = `• ${note}`;
    list.appendChild(li);
  });
}

window.addEventListener('DOMContentLoaded', init);

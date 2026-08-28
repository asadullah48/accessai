/**
 * AccessAI accessibility studio controller.
 *
 * Handlers are attached here rather than inline in the markup so the page stays
 * compatible with a restrictive Content-Security-Policy, and so translation can
 * replace text nodes without destroying the elements that carry event listeners.
 */

'use strict';

const API_ENDPOINT = '/api/v1/accessibility/describe-stream';

const TRANSLATIONS = {
  en: {
    documentTitle: 'AccessAI | Real-Time Audio Description & Accessibility Multi-Agent Framework',
    skipLink: 'Skip to main content',
    badgeTitle: 'WCAG 2.2 AAA Real-Time Agent',
    portfolioLink: 'DevUnity Portfolio',
    opensNewTab: '(opens in a new tab)',
    statusLive: 'Accessibility Daemon Active (:8015)',
    heroTitle: 'Real-Time Audio Description & Broadcast Accessibility',
    heroSubtitle:
      'Coordinate StreamAgent, NarratorAgent, and ComplianceAgent to generate zero-collision live audio descriptions and spatial sound summaries for visually impaired users with WCAG 2.2 AAA certification.',
    metricsHeading: 'Latest audit metrics',
    metric1Label: 'Stream Latency',
    metric1Sub: 'Budget 200ms',
    metric2Label: 'Compliance Score',
    metric2Sub: 'Weighted across 5 criteria',
    metric3Label: 'Dialogue Collision',
    metric3Sub: 'Speech must fit the silence gap',
    metric4Label: 'Caption Contrast',
    metric4Sub: 'Target >= 7.0 : 1 for AAA',
    studioTitle: 'Live Media Accessibility Studio',
    studioDesc:
      'Simulate live video stream frame ingestion, inspect on-screen visual entities and silence gap budgets, synthesize SSML speech markup, and review automated WCAG 2.2 AAA compliance audits.',
    lblPresets: 'Select Live Broadcast Scenario:',
    lblScene: 'Scene Category',
    lblEntities: 'Visual Salience & Entities (comma-separated)',
    helpEntities:
      'List entities most important first. The first entity is treated as the primary subject and is never removed when the description is shortened.',
    lblOcr: 'On-Screen Text OCR',
    lblSilenceGap: 'Available Inter-Dialogue Silence Gap',
    helpGap:
      'Seconds of silence available between lines of dialogue. The description is shortened until it fits.',
    lblExtendedPause: 'Allow extended pause (WCAG 1.2.7)',
    helpExtendedPause: 'Permits the player to pause the video so a longer description can be spoken.',
    btnExecuteDescribe: 'Generate Live Audio Description & Audit',
    btnWorking: 'Analyzing stream, generating description...',
    titleAudioTrack: 'Live Audio Description Stream',
    badgeAwaiting: 'Awaiting audit',
    badgeCompliant: 'WCAG 2.2 AAA compliant',
    badgeNonCompliant: 'Not compliant',
    lblSpokenDesc: 'Spoken Audio Description',
    lblSsml: 'SSML Speech Synthesis Stream',
    lblAuditLog: 'WCAG 2.2 AAA Compliance Audit',
    placeholderDesc: 'Select a scenario and generate a description.',
    placeholderAudit: 'No audit has run yet.',
    footerPortfolio: 'Back to Asadullah Shafique Portfolio (DevUnity)',
    footerTagline: 'Real-Time Accessibility Framework',
    footerRepo: 'GitHub Repository',
    estimatedSpeech: 'Estimated speech',
    shortened: 'shortened %d time(s) to fit the gap',
    requestFailed: 'Could not reach the accessibility gateway: %s',
    validationFailed: 'The gateway rejected the frame: %s',
    collisionYes: 'None',
    collisionNo: 'Detected',
    langButton: 'English'
  },
  ar: {
    documentTitle: 'AccessAI | الوصف الصوتي الفوري وإتاحة الوصول',
    skipLink: 'الانتقال إلى المحتوى الرئيسي',
    badgeTitle: 'وكيل الإتاحة الفورية WCAG 2.2 AAA',
    portfolioLink: 'محفظة DevUnity',
    opensNewTab: '(يفتح في نافذة جديدة)',
    statusLive: 'محرك إتاحة الوصول نشط (:8015)',
    heroTitle: 'الوصف الصوتي الفوري وإتاحة البث الرقمي الشامل',
    heroSubtitle:
      'تنسيق جهود وكيل البث، ووكيل الوصف الصوتي، ووكيل الامتثال لتوليد أوصاف صوتية فورية خالية من التداخل.',
    metricsHeading: 'مؤشرات آخر تدقيق',
    metric1Label: 'زمن استجابة البث',
    metric1Sub: 'الميزانية 200 مللي ثانية',
    metric2Label: 'درجة الامتثال',
    metric2Sub: 'موزونة على خمسة معايير',
    metric3Label: 'تداخل الحوار الصوتي',
    metric3Sub: 'يجب أن يناسب النطق فترة الصمت',
    metric4Label: 'تباين النص الظاهر',
    metric4Sub: 'المستهدف >= 7.0 : 1 لمستوى AAA',
    studioTitle: 'استوديو إتاحة الوصول للبث المباشر',
    studioDesc:
      'محاكاة معالجة إطارات الفيديو المباشر، وصياغة وسوم SSML، والتدقيق الآلي لمعايير WCAG 2.2 AAA.',
    lblPresets: 'اختر سيناريو البث المباشر:',
    lblScene: 'تصنيف المشهد المرئي',
    lblEntities: 'العناصر المرئية البارزة (مفصولة بفواصل)',
    helpEntities: 'اذكر العناصر الأهم أولاً. العنصر الأول هو الموضوع الرئيسي ولا يُحذف أبداً.',
    lblOcr: 'النصوص الظاهرة على الشاشة (OCR)',
    lblSilenceGap: 'فترة الصمت المتاحة بين الحوارات',
    helpGap: 'عدد الثواني المتاحة بين أسطر الحوار. يُختصر الوصف حتى يتناسب معها.',
    lblExtendedPause: 'السماح بإيقاف ممتد (WCAG 1.2.7)',
    helpExtendedPause: 'يسمح بإيقاف الفيديو مؤقتاً لنطق وصف أطول.',
    btnExecuteDescribe: 'توليد الوصف الصوتي وتدقيق المعايير',
    btnWorking: 'جارٍ تحليل البث وتوليد الوصف...',
    titleAudioTrack: 'مسار الوصف الصوتي المباشر',
    badgeAwaiting: 'بانتظار التدقيق',
    badgeCompliant: 'مطابق لمعيار WCAG 2.2 AAA',
    badgeNonCompliant: 'غير مطابق',
    lblSpokenDesc: 'النص المنطوق للوصف الصوتي',
    lblSsml: 'كود النطق الصوتي القياسي (SSML)',
    lblAuditLog: 'تدقيق معايير الإتاحة (WCAG 2.2 AAA)',
    placeholderDesc: 'اختر سيناريو ثم ولّد الوصف.',
    placeholderAudit: 'لم يُجرَ أي تدقيق بعد.',
    footerPortfolio: 'العودة إلى محفظة أسد الله شفيق',
    footerTagline: 'إطار عمل إتاحة الوصول الفوري',
    footerRepo: 'مستودع GitHub',
    estimatedSpeech: 'المدة المقدرة',
    shortened: 'تم اختصاره %d مرة ليناسب فترة الصمت',
    requestFailed: 'تعذر الاتصال ببوابة الإتاحة: %s',
    validationFailed: 'رفضت البوابة الإطار: %s',
    collisionYes: 'لا يوجد',
    collisionNo: 'تم اكتشافه',
    langButton: 'English'
  }
};

const SCENARIOS = [
  {
    name: 'Keynote Presentation: Enterprise AI Growth',
    scene: 'Keynote Presentation',
    entities: 'Presenter gesturing at slide, Bar chart showing revenue growth, Audience clapping',
    ocr: 'Q4 Enterprise AI Growth: +142% YoY',
    gap: 3.5
  },
  {
    name: 'Rocket Launch Broadcast: Orbital Docking',
    scene: 'Spacecraft Telemetry Feed',
    entities: 'Falcon spacecraft aligning with orbital docking ring, Thrusters firing gently',
    ocr: 'Docking Port Velocity 0.2 m/s',
    gap: 4.0
  },
  {
    name: 'Surgical Robotics Training: Micro-Incision',
    scene: 'Robotic Surgical Procedure',
    entities: 'Robotic arm positioning laser scalpel, Heart rate monitor pulse wave',
    ocr: 'Tissue Depth 1.2mm, Vitals Stable',
    gap: 3.0
  },
  {
    name: 'Live Football Broadcast: Counterattack Goal',
    scene: 'Sports Broadcast Stadium View',
    entities: 'Forward sprinting past defender, Striking ball into top corner of net',
    ocr: 'GOAL! Manchester 2 - 1 Madrid (88)',
    gap: 2.5
  }
];

let currentLang = 'en';

/** Look up a translation, falling back to English then to the key itself. */
function t(key) {
  return TRANSLATIONS[currentLang][key] || TRANSLATIONS.en[key] || key;
}

const $ = (id) => document.getElementById(id);

/* ------------------------------------------------------------------ i18n --- */

/**
 * Swap every translatable string.
 *
 * Only elements carrying data-i18n have their text replaced, so elements holding
 * event listeners survive translation. Writing innerText on a parent would
 * discard its child spans and silently break both the listeners and any later
 * translation pass.
 */
function applyTranslations() {
  document.documentElement.lang = currentLang;
  document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
  document.title = t('documentTitle');

  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const value = TRANSLATIONS[currentLang][el.dataset.i18n];
    if (value) {
      el.textContent = value;
    }
  });

  // The toggle is labelled in the language it switches TO, so it carries that
  // language's own lang attribute for correct screen-reader pronunciation.
  $('langLabel').textContent = t('langButton');
  $('langToggleBtn').lang = currentLang === 'en' ? 'ar' : 'en';
}

function toggleLanguage() {
  currentLang = currentLang === 'en' ? 'ar' : 'en';
  applyTranslations();
}

/* -------------------------------------------------------------- scenarios --- */

function renderPresets() {
  const container = $('scenarioButtons');
  container.replaceChildren();

  SCENARIOS.forEach((scenario, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'preset-btn';
    button.textContent = scenario.name;
    // aria-pressed makes the selected scenario perceivable without relying on colour.
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => loadScenario(index));
    container.appendChild(button);
  });
}

function loadScenario(index) {
  const scenario = SCENARIOS[index];
  $('sceneInput').value = scenario.scene;
  $('entitiesInput').value = scenario.entities;
  $('ocrInput').value = scenario.ocr;
  $('gapRange').value = String(scenario.gap);
  updateGapLabel();

  $('scenarioButtons')
    .querySelectorAll('.preset-btn')
    .forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
}

function updateGapLabel() {
  $('gapVal').textContent = Number($('gapRange').value).toFixed(1) + 's';
}

/* ------------------------------------------------------------------ fetch --- */

function showError(message) {
  const box = $('formError');
  box.textContent = message;
  box.hidden = false;
}

function clearError() {
  const box = $('formError');
  box.hidden = true;
  box.textContent = '';
}

function readFrame() {
  return {
    frame_id: 'FRM-' + Date.now(),
    timestamp_ms: 18400,
    scene_category: $('sceneInput').value.trim(),
    visual_entities: $('entitiesInput')
      .value.split(',')
      .map((entity) => entity.trim())
      .filter(Boolean),
    on_screen_ocr: $('ocrInput').value.trim(),
    inter_dialogue_gap_sec: Number($('gapRange').value),
    extended_pause_available: $('extendedPause').checked
  };
}

/** Flatten FastAPI's 422 detail array into one readable sentence. */
function describeValidationError(detail) {
  if (!Array.isArray(detail)) {
    return String(detail);
  }
  return detail
    .map((item) => (item.loc || []).slice(1).join('.') + ': ' + item.msg)
    .join('; ');
}

async function runAccessibilityStream(event) {
  event.preventDefault();

  const button = $('describeBtn');
  const label = $('describeBtnLabel');
  const panel = $('auditList').closest('.output-panel');

  clearError();
  button.disabled = true;
  label.textContent = t('btnWorking');
  panel.setAttribute('aria-busy', 'true');

  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(readFrame())
    });

    const data = await response.json();

    if (!response.ok) {
      // A rejected frame is a user-correctable problem, not a crash: report the
      // gateway's own reason rather than a generic failure.
      showError(t('validationFailed').replace('%s', describeValidationError(data.detail)));
      return;
    }

    renderStreamResult(data);
  } catch (error) {
    showError(t('requestFailed').replace('%s', error.message));
  } finally {
    button.disabled = false;
    label.textContent = t('btnExecuteDescribe');
    panel.removeAttribute('aria-busy');
  }
}

/* ----------------------------------------------------------------- render --- */

function renderStreamResult(data) {
  const audit = data.audit;
  const description = data.description;

  const badge = $('complianceBadge');
  badge.className = audit.is_compliant ? 'badge badge-success' : 'badge badge-danger';
  badge.textContent =
    (audit.is_compliant ? t('badgeCompliant') : t('badgeNonCompliant')) +
    ' (' + audit.compliance_score + '%)';

  // Metrics come from the audit that just ran, so the headline figures cannot
  // drift away from the record shown beneath them.
  $('metricLatency').textContent = audit.latency_ms.toFixed(2) + ' ms';
  $('metricScore').textContent = audit.compliance_score + '%';
  $('metricCollision').textContent = audit.dialogue_collision_passed
    ? t('collisionYes')
    : t('collisionNo');
  $('metricContrast').textContent = audit.wcag_rule_1_4_3_contrast_ratio.toFixed(2) + ' : 1';

  let spoken =
    '"' + description.description_text + '" (' +
    t('estimatedSpeech') + ': ' + description.estimated_speech_sec + 's)';
  if (description.prune_level > 0) {
    spoken += ' - ' + t('shortened').replace('%d', description.prune_level);
  }
  $('audioText').textContent = spoken;

  $('ssmlStream').textContent = description.ssml_markup;

  // Each check renders its own PASS/FAIL word, so the outcome never depends on
  // colour alone (WCAG 1.4.1).
  const list = $('auditList');
  list.replaceChildren();
  audit.checks.forEach((check) => {
    const item = document.createElement('li');
    const status = document.createElement('strong');
    status.textContent = check.passed ? 'PASS' : 'FAIL';
    item.appendChild(status);
    item.appendChild(
      document.createTextNode(
        ' - ' + check.title + ': ' + check.observed + ' (required: ' + check.required + ')'
      )
    );
    list.appendChild(item);
  });
}

/* ------------------------------------------------------------------- init --- */

function init() {
  renderPresets();
  loadScenario(0);
  applyTranslations();

  $('streamForm').addEventListener('submit', runAccessibilityStream);
  $('gapRange').addEventListener('input', updateGapLabel);
  $('langToggleBtn').addEventListener('click', toggleLanguage);
}

document.addEventListener('DOMContentLoaded', init);

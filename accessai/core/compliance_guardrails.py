"""
Accessibility compliance evaluation.

Each criterion is measured from the frame and the generated description; nothing
is asserted. An audit that cannot fail is not an audit, so every check here has
inputs that can make it return False.
"""

from __future__ import annotations

from accessai.core.audio_synthesizer import stable_event_id
from accessai.core.models import (
    AccessibilityAuditResult,
    AccessibilityStandard,
    AudioDescriptionEvent,
    AuditCheck,
    LiveStreamFrame,
)
from accessai.core.wcag import (
    ConformanceLevel,
    contrast_ratio,
    parse_hex_color,
    required_contrast,
)

# End-to-end budget for live broadcast; beyond this the description desynchronises
# from the picture it describes.
LATENCY_BUDGET_MS = 200.0

# Relative severity of each criterion, summing to 100.
#
# POLICY: these weights encode a judgement about how much each failure harms a
# visually impaired listener. A dialogue collision is weighted heaviest because it
# does not merely fail to help - it actively masks the dialogue the listener could
# otherwise hear. Latency is weighted lightest because a late-but-correct
# description still conveys the scene. Tune these to match your own risk posture.
CHECK_WEIGHTS = {
    "dialogue-collision": 30.0,
    "wcag-1.2.5": 25.0,
    "wcag-1.4.6": 20.0,
    "wcag-1.2.7": 15.0,
    "latency": 10.0,
}


class ComplianceGuardrails:
    """Evaluates a description against WCAG 2.2, Section 508 and ADA Title III."""

    @staticmethod
    def audit_stream_accessibility(
        frame: LiveStreamFrame,
        event: AudioDescriptionEvent,
        latency_ms: float = 120.0,
        conformance_level: ConformanceLevel = ConformanceLevel.AAA,
    ) -> AccessibilityAuditResult:
        """Measure every criterion and return the resulting audit record."""
        checks: list[AuditCheck] = []

        # --- WCAG 1.2.5 Audio Description -----------------------------------
        # An audio description track must actually exist and carry content.
        has_description = bool(event.description_text.strip())
        checks.append(
            AuditCheck(
                rule_id="wcag-1.2.5",
                title="Audio Description (Prerecorded)",
                passed=has_description,
                observed=(
                    f"{len(event.description_text.split())} word description synthesized"
                    if has_description
                    else "No description text produced"
                ),
                required="A non-empty audio description track",
                weight=CHECK_WEIGHTS["wcag-1.2.5"],
            )
        )

        # --- Dialogue collision ---------------------------------------------
        # The utterance must finish inside the silence gap between dialogue lines.
        collision_passed = event.estimated_speech_sec <= frame.inter_dialogue_gap_sec
        checks.append(
            AuditCheck(
                rule_id="dialogue-collision",
                title="Zero Dialogue Collision",
                passed=collision_passed,
                observed=f"{event.estimated_speech_sec:.2f}s of speech",
                required=f"<= {frame.inter_dialogue_gap_sec:.2f}s silence gap",
                weight=CHECK_WEIGHTS["dialogue-collision"],
            )
        )

        # --- WCAG 1.2.7 Extended Audio Description --------------------------
        # Only engaged when the description cannot fit the natural gap: the player
        # must then be able to pause the video to open an extended window.
        needs_extension = not collision_passed
        rule_127_passed = (not needs_extension) or frame.extended_pause_available
        checks.append(
            AuditCheck(
                rule_id="wcag-1.2.7",
                title="Extended Audio Description",
                passed=rule_127_passed,
                observed=(
                    "Description fits the natural gap; no extension required"
                    if not needs_extension
                    else (
                        "Extended pause window available"
                        if frame.extended_pause_available
                        else "Description overruns the gap and no extended pause is available"
                    )
                ),
                required="Extended pause available whenever the gap is too short",
                weight=CHECK_WEIGHTS["wcag-1.2.7"],
            )
        )

        # --- WCAG 1.4.6 Contrast (Enhanced) ---------------------------------
        # Measured from the frame's actual caption colours.
        ratio = contrast_ratio(
            parse_hex_color(frame.caption_foreground_hex),
            parse_hex_color(frame.caption_background_hex),
        )
        threshold = required_contrast(conformance_level, frame.caption_text_size)
        contrast_passed = ratio >= threshold
        colours = f"{frame.caption_foreground_hex} on {frame.caption_background_hex}"
        size_label = frame.caption_text_size.value.lower()
        checks.append(
            AuditCheck(
                rule_id="wcag-1.4.6",
                title="Contrast (Enhanced)",
                passed=contrast_passed,
                observed=f"{ratio:.2f}:1 measured ({colours})",
                required=f">= {threshold:.1f}:1 for {conformance_level.value} {size_label} text",
                weight=CHECK_WEIGHTS["wcag-1.4.6"],
            )
        )

        # --- Latency budget --------------------------------------------------
        latency_passed = latency_ms <= LATENCY_BUDGET_MS
        checks.append(
            AuditCheck(
                rule_id="latency",
                title="Real-Time Latency Budget",
                passed=latency_passed,
                observed=f"{latency_ms:.2f}ms end-to-end",
                required=f"<= {LATENCY_BUDGET_MS:.0f}ms",
                weight=CHECK_WEIGHTS["latency"],
            )
        )

        # --- Aggregate --------------------------------------------------------
        total_weight = sum(check.weight for check in checks)
        earned = sum(check.weight for check in checks if check.passed)
        score = round(100.0 * earned / total_weight, 1) if total_weight else 0.0
        is_compliant = all(check.passed for check in checks)

        notes = [
            f"{'PASS' if check.passed else 'FAIL'} [{check.rule_id}] {check.title}: "
            f"{check.observed} (required: {check.required})"
            for check in checks
        ]

        return AccessibilityAuditResult(
            audit_id=stable_event_id("AUD", f"{frame.frame_id}|{event.event_id}"),
            standard=AccessibilityStandard.WCAG_2_2_AAA,
            conformance_level=conformance_level,
            wcag_rule_1_2_5_passed=has_description,
            wcag_rule_1_2_7_passed=rule_127_passed,
            wcag_rule_1_4_3_contrast_ratio=round(ratio, 2),
            contrast_passed=contrast_passed,
            dialogue_collision_passed=collision_passed,
            latency_ms=latency_ms,
            latency_passed=latency_passed,
            is_compliant=is_compliant,
            compliance_score=score,
            checks=checks,
            audit_notes=notes,
        )

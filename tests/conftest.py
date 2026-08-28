"""Shared fixtures for the AccessAI test suite."""

import logging

import pytest

from accessai.core.models import LiveStreamFrame


@pytest.fixture(autouse=True)
def _silence_audit_warnings(caplog):
    """Keep intentional non-compliant fixtures from spamming test output."""
    caplog.set_level(logging.ERROR, logger="accessai.orchestration.accessai_engine")


@pytest.fixture
def nominal_frame() -> LiveStreamFrame:
    """A frame that comfortably satisfies every criterion."""
    return LiveStreamFrame(
        frame_id="FRM-NOMINAL",
        scene_category="Keynote Presentation",
        visual_entities=["Presenter gesturing at slide", "Bar chart showing growth"],
        on_screen_ocr="Q4 Growth: +142% YoY",
        inter_dialogue_gap_sec=6.0,
        caption_foreground_hex="#F2F5F7",
        caption_background_hex="#0B0F14",
    )

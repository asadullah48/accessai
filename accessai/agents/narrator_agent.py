from accessai.core.models import LiveStreamFrame, AudioDescriptionEvent, SpatialAudioPosition
from accessai.core.audio_synthesizer import AudioSynthesizer

class NarratorAgent:
    """
    NarratorAgent: Synthesizes concise, vivid audio descriptions fitted precisely
    into available silence gaps without colliding with dialogue.
    """
    def __init__(self):
        self.name = "NarratorAgent"
        self.version = "1.0.0"

    def describe_scene(self, frame: LiveStreamFrame) -> AudioDescriptionEvent:
        entities_str = ", ".join(frame.visual_entities)
        desc = f"On screen: {entities_str}. '{frame.on_screen_ocr}'."
        
        event = AudioSynthesizer.generate_ssml(desc, SpatialAudioPosition.CENTER)
        
        # Adaptive pruning loop if speech duration exceeds available dialogue silence gap
        if event.estimated_speech_sec > frame.inter_dialogue_gap_sec:
            # Concise fallback
            desc_pruned = f"{frame.visual_entities[0]}. '{frame.on_screen_ocr}'."
            event = AudioSynthesizer.generate_ssml(desc_pruned, SpatialAudioPosition.CENTER)
            
            # If still exceeding, ultra-concise
            if event.estimated_speech_sec > frame.inter_dialogue_gap_sec:
                desc_ultra = f"{frame.visual_entities[0]}."
                event = AudioSynthesizer.generate_ssml(desc_ultra, SpatialAudioPosition.CENTER)
        
        return event

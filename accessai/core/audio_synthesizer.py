from accessai.core.models import AudioDescriptionEvent, SpatialAudioPosition

class AudioSynthesizer:
    """
    AudioSynthesizer: Formats natural audio descriptions into SSML audio synthesis markup
    and calculates speech duration.
    """
    @staticmethod
    def generate_ssml(text: str, position: SpatialAudioPosition = SpatialAudioPosition.CENTER) -> AudioDescriptionEvent:
        # Standard professional audio description speech rate ~3.8 words/sec (228 wpm)
        words = text.split()
        word_count = len(words)
        duration = max(0.5, round(word_count / 3.8, 2))
        
        ssml = (
            f"<speak>\n"
            f'  <prosody rate="110%" pitch="+2st">\n'
            f'    <emphasis level="moderate">{text}</emphasis>\n'
            f'  </prosody>\n'
            f"</speak>"
        )

        return AudioDescriptionEvent(
            event_id=f"EVT-{abs(hash(text)) % 10000}",
            description_text=text,
            ssml_markup=ssml,
            estimated_speech_sec=duration,
            spatial_position=position,
            fits_silence_gap=True
        )

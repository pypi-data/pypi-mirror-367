import whisper
import torchaudio
import logging
import torch
from pathlib import Path
from typing import List, Dict, Union

def transcribe_segments(
    audio_path: str,
    speech_timestamps: List[Dict[str, float]],
    model_name: str,
    device: str
) -> List[Dict[str, Union[float, str]]]:
    """
    Транскрибирует аудиосегменты, используя OpenAI Whisper.
    
    Args:
        audio_path (str): Путь к полному аудиофайлу.
        speech_timestamps (list): Список словарей с начальным и конечным временем 
                                   каждого сегмента речи.
        model_name (str): Имя модели Whisper (например, 'base').
        device (str): Устройство для выполнения ('cuda' или 'cpu').

    Returns:
        list: Список транскрибированных сегментов.
    """
    model = whisper.load_model(model_name, device=device)
    
    transcriptions = []
    
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Аудиофайл не найден: {audio_path}")
        
    full_waveform, sample_rate = torchaudio.load(audio_path)
    
    if full_waveform.shape[0] > 1:
        full_waveform = torch.mean(full_waveform, dim=0, keepdim=True)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        full_waveform = resampler(full_waveform)
        sample_rate = 16000
    
    for segment in speech_timestamps:
        start_time = segment['start']
        end_time = segment['end']
        
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        
        audio_segment = full_waveform[:, start_sample:end_sample].squeeze().numpy()
        
        if audio_segment.size == 0:
            transcriptions.append({
                'start': start_time,
                'end': end_time,
                'text': ''
            })
            continue

        try:
            result = model.transcribe(audio_segment, language="ja")
            
            transcriptions.append({
                'start': start_time,
                'end': end_time,
                'text': result['text'].strip()
            })
        except Exception as e:
            logging.exception(f"Ошибка при транскрипции сегмента с помощью Whisper [{start_time:.2f}s - {end_time:.2f}s]: {e}")
            transcriptions.append({
                'start': start_time,
                'end': end_time,
                'text': ''
            })
            
    return transcriptions
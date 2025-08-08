import logging
import torch
import torchaudio
from pathlib import Path
from typing import List, Dict, Union

# Импортируем Whisper из transformers
from transformers import WhisperForConditionalGeneration, WhisperProcessor

# Словарь для преобразования коротких имен моделей в их полные ID на Hugging Face Hub
MODEL_IDS = {
    "tiny": "openai/whisper-tiny",
    "base": "openai/whisper-base",
    "small": "openai/whisper-small",
    "medium": "openai/whisper-medium",
    "large": "openai/whisper-large",
    "large-v2": "openai/whisper-large-v2",
    "large-v3": "openai/whisper-large-v3",
    "kotoba-whisper": "kotoba-tech/kotoba-whisper-v2.0"
}

def transcribe_segments(
    audio_path: str,
    speech_timestamps: List[Dict[str, float]],
    model_name: str,
    device: str
) -> List[Dict[str, Union[float, str]]]:
    """
    Транскрибирует аудиосегменты, используя Whisper из библиотеки transformers.
    
    Args:
        audio_path (str): Путь к полному аудиофайлу.
        speech_timestamps (list): Список словарей с начальным и конечным временем 
                                   каждого сегмента речи.
        model_name (str): Имя модели Whisper (например, 'base').
        device (str): Устройство для выполнения ('cuda' или 'cpu').

    Returns:
        list: Список транскрибированных сегментов.
    """
    # Преобразуем короткое имя модели в полный ID
    model_id = MODEL_IDS.get(model_name.lower())
    if not model_id:
        logging.error(f"Ошибка: Неизвестное имя модели: {model_name}")
        return []

    # Загружаем модель и процессор
    logging.info(f"Загрузка модели ASR: {model_id} на устройство {device}...")
    model = WhisperForConditionalGeneration.from_pretrained(model_id).to(device)
    processor = WhisperProcessor.from_pretrained(model_id)
    
    transcriptions = []
    
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Аудиофайл не найден: {audio_path}")
    
    for segment in speech_timestamps:
        start_time = segment['start']
        end_time = segment['end']
        
        start_sample = int(start_time * 16000)
        end_sample = int(end_time * 16000)
        
        try:
            # Загрузка и обработка аудио сегмента
            audio_segment, _ = torchaudio.load(
                audio_path,
                frame_offset=start_sample,
                num_frames=end_sample - start_sample
            )
            
            # Приведение к моно, если необходимо
            if audio_segment.shape[0] > 1:
                audio_segment = torch.mean(audio_segment, dim=0, keepdim=True)

            # Токенизация и подготовка к транскрибации
            inputs = processor(audio_segment.squeeze().numpy(), sampling_rate=16000, return_tensors="pt").to(device)
            
            # Генерация транскрипции
            forced_decoder_ids = processor.get_decoder_prompt_ids(language="ja", task="transcribe")
            generated_ids = model.generate(inputs.input_features, forced_decoder_ids=forced_decoder_ids)
            transcribed_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            transcriptions.append({
                'start': start_time,
                'end': end_time,
                'text': transcribed_text.strip()
            })
        except Exception as e:
            logging.exception(f"Ошибка при транскрипции сегмента с помощью Whisper [{start_time:.2f}s - {end_time:.2f}s]: {e}")
            transcriptions.append({
                'start': start_time,
                'end': end_time,
                'text': ''
            })
            
    return transcriptions
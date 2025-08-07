import datetime
from typing import List, Dict

def _format_srt_time(seconds: float) -> str:
    """
    Форматирует время из секунд в формат SRT: ЧЧ:ММ:СС,ммм.
    
    Args:
        seconds (float): Время в секундах.
        
    Returns:
        str: Отформатированная строка времени.
    """
    delta = datetime.timedelta(seconds=seconds)

    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = delta.microseconds // 1000
    
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def segments_to_srt(segments: List[Dict]) -> str:
    """
    Преобразует список сегментов в одну строку в формате SRT.

    Args:
        segments (List[Dict]): Список словарей, где каждый словарь
                               содержит ключи 'start', 'end' и 'text'.

    Returns:
        str: Содержимое SRT-файла в виде строки.
    """
    srt_blocks = []

    for i, segment in enumerate(segments, start=1):
        # Пропускаем сегменты без текста, чтобы не создавать пустые субтитры
        if not segment.get('text', '').strip():
            continue
            
        start_time = _format_srt_time(segment['start'])
        end_time = _format_srt_time(segment['end'])
        text = segment['text']
        
        block = f"{i}\n{start_time} --> {end_time}\n{text}\n"
        srt_blocks.append(block)
        
    return "\n".join(srt_blocks)
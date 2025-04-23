import re
import random

def process_beat(beat, alpha):
    """处理单个拍内的音符，以alpha概率删除每个音符"""
    if not beat.strip():
        return ''
    notes = beat.split('/')
    kept_notes = []
    for note in notes:
        if random.random() >= alpha:  # 保留概率为1-alpha
            kept_notes.append(note.strip())
    return '/'.join(kept_notes) if kept_notes else ''

def process_notes_part(notes_part, alpha):
    """处理音符部分（逗号分隔的多个拍）"""
    beats = notes_part.split(',')
    processed_beats = []
    for beat in beats:
        processed_beat = process_beat(beat, alpha)
        processed_beats.append(processed_beat)
    return ','.join(processed_beats)

def process_line(line, alpha):
    """处理单行乐谱"""
    # 正则匹配头部（BPM和分音标记）和音符部分
    pattern = re.compile(r'((?:\(\d+\.?\d*\)|\{\d+\})*)([^(){}]*)')
    segments = pattern.findall(line)
    processed_segments = []
    for head, notes_part in segments:
        processed_notes = process_notes_part(notes_part, alpha)
        processed_segments.append(head + processed_notes)
    return ''.join(processed_segments)

def random_delete(chart_lines, alpha):
    """主函数：随机删除乐谱中的音符"""
    processed_lines = []
    for line in chart_lines:
        processed_line = process_line(line.strip(), alpha)
        processed_lines.append(processed_line)
    return processed_lines
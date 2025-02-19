import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QPainter
from PyQt5.QtCore import Qt

# MIDI 数据解析
midi_data = {
    "metadata": {"bpm": 120, "ppq_resolution": 960},
    "type": "midi",
    "data": [
        {"pitch": 60, "end_ppq": 2744, "start_ppq": 0, "velocity": 127, "mute": False},
        {"pitch": 67, "end_ppq": 3659, "start_ppq": 2880, "velocity": 127, "mute": False},
        {"pitch": 65, "end_ppq": 6708, "start_ppq": 3840, "velocity": 127, "mute": False},
        {"pitch": 64, "end_ppq": 7703, "start_ppq": 6720, "velocity": 127, "mute": False},
        {"pitch": 60, "end_ppq": 10547, "start_ppq": 7680, "velocity": 127, "mute": False},
        {"pitch": 67, "end_ppq": 11338, "start_ppq": 10560, "velocity": 127, "mute": False},
        {"pitch": 65, "end_ppq": 14346, "start_ppq": 11520, "velocity": 127, "mute": False},
        {"pitch": 64, "end_ppq": 15360, "start_ppq": 14400, "velocity": 127, "mute": False},
    ]
}

# 画布参数
KEY_HEIGHT = 20  # 每个键的高度
NOTE_HEIGHT = 18  # 音符矩形高度
PPQ_SCALE = 0.1  # PPQ 缩放比例（用于时间轴）
BEAT_INTERVAL = midi_data["metadata"]["ppq_resolution"]  # 每节拍的 PPQ

# 获取音符范围
pitches = [note["pitch"] for note in midi_data["data"]]
min_pitch = min(pitches) - 2
max_pitch = max(pitches) + 2

class PianoRoll(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.draw_grid()
        self.draw_notes()
        self.setSceneRect(0, (127 - max_pitch) * KEY_HEIGHT, 1600, (max_pitch - min_pitch) * KEY_HEIGHT)
        self.scale(1.2, 1.2)  # 默认缩放

    def draw_grid(self):
        """绘制钢琴键背景网格，并标注 X 轴为节拍，Y 轴为音高"""
        for pitch in range(min_pitch, max_pitch + 1):
            y = (127 - pitch) * KEY_HEIGHT
            color = QColor(220, 220, 220) if pitch % 12 in [1, 3, 6, 8, 10] else QColor(240, 240, 240)
            self.scene.addRect(0, y, 1600, KEY_HEIGHT, QPen(Qt.NoPen), QBrush(color))
            
            text = QGraphicsTextItem(self.pitch_to_note_name(pitch))
            text.setFont(QFont("Arial", 10))
            text.setDefaultTextColor(Qt.black)
            text.setPos(-40, y + (KEY_HEIGHT - 10) / 2)
            self.scene.addItem(text)

        for beat in range(0, 1600, int(BEAT_INTERVAL * PPQ_SCALE)):
            self.scene.addLine(beat, (127 - max_pitch) * KEY_HEIGHT, beat, (127 - min_pitch) * KEY_HEIGHT, QPen(QColor(180, 180, 180), 1))
            
            text = QGraphicsTextItem(str(beat // int(BEAT_INTERVAL * PPQ_SCALE)))
            text.setFont(QFont("Arial", 10))
            text.setDefaultTextColor(Qt.black)
            text.setPos(beat, (127 - max_pitch) * KEY_HEIGHT - 20)
            self.scene.addItem(text)

    def draw_notes(self):
        """绘制 MIDI 音符，并标示音名"""
        colors = [QColor("#ff595e"), QColor("#ffca3a"), QColor("#8ac926"), QColor("#1982c4"), QColor("#6a4c93")]
        for note in midi_data["data"]:
            pitch = note["pitch"]
            start_x = note["start_ppq"] * PPQ_SCALE
            length = (note["end_ppq"] - note["start_ppq"]) * PPQ_SCALE
            y = (127 - pitch) * KEY_HEIGHT + (KEY_HEIGHT - NOTE_HEIGHT) / 2
            color = colors[pitch % len(colors)]
            rect = QGraphicsRectItem(start_x, y, length, NOTE_HEIGHT)
            rect.setBrush(QBrush(color))
            rect.setPen(QPen(Qt.black, 0.5))
            self.scene.addItem(rect)
            
            text = QGraphicsTextItem(self.pitch_to_note_name(pitch))
            text.setFont(QFont("Arial", 8))
            text.setDefaultTextColor(Qt.white)
            text.setPos(start_x + 2, y + 2)
            self.scene.addItem(text)
    
    def pitch_to_note_name(self, pitch):
        """将 MIDI 音高转换为音名"""
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (pitch // 12) - 1
        note = note_names[pitch % 12]
        return f"{note}{octave}"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PianoRoll()
    window.show()
    sys.exit(app.exec_())


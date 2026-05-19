import sys
import time
from enum import Enum
from threading import Thread, Event

class SpinnerStyle(Enum):
    """旋转动画样式"""
    CLASSIC = 1
    BRAILLE = 2
    ARROW = 3
    SIMPLE = 4

class MySpinner:
    # 你指定的顶级漂亮动画素材
    SPIN_FRAMES = {
        SpinnerStyle.CLASSIC: ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        SpinnerStyle.BRAILLE: ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'],
        SpinnerStyle.ARROW: ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        SpinnerStyle.SIMPLE: ['-', '\\', '|', '/']
    }

    def __init__(self, style: SpinnerStyle = SpinnerStyle.BRAILLE, defaultText: str = "正在处理中..."):
        self.style = style
        self.displayText = defaultText
        self._stop = Event()
        self._thread = None

    def setText(self, text: str):
        """随时修改显示文字"""
        self.displayText = text

    def _hideCursor(self):
        """隐藏光标"""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    def _showCursor(self):
        """显示光标"""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def _run(self):
        frames = self.SPIN_FRAMES[self.style]
        idx = 0
        self._hideCursor()  # 动画开始 → 隐藏光标
        
        while not self._stop.is_set():
            sys.stdout.write("\r\033[K")  # 清空整行，无残留
            char = frames[idx % len(frames)]
            sys.stdout.write(f"{char} {self.displayText}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)

    def start(self):
        """启动动画（非阻塞）"""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self,text:str|None=None,success:bool=True,showIcon:bool=True):
        """停止动画（非阻塞）"""
        self._stop.set()
        if self._thread:
            self._thread.join()
        sys.stdout.write("\r\033[K")
        self._showCursor()
        if text:
            if success:
                print(f"✅ {text}" if showIcon else f"{text}")
            else:
                print(f"❌ {text}" if showIcon else f"{text}")
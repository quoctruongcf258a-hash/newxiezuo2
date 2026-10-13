"""ruler_overlay.py — 程序二 窗口测量尺子叠加层。

透明叠加在 QMainWindow 之上，沿上/左边缘画刻度，并显示：
  · 窗口实时 宽×高（右下角读数）
  · 鼠标位置 (x, y)，用于测量任意子区域宽高（十字线）
鼠标对该层透明（不挡操作），由外部按钮切换显隐。
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PySide6.QtCore import Qt, QPoint, QRect


class RulerOverlay(QWidget):
    RULER = 22  # 刻度条厚度(px)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 鼠标对该层透明，不挡下面 dock / 中央的操作
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.cursor_pos = None
        self.measure_start = None  # 点选的起点(QPoint)，None 表示未选

    # ---- 外部调用：更新鼠标位置 ----
    def set_cursor(self, pos: QPoint):
        self.cursor_pos = pos
        self.update()

    def clear_cursor(self):
        self.cursor_pos = None
        self.update()

    # ---- 外部调用：点选 / 清除测量起点 ----
    def set_measure_start(self, pos: QPoint):
        self.measure_start = pos
        self.update()

    def clear_measure(self):
        self.measure_start = None
        self.update()

    def measure_rect(self):
        """返回 起点→光标 的 QRect（覆盖整窗坐标），无选区时返回 None。"""
        if self.measure_start is None or self.cursor_pos is None:
            return None
        return QRect(self.measure_start, self.cursor_pos).normalized()

    # ---- 绘制 ----
    def paintEvent(self, event):
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)

        bg = QColor(0, 0, 0, 60)
        tick_major = QColor(0, 229, 255)
        tick_minor = QColor(0, 229, 255, 160)
        tick_tiny = QColor(0, 229, 255, 90)

        # 上 / 左 刻度条底色
        p.fillRect(0, 0, w, self.RULER, bg)
        p.fillRect(0, 0, self.RULER, h, bg)

        font = QFont("Consolas", 8)
        p.setFont(font)
        fm = QFontMetrics(font)

        # 上边缘：横向刻度（每 10px 一细线，50px 中线，100px 标数字）
        x = 0
        while x <= w:
            if x % 100 == 0:
                p.setPen(QPen(tick_major, 1))
                p.drawLine(x, 0, x, self.RULER)
                p.drawText(x + 2, self.RULER - 4, str(x))
            elif x % 50 == 0:
                p.setPen(QPen(tick_minor, 1))
                p.drawLine(x, self.RULER - 10, x, self.RULER)
            else:
                p.setPen(QPen(tick_tiny, 1))
                p.drawLine(x, self.RULER - 5, x, self.RULER)
            x += 10

        # 左边缘：纵向刻度
        y = 0
        while y <= h:
            if y % 100 == 0:
                p.setPen(QPen(tick_major, 1))
                p.drawLine(0, y, self.RULER, y)
                p.drawText(4, y + fm.height() - 2, str(y))
            elif y % 50 == 0:
                p.setPen(QPen(tick_minor, 1))
                p.drawLine(0, y, self.RULER, y)
            else:
                p.setPen(QPen(tick_tiny, 1))
                p.drawLine(0, y, self.RULER - 5, y)
            y += 10

        # 实时窗口宽高读数（右下角）
        readout = f"宽 {w} px   高 {h} px"
        p.setFont(QFont("Consolas", 10))
        fm2 = QFontMetrics(p.font())
        rw = fm2.horizontalAdvance(readout) + 12
        rh = 18
        rx = w - rw - 4
        ry = h - rh - 4
        p.fillRect(rx, ry, rw, rh, QColor(20, 20, 20, 220))
        p.setPen(QColor(0, 229, 255))
        p.drawText(rx + 6, ry + 13, readout)

        # 鼠标十字线 + 坐标
        if self.cursor_pos is not None:
            cx, cy = self.cursor_pos.x(), self.cursor_pos.y()
            if 0 <= cx <= w and 0 <= cy <= h:
                cross = QColor(255, 214, 0, 190)
                p.setPen(QPen(cross, 1))
                p.drawLine(cx, 0, cx, h)
                p.drawLine(0, cy, w, cy)
                coord = f"x {cx}  y {cy}"
                p.setFont(QFont("Consolas", 9))
                fm3 = QFontMetrics(p.font())
                cw = fm3.horizontalAdvance(coord) + 10
                ch = 16
                bx = min(cx + 8, w - cw - 2)
                by = min(cy + 8, h - ch - 2)
                p.fillRect(bx, by, cw, ch, QColor(20, 20, 20, 220))
                p.setPen(QColor(255, 214, 0))
                p.drawText(bx + 5, by + 12, coord)

        # 测量：从点选起点到当前鼠标的 矩形 + 斜边 + 读数
        if self.measure_start is not None and self.cursor_pos is not None:
            sx, sy = self.measure_start.x(), self.measure_start.y()
            ex, ey = self.cursor_pos.x(), self.cursor_pos.y()
            if 0 <= sx <= w and 0 <= sy <= h and 0 <= ex <= w and 0 <= ey <= h:
                meas = QColor(0, 255, 140, 220)
                p.setPen(QPen(meas, 1))
                # 起点标记
                p.drawLine(sx - 4, sy, sx + 4, sy)
                p.drawLine(sx, sy - 4, sx, sy + 4)
                # 外接矩形（只描上/右/下/左四边，避开刻度条遮挡）
                rx0, ry0 = min(sx, ex), min(sy, ey)
                rx1, ry1 = max(sx, ex), max(sy, ey)
                p.drawRect(rx0, ry0, rx1 - rx0, ry1 - ry0)
                # 起点→鼠标的斜边
                p.setPen(QPen(meas, 1, Qt.DashLine))
                p.drawLine(sx, sy, ex, ey)
                # 读数
                dx = abs(ex - sx)
                dy = abs(ey - sy)
                dist = int(((ex - sx) ** 2 + (ey - sy) ** 2) ** 0.5)
                label = f"起点 {sx},{sy}   Δ宽 {dx} × Δ高 {dy}   斜边 {dist} px"
                p.setFont(QFont("Consolas", 9))
                fm4 = QFontMetrics(p.font())
                mw = fm4.horizontalAdvance(label) + 10
                mh = 16
                mx = min(ex + 8, w - mw - 2)
                my = max(0, min(ey - 20, h - mh - 2))
                p.fillRect(mx, my, mw, mh, QColor(0, 40, 20, 230))
                p.setPen(QColor(0, 255, 140))
                p.drawText(mx + 5, my + 12, label)

        p.end()

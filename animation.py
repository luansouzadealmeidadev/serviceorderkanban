from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

def fade_in(widget, duration=300):
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.setEasingCurve(QEasingCurve.OutQuad)
    animation.start()

def fade_out(widget, duration=300):
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(1)
    animation.setEndValue(0)
    animation.setEasingCurve(QEasingCurve.OutQuad)
    animation.start()
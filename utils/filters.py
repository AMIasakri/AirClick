"""
فیلترهای نرم‌سازی حرکت
"""


class ExponentialMovingAverage:
    def __init__(self, alpha=0.6):
        self.alpha = alpha
        self.value = None
        self.initialized = False
    
    def update(self, new_value):
        if not self.initialized:
            self.value = new_value
            self.initialized = True
        else:
            self.value = self.alpha * new_value + (1 - self.alpha) * self.value
        return self.value
    
    def reset(self):
        self.value = None
        self.initialized = False
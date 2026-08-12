"""
فیلترهای نرم‌سازی و پردازش سیگنال برای حرکت روان موس
"""

import numpy as np
from collections import deque


class ExponentialMovingAverage:
    """
    فیلتر میانگین متحرک نمایی (EMA)
    برای نرم‌سازی حرکت موس با تأخیر کم
    """
    
    def __init__(self, alpha=0.6):
        """
        Args:
            alpha: ضریب نرم‌سازی (0.0 تا 1.0)
                  عدد بیشتر = نرم‌تر ولی با تأخیر بیشتر
        """
        self.alpha = alpha
        self.value = None
        self.initialized = False
    
    def update(self, new_value):
        """
        به‌روزرسانی فیلتر با مقدار جدید
        
        Args:
            new_value: مقدار جدید
        
        Returns:
            float: مقدار نرم‌سازی شده
        """
        if not self.initialized:
            self.value = new_value
            self.initialized = True
        else:
            self.value = self.alpha * new_value + (1 - self.alpha) * self.value
        
        return self.value
    
    def reset(self):
        """بازنشانی فیلتر"""
        self.value = None
        self.initialized = False


class MovingAverageFilter:
    """
    فیلتر میانگین متحرک ساده
    برای نرم‌سازی با پنجره‌ی مشخص
    """
    
    def __init__(self, window_size=5):
        """
        Args:
            window_size: اندازه‌ی پنجره (تعداد فریم‌ها)
        """
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
    
    def update(self, new_value):
        """
        به‌روزرسانی فیلتر با مقدار جدید
        
        Args:
            new_value: مقدار جدید
        
        Returns:
            float: مقدار نرم‌سازی شده
        """
        self.values.append(new_value)
        return np.mean(self.values)
    
    def reset(self):
        """بازنشانی فیلتر"""
        self.values.clear()


class KalmanFilter1D:
    """
    فیلتر کالمن یک‌بعدی ساده
    برای پیش‌بینی و نرم‌سازی حرکت
    """
    
    def __init__(self, process_noise=0.1, measurement_noise=0.1):
        """
        Args:
            process_noise: نویز فرآیند (پیش‌بینی)
            measurement_noise: نویز اندازه‌گیری
        """
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.estimate = 0
        self.estimate_error = 1
        self.initialized = False
    
    def update(self, measurement):
        """
        به‌روزرسانی فیلتر با اندازه‌گیری جدید
        
        Args:
            measurement: مقدار اندازه‌گیری شده
        
        Returns:
            float: مقدار تخمین زده شده
        """
        if not self.initialized:
            self.estimate = measurement
            self.initialized = True
            return measurement
        
        # پیش‌بینی
        self.estimate_error += self.process_noise
        
        # به‌روزرسانی
        kalman_gain = self.estimate_error / (self.estimate_error + self.measurement_noise)
        self.estimate = self.estimate + kalman_gain * (measurement - self.estimate)
        self.estimate_error = (1 - kalman_gain) * self.estimate_error
        
        return self.estimate
    
    def reset(self):
        """بازنشانی فیلتر"""
        self.estimate = 0
        self.estimate_error = 1
        self.initialized = False


class DualFilter:
    """
    فیلتر دوگانه برای نرم‌سازی همزمان x و y
    """
    
    def __init__(self, filter_type='ema', alpha=0.6, window_size=5):
        """
        Args:
            filter_type: نوع فیلتر ('ema', 'moving_average', 'kalman')
            alpha: ضریب نرم‌سازی (برای EMA)
            window_size: اندازه‌ی پنجره (برای Moving Average)
        """
        self.filter_type = filter_type
        self.x_filter = self._create_filter()
        self.y_filter = self._create_filter()
        self.alpha = alpha
        self.window_size = window_size
    
    def _create_filter(self):
        """ایجاد یک فیلتر جدید بر اساس نوع"""
        if self.filter_type == 'ema':
            return ExponentialMovingAverage(self.alpha)
        elif self.filter_type == 'moving_average':
            return MovingAverageFilter(self.window_size)
        elif self.filter_type == 'kalman':
            return KalmanFilter1D()
        else:
            return ExponentialMovingAverage(self.alpha)
    
    def update(self, x, y):
        """
        به‌روزرسانی فیلتر با مختصات جدید
        
        Args:
            x: مختصات x
            y: مختصات y
        
        Returns:
            tuple: (smoothed_x, smoothed_y)
        """
        smoothed_x = self.x_filter.update(x)
        smoothed_y = self.y_filter.update(y)
        return smoothed_x, smoothed_y
    
    def reset(self):
        """بازنشانی فیلترها"""
        self.x_filter.reset()
        self.y_filter.reset()
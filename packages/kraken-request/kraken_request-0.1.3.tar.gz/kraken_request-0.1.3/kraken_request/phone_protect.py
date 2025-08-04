import re

class PhoneProtector:
    """Класс для защиты телефонных номеров"""
    def __init__(self, phone_number):
        self.original_number = phone_number
        self.sanitized = self._sanitize(phone_number)
    
    def _sanitize(self, number):
        """Очистка номера от спецсимволов"""
        return re.sub(r'[^0-9+]', '', number)
    
    def masked(self, visible=3):
        """Маскировка номера"""
        if len(self.sanitized) <= visible:
            return self.sanitized
        return '*' * (len(self.sanitized) - visible) + self.sanitized[-visible:]
    
    def get_info(self):
        """Информация о номере (заглушка)"""
        return {
            "number": self.masked(),
            "country": "Unknown",
            "carrier": "Hidden"
        }

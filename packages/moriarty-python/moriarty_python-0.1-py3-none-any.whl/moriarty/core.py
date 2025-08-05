import socket
import logging
from .encryption import QuantumEncryptor
from .proxy_chain import HydraProxyNetwork
from .forensic import ZeroFootprint

class MoriartyEngine:
    def __init__(self, threat_level="HIGH", auto_wipe=True):
        self.encryptor = QuantumEncryptor()
        self.proxy_net = HydraProxyNetwork(threat_level)
        self.forensic = ZeroFootprint(auto_wipe=auto_wipe)
        self.session_id = self.encryptor.generate_session_id()
        logging.basicConfig(level=logging.CRITICAL)  # Отключаем логирование
        
    def start_session(self):
        """Инициализация защищенной сессии"""
        self.proxy_net.initialize_chain()
        self.forensic.prepare_environment()
        return MoriartySession(self)
    
    def terminate(self):
        """Экстренное завершение с очисткой следов"""
        self.forensic.emergency_cleanup()

class MoriartySession:
    def __init__(self, engine):
        self.engine = engine
        self.sock = None
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def connect(self, host, port):
        """Установка защищенного соединения"""
        entry_node = self.engine.proxy_net.get_entry_point()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(entry_node)
        return self.sock
        
    def send(self, data):
        """Отправка зашифрованных данных"""
        encrypted = self.engine.encryptor.encrypt(data)
        morphed = self.engine.proxy_net.morph_packet(encrypted)
        self.sock.sendall(morphed)
        
    def recv(self, buffer_size=4096):
        """Прием и расшифровка данных"""
        data = self.sock.recv(buffer_size)
        decrypted = self.engine.encryptor.decrypt(data)
        return decrypted
        
    def close(self):
        """Безопасное закрытие соединения"""
        if self.sock:
            self.sock.close()
        self.engine.forensic.cleanup()

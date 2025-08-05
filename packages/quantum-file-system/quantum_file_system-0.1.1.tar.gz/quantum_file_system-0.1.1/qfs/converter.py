
"""
Quantum converter module for backward compatibility and simplified interface.
"""

from .quantum_cipher import QuantumJSONConverter

class QuantumConverter(QuantumJSONConverter):
    """Quantum-inspired encryption converter with custom algorithms"""
    
    def __init__(self, auth_key):
        """Initialize converter with authorization key"""
        super().__init__(auth_key)
    
    def convert_json_to_qjson(self, json_content):
        """Convert JSON content to QJSON format"""
        return self.encrypt_json(json_content)
    
    def convert_qjson_to_json(self, qjson_content):
        """Convert QJSON content back to JSON format"""
        return self.decrypt_qjson(qjson_content)

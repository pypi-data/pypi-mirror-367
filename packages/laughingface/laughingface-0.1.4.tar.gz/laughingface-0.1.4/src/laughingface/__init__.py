from .core import init, list_modules, module, LaughingFaceModule

class LaughingFace:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def init(self):
        init(self.api_key)
    
    def list_modules(self):
        return list_modules()
    
    def module(self, module_name: str):
        return module(module_name)

__all__ = ['LaughingFace', 'init', 'list_modules', 'module', 'LaughingFaceModule']
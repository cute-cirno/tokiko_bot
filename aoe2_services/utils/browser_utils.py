from playwright.async_api import Browser, async_playwright
from typing import Optional
import asyncio

class Aoe2Browser:
    _instance: Optional['Aoe2Browser'] = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if not cls._instance:
            raise RuntimeError("Browser is not initialized. Please call Aoe2Browser.init() first.")
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '__initialized'):
            raise RuntimeError("Please use Aoe2Browser.init() to create an instance of Aoe2Browser.")
    
    @classmethod
    async def init(cls, **kwargs) -> 'Aoe2Browser':
        """
        Initializes the browser instance with the given kwargs. The kwargs are passed to the launch() method of the browser.
        """
        async with cls._lock:
            if not cls._instance:
                instance = super(Aoe2Browser, cls).__new__(cls)
                await instance._async_init(**kwargs)
                cls._instance = instance
            return cls._instance
                
    
    async def _async_init(self,**kwargs):
        """
        Initializes the browser istance with kwargs. The kwargs are passed to the launch() method of the browser.
        """
        self._initialized = True
        browser = await async_playwright().start()
        self.browser: Optional[Browser] = await browser.chromium.launch(**kwargs)
    
    async def get_browser(self) -> Browser:
        """
        Retrieves the single instance of the browser. Ensures the browser is initialized.

        Returns:
            Browser: The single instance of the browser.

        Raises:
            RuntimeError: If the browser instance is not initialized.
        """
        if not self.browser:
            raise RuntimeError("Browser is not initialized. Please call Aoe2Browser.init() first.")
        return self.browser

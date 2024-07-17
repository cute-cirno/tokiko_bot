import asyncio
import aiofiles
from collections import OrderedDict
from typing import Optional,ClassVar,Union



class CachedFileReader:
    _instance: Optional["CachedFileReader"] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            raise RuntimeError(
                "This class must be instantiated using 'await CachedFileReader.create()'"
            )
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            raise RuntimeError(
                "This class must be initialized using 'await CachedFileReader.create()'"
            )

    @classmethod
    async def create(cls, max_chache_size: int = 10) -> "CachedFileReader":
        """
        Returns a singleton instance of the CachedFileReader with thread safety ensured by an asyncio.Lock.
        """
        async with cls._lock:
            if cls._instance is None:
                instance = super(CachedFileReader, cls).__new__(cls)
                await instance._async_init(max_chache_size)
                cls._instance = instance
        return cls._instance

    async def _async_init(self, max_chache_size: int):
        self.cache: OrderedDict = OrderedDict()
        self._initialized = True
        self.max_chache_size = max_chache_size

    

    async def read_file(self, file_path: str, binary_mode: bool = False) -> Union[str, bytes]:
        """
        Asynchronously reads a file's content with caching, using LRU eviction policy.
        Can read in binary mode for files that need to be processed as binary data.

        :param file_path: Path to the file to be read.
        :param binary_mode: Boolean indicating whether to read the file as binary.
        :return: The content of the file as either a string or bytes, depending on the binary_mode.
        """
        if file_path in self.cache:
            self.cache.move_to_end(file_path)
            return self.cache[file_path]

        if binary_mode:
            mode = 'rb'
            async with aiofiles.open(file_path, mode=mode) as file:
                content = await file.read()
        else:
            mode = 'r'
            async with aiofiles.open(file_path, mode=mode, encoding='utf-8') as file:
                content = await file.read()

        if len(self.cache) >= self.max_chache_size:
            self.cache.popitem(last=False)
        self.cache[file_path] = content
        self.cache.move_to_end(file_path)
        return content

    
    def clear_cache(self):
        """
        Clears the cache.
        """
        self.cache.clear()
        
    def remove_from_cache(self, file_path: str):
        """
        Removes a specific file's content from the cache.
        
        :param file_path: Path to the file whose cache should be cleared.
        """
        if file_path in self.cache:
            self.cache.pop(file_path)



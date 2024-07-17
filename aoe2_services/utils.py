import base64
import aiofiles
import json
from collections import OrderedDict
import asyncio
from typing import Optional,ClassVar,Union,Dict,List,Any



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


class Utils:
    @staticmethod
    async def imagefile_to_base64(image_path: str) -> str:
        """
        Asynchronously reads an image file, encodes it to Base64, and returns the encoded string.
        
        :param image_path: The path to the image file to be read and encoded.
        :return: A Base64 encoded string of the image.
        :raises ValueError: If the read data is not in bytes format.
        """
        # Ensure the CachedFileReader is instantiated and used correctly
        cache = await CachedFileReader.create()
        image_data = await cache.read_file(image_path, binary_mode=True)

        # Check if the read data is in bytes, which is necessary for base64 encoding
        if isinstance(image_data, bytes):
            base64_data = base64.b64encode(image_data)
            return base64_data.decode("utf-8")
        else:
            # Raise an error if the data is not in the expected format
            raise ValueError("Expected bytes data for base64 encoding, got different format.")


    @staticmethod
    async def load_json_file(file_path: str) -> Union[Dict[Any, Any], List[Any]]:
        """
        Asynchronously loads a JSON file and returns its content as either a dictionary or a list,
        depending on the top-level JSON element.
        
        :param file_path: The path to the JSON file to be read.
        :return: A dictionary or list representing the JSON file's content.
        """
        # Ensure the CachedFileReader is created with text mode enabled
        cache = await CachedFileReader.create()
        content = await cache.read_file(file_path, binary_mode=False)
        
        try:
            # Attempt to parse the JSON content
            json_data = json.loads(content)
            return json_data
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            raise ValueError(f"Failed to decode JSON from {file_path}: {e}")
        except Exception as e:
            # Handle other exceptions, such as issues with file reading
            raise IOError(f"Failed to read or process {file_path}: {e}")
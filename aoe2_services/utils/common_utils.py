import json
import base64
from typing import Any, Dict
from .cache_utils import CachedFileReader
from functools import wraps
from collections import OrderedDict

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
        return image_to_base64(image_data)
    else:
        # Raise an error if the data is not in the expected format
        raise ValueError("Expected bytes data for base64 encoding, got different format.")


async def load_json_file(file_path: str) ->Dict[str, Any]:
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
        if isinstance(json_data, dict):
            return json_data
        else:
            raise ValueError(f"Expected top-level JSON element to be a dictionary, got {type(json_data).__name__}.")
    except json.JSONDecodeError as e:
        # Handle JSON decoding errors
        raise ValueError(f"Failed to decode JSON from {file_path}: {e}")
    except Exception as e:
        # Handle other exceptions, such as issues with file reading
        raise IOError(f"Failed to read or process {file_path}: {e}")
    
def image_to_base64(image_data: bytes) -> str:
    """
    Encodes an image to Base64 and returns the encoded string.
    """
    base64_data = base64.b64encode(image_data)
    return "base64://" + base64_data.decode("utf-8")


def async_lru_cache(maxsize=20):
    def decorator(func):
        cache = OrderedDict()

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 使用参数构建一个键
            key = args + tuple(kwargs.items())
            # 如果缓存中已有这个键，将其移到字典末尾表示最近使用
            if key in cache:
                cache.move_to_end(key)
                return cache[key]
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            # 添加新的结果到缓存，若缓存已满，移除最早的条目
            cache[key] = result
            if len(cache) > maxsize:
                cache.popitem(last=False)
            return result
        return wrapper
    return decorator


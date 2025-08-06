from typing import Any,AsyncGenerator
from ..utility import ModelConfig
from abc import ABC,abstractmethod
from enum import Enum
class StreamDataStatus(Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"
class DataPackage:
    def __init__(self,status:StreamDataStatus,data:Any,usage:dict[str,Any]|None=None):
        self._status = status
        if self._status == StreamDataStatus.GENERATING:
            self._data = {"data":data}
        elif self._status == StreamDataStatus.COMPLETED:
            self._data = {"full_data":data,"usage":usage}
        elif self._status == StreamDataStatus.ERROR:
            self._data = data

    def to_dict(self)->dict[str,Any]:
        return {
            "status":self._status.value,
            "data":self._data
        }
    def read_data(self) -> Any:
        return self._data.get("data") or self._data.get("full_data") or self._data
    def get_status(self)->StreamDataStatus:
        return self._status
    def get_usage(self)->dict[str,Any]:
        return self._data.get("usage") or {}
class BaseProcessor(ABC):
    _api_key:str
    _base_url:str
    _proxy:str
    _llm_config:ModelConfig
    def __init__(self):
        self._api_key = None
        self._base_url = None
        self._proxy = None
        self._llm_config = None
    @abstractmethod
    async def interact(self,messages:dict[str,str], llm_config: ModelConfig,proxy:str,api_key:str,base_url:str)->AsyncGenerator[DataPackage,None]:
        ...
    def get_headers(self)->dict[str,Any]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
    @abstractmethod
    def get_payload(self,messages:Any)->dict[str,Any]:
        ...
    @abstractmethod
    def get_chat_url(self)->str:
        ...
    @abstractmethod
    def parse_stream_chunk(self,chunk_data:dict[str,Any])->str:
        ...
    @abstractmethod
    def get_usage(self,last_chunk_data:dict[str,Any],messages:dict[str,str],model_output:Any)->dict[str,Any]:
        ...
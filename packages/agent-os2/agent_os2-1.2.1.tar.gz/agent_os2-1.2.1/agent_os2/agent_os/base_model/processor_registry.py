from itertools import accumulate
from typing import Type,Any,AsyncGenerator,TYPE_CHECKING
from .model_processor import BaseProcessor,DataPackage,StreamDataStatus
import aiohttp
import json
import os
import asyncio
import time
import uuid
import io
import base64
from datetime import datetime
from google.genai import types,Client
from PIL import Image
from .utility import get_model_cost,get_fallback_tokens
if TYPE_CHECKING:
    from ..base_agent import LLMConfig,ImageConfig
# 模型注册表
TYPE_MAPPINGS: dict[str, Type[BaseProcessor]] = {}

def register(*processor_types: str):
    def decorator(cls: Type[BaseProcessor]):
        for processor_type in processor_types:
            if processor_type in TYPE_MAPPINGS:
                raise ValueError(f"模型类型 '{processor_type}' 已注册")
            TYPE_MAPPINGS[processor_type] = cls
        return cls
    return decorator
def process_messages_to_openai_style(messages:list[dict[str,str]]|str|dict[str,str])->list[dict[str, str]]:
    processed_messages = []
    if isinstance(messages, str):
        processed_messages.append({"role":"user","content":messages})
    elif isinstance(messages,dict):
        if "system" in messages:
            processed_messages.append({"role":"system","content":messages["system"]})
        if "user" in messages:
            processed_messages.append({"role":"user","content":messages["user"]})
        if "assistant" in messages:
            processed_messages.append({"role":"assistant","content":messages["assistant"]})
    elif isinstance(messages,list):
        for message in messages:
            if isinstance(message,dict):
                if "system" in message:
                    processed_messages.append({"role":"system","content":message["system"]})
                elif "user" in message:
                    processed_messages.append({"role":"user","content":message["user"]})
                elif "assistant" in message:
                    processed_messages.append({"role":"assistant","content":message["assistant"]})
            else:
                raise ValueError(f"messages中的元素必须是dict，当前message: {message}")
    return processed_messages
@register("google-none-thinking-chat")
class GoogleStyleNoneThinkingProcessor(BaseProcessor):
    @staticmethod
    def process_messages(messages:list[dict[str,str]]|str|dict[str,str])->list[dict[str, str]]:
        processed_messages = process_messages_to_openai_style(messages)
        contents = []
        for message in processed_messages:
            if message['role'] == 'system':
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=message['content'])]
                ))
            elif message['role'] == 'user':
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=message['content'])]
                ))
            elif message['role'] == 'assistant':
                contents.append(types.Content(
                    role="model",
                    parts=[types.Part(text=message['content'])]
                ))
        return contents
    async def interact(self, messages:dict[str,str], llm_config: "LLMConfig",proxy:str,api_key:str,base_url:str)->AsyncGenerator[DataPackage,None]:
        self._llm_config = llm_config
        self._api_key = api_key
        self._base_url = base_url
        self._proxy = proxy
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = Client(api_key=api_key)
        processed_messages = self.process_messages(messages)
        model_name = llm_config.get_model_name()
        if model_name.startswith("none_thinking/"):
            model_name = model_name.split("/")[1]
        if model_name == "gemini-2.5-pro":
            print("警告，gemini-2.5-pro无法停止思考，建议语义更加清晰的处理器")
        
        # 在线程池中运行同步生成器
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        
        def _generate():
            """同步生成器函数"""
            try:
                response = client.models.generate_content_stream(
                    model=model_name,
                    contents=processed_messages,
                    config=self.get_payload(messages)
                )
                accumulated_text = ""
                last_chunk = None
                for chunk in response:
                    last_chunk = chunk
                    text = self.parse_stream_chunk(chunk)
                    accumulated_text += text
                    yield ("chunk", text)
                yield ("complete", accumulated_text, last_chunk)
            except Exception as e:
                yield ("error", str(e))
        
        # 将同步生成器转换为异步生成器
        try:
            gen = _generate()
            while True:
                result = await loop.run_in_executor(executor, next, gen, None)
                if result is None:
                    break
                    
                if result[0] == "chunk":
                    yield DataPackage(StreamDataStatus.GENERATING, data=result[1])
                elif result[0] == "complete":
                    yield DataPackage(StreamDataStatus.COMPLETED, 
                                    data=result[1], 
                                    usage=self.get_usage(result[2], messages, result[1]))
                elif result[0] == "error":
                    yield DataPackage(StreamDataStatus.ERROR, data={
                        "code": 500,
                        "message": result[1],
                        "detail": f"{self.__class__.__name__} 请求失败"
                    })
                    break
        finally:
            executor.shutdown(wait=False)
    def get_usage(self,last_chunk_data:"types.GenerateContentResponse",messages:list[dict[str,str]],model_output:Any)->dict[str,Any]:
        return {
            "prompt_tokens": last_chunk_data.usage_metadata.prompt_token_count,
            "completion_tokens": last_chunk_data.usage_metadata.candidates_token_count,
            "total_tokens": last_chunk_data.usage_metadata.total_token_count,
            "cost": get_model_cost(self._llm_config.get_model_name().split("/")[1] if self._llm_config.get_model_name().startswith("none_thinking/") else self._llm_config.get_model_name()
            ,last_chunk_data.usage_metadata.prompt_token_count,last_chunk_data.usage_metadata.candidates_token_count)
        }
    def get_payload(self, messages: Any) -> "types.GenerateContentRequest":
        config = self._llm_config.get_interact_config().copy()
        max_tokens = config.pop("max_tokens", 65535)
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=0 #关闭思考
            ),
            max_output_tokens = max_tokens,
            **config
        )
        return generate_content_config
    def get_chat_url(self) -> str:
        pass
    def parse_stream_chunk(self, chunk_data) -> str:
        if chunk_data.text:
            return chunk_data.text
@register("openai-style-chat")
class OpenAIStyleChatProcessor(BaseProcessor):
    _llm_config:"LLMConfig"
    def get_usage(self,last_chunk_data:dict[str,Any],messages:list[dict[str,str]],model_output:Any)->dict[str,Any]:
        model_name = self._llm_config.get_model_name()
        # OpenAI风格聊天模型，为prompt添加消息格式开销，为completion添加assistant回复开销
        prompt_tokens = last_chunk_data.get("usage", {}).get("prompt_tokens", get_fallback_tokens(*(message['content'] for message in messages), model=model_name, initial_tokens=3))
        completion_tokens = last_chunk_data.get("usage", {}).get("completion_tokens", get_fallback_tokens(model_output, model=model_name, initial_tokens=3))
        total_tokens = last_chunk_data.get("usage", {}).get("total_tokens", prompt_tokens + completion_tokens)
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": get_model_cost(model_name,prompt_tokens,completion_tokens)
        }
    async def interact(self, messages: str|list[dict[str,str]]|dict[str,str], llm_config: "LLMConfig",proxy:str,api_key:str,base_url:str)->AsyncGenerator[DataPackage,None]:
        self._llm_config = llm_config
        self._api_key = api_key
        self._base_url = base_url
        self._proxy = proxy
        messages = process_messages_to_openai_style(messages)
        headers = self.get_headers()
        payload = self.get_payload(messages)
        url = self.get_chat_url()
        generated_content = ""
        last_chunk_data: dict[str, Any] = {}

        try:
            session_kwargs = {}
            if self._proxy:
                session_kwargs["proxy"] = self._proxy

            if not self._base_url:
                raise ValueError("api_url 不能为空！请检查 llm_key.json 配置和模型名到平台的映射关系。")

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(url, headers=headers, json=payload, **session_kwargs) as response:
                        if response.status != 200:
                            error = await response.text()
                            yield DataPackage(StreamDataStatus.ERROR,data={
                                "code": response.status,
                                "message": error,
                                "detail": f"{self.__class__.__name__} 请求失败"
                            })
                            return

                        async for line in response.content:
                            chunk = line.decode("utf-8").strip()
                            if chunk.startswith("data: "):
                                chunk = chunk[len("data: "):]
                            if chunk and chunk != "[DONE]":
                                try:
                                    chunk_data = json.loads(chunk)
                                    last_chunk_data = chunk_data
                                    content = self.parse_stream_chunk(chunk_data)
                                    if content:
                                        generated_content += content
                                        if llm_config.is_stream():
                                            yield DataPackage(StreamDataStatus.GENERATING,data=content)
                                except Exception as e:
                                    print(f"{self.__class__.__name__} 流式解析失败: {str(e)}，chunk内容: {chunk[:200]}")

                except aiohttp.ClientError as net_exc:
                    # 网络级错误，如连接失败、超时等
                    yield DataPackage(StreamDataStatus.ERROR,data={
                        "code":500,
                        "message": str(net_exc),
                        "detail": f"{self.__class__.__name__} 发出请求时出现网络异常",
                    })
                    return
            # 使用get_usage方法计算完整的usage信息
            usage_info = self.get_usage(last_chunk_data, messages, generated_content)
            yield DataPackage(StreamDataStatus.COMPLETED,data=generated_content,usage=usage_info)

        except Exception as logic_error:
            # 代码逻辑错误应继续抛出（开发时立刻暴露）
            raise  # 不 yield，直接抛出

    def get_payload(self, messages):
        return {
            "model": self._llm_config.get_model_name(),
            "messages": messages,
            **self._llm_config.get_interact_config(),
            "stream": True
        }

    def get_chat_url(self):
        base_url = self._base_url
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        if base_url.endswith("/chat/completions"):
            return base_url
        return f"{base_url}/chat/completions"

    def parse_stream_chunk(self, chunk_data)->str:
        # 默认openai兼容
        if ('choices' in chunk_data and 
            len(chunk_data['choices']) > 0 and 
            'delta' in chunk_data['choices'][0]):
            delta = chunk_data['choices'][0]['delta']
            return delta.get('content', '')
        return ""

# 图片模型保留自定义实现
@register("openai-style-image-generate")
class OpenAIStyleImageProcessor(BaseProcessor):
    _llm_config:"ImageConfig"
    def get_usage(self,last_chunk_data:dict[str,Any],messages:str,model_output:Any)->dict[str,Any]:
        model_name = self._llm_config.get_model_name()
        # 图片生成模型：prompt正常计算，completion添加大量预估开销（图片数据+metadata）
        prompt_tokens = last_chunk_data.get("usage", {}).get("prompt_tokens", get_fallback_tokens(messages, model=model_name))
        completion_tokens = last_chunk_data.get("usage", {}).get("completion_tokens", get_fallback_tokens(str(model_output), model=model_name, initial_tokens=200))  # 为图片输出添加200token的保守预估
        total_tokens = last_chunk_data.get("usage", {}).get("total_tokens", prompt_tokens + completion_tokens)
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": get_model_cost(model_name,prompt_tokens,completion_tokens)
        }
    async def interact(self, messages:str, image_config: "ImageConfig",proxy:str,api_key:str,base_url:str):
        self._llm_config = image_config
        self._api_key = api_key
        self._base_url = base_url
        self._proxy = proxy
        memory_folder = os.path.join(os.getcwd(), "memory","pic_lib")
        os.makedirs(memory_folder, exist_ok=True)
        headers = self.get_headers()
        payload = self.get_payload(messages)
        try:
            session_kwargs = {}
            if self._proxy:
                session_kwargs["proxy"] = self._proxy
            if not self._base_url:
                raise ValueError("api_url 不能为空！请检查 llm_key.json 配置和模型名到平台的映射关系。")
            async with aiohttp.ClientSession() as session:
                async with session.post(self.get_chat_url(), headers=headers, json=payload, **session_kwargs) as response:
                    if response.status != 200:
                        error = await response.text()
                        yield DataPackage(StreamDataStatus.ERROR,data={
                            "code": response.status,
                            "message": error,
                            "detail": f"gpt-image-1图片生成失败"
                        })
                    response_data = await response.json()
                    results = []
                    for item in response_data.get("data", []):
                        if "b64_json" in item:
                            image_info = self.save_image_from_base64(item["b64_json"], memory_folder)
                            results.append(image_info)
                        if image_config.is_stream():
                            yield DataPackage(StreamDataStatus.GENERATING,data=item)
                    # 使用get_usage方法计算完整的usage信息
                    usage_info = self.get_usage(response_data, messages, results)
                    yield DataPackage(StreamDataStatus.COMPLETED,data=results,usage=usage_info)
        except Exception as e:
            raise  # 直接上抛异常，包含错误码
    
    def get_payload(self, messages:Any):
        return {
            "model": self._llm_config.get_model_name(),
            "prompt": messages,
            "n": 1,
            "size": self._llm_config.get_size(),
            "quality": self._llm_config.get_quality(),
            "background": self._llm_config.get_background(),
            "response_format": "b64_json"
        }

    def get_chat_url(self):
        """图像模型不使用聊天URL，此方法仅满足抽象类要求"""
        return f"{self._base_url}/images/generations"

    def parse_stream_chunk(self, chunk_data: dict[str, Any]):
        """图像模型不支持流式解析，此方法仅满足抽象类要求"""
        return ""

    @staticmethod
    def save_image_from_base64(b64_data, memory_folder, mime_type="image/png"):
        image_id = f"gpt_image_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        extension = "png"
        if "jpeg" in mime_type or "jpg" in mime_type:
            extension = "jpg"
        filename = f"{image_id}.{extension}"
        save_path = os.path.join(memory_folder, filename)
        image_bytes = base64.b64decode(b64_data)
        image = Image.open(io.BytesIO(image_bytes))
        image.save(save_path)
        return {
            "b64_json": b64_data,
            "image_id": image_id,
            "path": save_path,
            "relative_path": os.path.relpath(save_path,os.getcwd()),
            "mime_type": mime_type,
            "created_at": datetime.now().isoformat()
        }

@register("flux-image-generate")
class FluxProcessor(BaseProcessor):
    _llm_config:"ImageConfig"
    def get_usage(self,last_chunk_data:dict[str,Any],messages:str,model_output:Any)->dict[str,Any]:
        return {
            "cost": 0.02
        }
    async def interact(self, messages:str, image_config: "ImageConfig",proxy:str,api_key:str,base_url:str):
        self._llm_config = image_config
        self._api_key = api_key
        self._base_url = base_url
        self._proxy = proxy
        headers = self.get_headers()
        payload = self.get_payload(messages)
        try:
            async with aiohttp.ClientSession() as session:
                # 第一次请求以获取请求ID和轮询URL
                async with session.post(self.get_chat_url(), headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield DataPackage(StreamDataStatus.ERROR,data={
                            "code": response.status,
                            "message": error_text,
                            "detail": f"flux 图片生成失败"
                        })
                        return

                    response_data = await response.json()
                    if not response_data:
                        yield DataPackage(StreamDataStatus.ERROR,data={
                            "code": response.status,
                            "message": "未能获取有效的响应数据",
                            "detail": "未能获取有效的响应数据"
                        })
                        return

                    polling_url = response_data.get("polling_url")
                    request_id = response_data.get("id")

                    if not polling_url:
                        yield DataPackage(StreamDataStatus.ERROR,data={
                            "code": response.status,
                            "message": "未能获取轮询URL",
                            "detail": "未能获取轮询URL"
                        })
                        return

                    params = {
                        'id': request_id,
                    }

                    # 第二次请求以获取图片URL
                    while True:
                        await asyncio.sleep(0.5) # 使用 asyncio.sleep
                        async with session.get(polling_url, headers=headers, params=params) as polling_response:
                            if polling_response.status != 200:
                                polling_error_text = await polling_response.text()
                                yield DataPackage(StreamDataStatus.ERROR,data={
                                    "code": polling_response.status,
                                    "message": polling_error_text,
                                    "detail": f"轮询请求失败"
                                })
                                return

                            polling_data = await polling_response.json()
                            status = polling_data["status"]

                            if status == "Ready":
                                image_url = polling_data['result']['sample']
                                break
                            elif status in ["Error", "Failed"]:
                                yield DataPackage(StreamDataStatus.ERROR,data={
                                    "code": polling_response.status,
                                    "message": polling_error_text,
                                    "detail": f"轮询请求失败"
                                })
                                break

                    # 下载并保存图片
                    async with session.get(image_url) as image_response:
                        if image_response.status != 200:
                            image_error_text = await image_response.text()
                            yield DataPackage(StreamDataStatus.ERROR, data={
                                "code": image_response.status,
                                "message": image_error_text,
                                "detail": "图片下载失败"
                            })
                            return

                        image_bytes = await image_response.read()
                        if image_config.is_stream():
                            yield DataPackage(StreamDataStatus.GENERATING,data=image_bytes)

                        # 统一的保存方式
                        memory_folder = os.path.join(os.getcwd(), "memory","pic_lib")
                        os.makedirs(memory_folder, exist_ok=True)
                        image_info = self.save_image_from_bytes(image_bytes, memory_folder)

                        # 补充 URL 字段（因为 Flux 有真实的图片 URL）
                        image_info["url"] = image_url

                        # 使用get_usage方法计算完整的usage信息
                        usage_info = self.get_usage({}, messages, image_info)
                        yield DataPackage(StreamDataStatus.COMPLETED, data=image_info, usage=usage_info)
                        return
        except Exception as e:
            raise # 直接上抛异常，包含错误码
    def get_headers(self):
        return {
            'accept': 'application/json',
            'x-key': self._api_key,
            'Content-Type': 'application/json',
        }
    def get_payload(self,messages:Any):
        return {
            'prompt': messages,
            'aspect_ratio': '1:1'
        }
    def get_chat_url(self):
        return f"{self._base_url}/flux-kontext-pro"
    def parse_stream_chunk(self,chunk_data:dict[str,Any]):
        return ""
    @staticmethod
    def save_image_from_bytes(image_bytes: bytes, memory_folder: str, mime_type="image/png"):
        image_id = f"flux_image_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        extension = "png"
        filename = f"{image_id}.{extension}"
        save_path = os.path.join(memory_folder, filename)
        relative_path = os.path.relpath(save_path,os.getcwd())
        image = Image.open(io.BytesIO(image_bytes))
        image.save(save_path)

        return {
            "image_id": image_id,
            "path": save_path,
            "relative_path": relative_path,
            "mime_type": mime_type,
            "created_at": datetime.now().isoformat(),
        }
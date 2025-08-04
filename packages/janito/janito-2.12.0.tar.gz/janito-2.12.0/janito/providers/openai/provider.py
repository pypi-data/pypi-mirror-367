from janito.llm.provider import LLMProvider
from janito.llm.model import LLMModelInfo
from janito.llm.auth import LLMAuthManager
from janito.llm.driver_config import LLMDriverConfig
from janito.drivers.openai.driver import OpenAIModelDriver
from janito.tools import get_local_tools_adapter
from janito.providers.registry import LLMProviderRegistry
from .model_info import MODEL_SPECS
from queue import Queue

available = OpenAIModelDriver.available
unavailable_reason = OpenAIModelDriver.unavailable_reason


class OpenAIProvider(LLMProvider):
    name = "openai"
    NAME = "openai"
    MAINTAINER = "João Pinto <janito@ikignosis.org>"
    MODEL_SPECS = MODEL_SPECS
    DEFAULT_MODEL = "gpt-4.1"  # Options: gpt-4.1, gpt-4o, o3-mini, o4-mini,

    def __init__(
        self, auth_manager: LLMAuthManager = None, config: LLMDriverConfig = None
    ):
        if not self.available:
            # Even when the OpenAI driver is unavailable we still need a tools adapter
            # so that any generic logic that expects `execute_tool()` to work does not
            # crash with an AttributeError when it tries to access `self._tools_adapter`.
            self._tools_adapter = get_local_tools_adapter()
            self._driver = None
        else:
            self.auth_manager = auth_manager or LLMAuthManager()
            self._api_key = self.auth_manager.get_credentials(type(self).NAME)
            if not self._api_key:
                print(f"[ERROR] No API key found for provider '{self.name}'. Please set the API key using:")
                print(f"  janito --set-api-key YOUR_API_KEY -p {self.name}")
                print(f"Or set the OPENAI_API_KEY environment variable.")
                return
            
            self._tools_adapter = get_local_tools_adapter()
            self._driver_config = config or LLMDriverConfig(model=None)
            if not self._driver_config.model:
                self._driver_config.model = self.DEFAULT_MODEL
            if not self._driver_config.api_key:
                self._driver_config.api_key = self._api_key
            # Set only the correct token parameter for the model
            model_name = self._driver_config.model
            model_spec = self.MODEL_SPECS.get(model_name)
            # Remove both to avoid stale values
            if hasattr(self._driver_config, "max_tokens"):
                self._driver_config.max_tokens = None
            if hasattr(self._driver_config, "max_completion_tokens"):
                self._driver_config.max_completion_tokens = None
            if model_spec:
                if getattr(model_spec, "thinking_supported", False):
                    max_cot = getattr(model_spec, "max_cot", None)
                    if max_cot and max_cot != "N/A":
                        self._driver_config.max_completion_tokens = int(max_cot)
                else:
                    max_response = getattr(model_spec, "max_response", None)
                    if max_response and max_response != "N/A":
                        self._driver_config.max_tokens = int(max_response)
            self.fill_missing_device_info(self._driver_config)
            self._driver = None  # to be provided by factory/agent

    @property
    def driver(self) -> OpenAIModelDriver:
        if not self.available:
            raise ImportError(f"OpenAIProvider unavailable: {self.unavailable_reason}")
        return self._driver

    @property
    def available(self):
        return available

    @property
    def unavailable_reason(self):
        return unavailable_reason

    def create_driver(self):
        """
        Creates and returns a new OpenAIModelDriver instance with input/output queues.
        """
        driver = OpenAIModelDriver(
            tools_adapter=self._tools_adapter, provider_name=self.NAME
        )
        driver.config = self._driver_config
        # NOTE: The caller is responsible for calling driver.start() if background processing is needed.
        return driver

    def create_agent(self, tools_adapter=None, agent_name: str = None, **kwargs):
        from janito.llm.agent import LLMAgent

        # Always create a new driver with the passed-in tools_adapter
        if tools_adapter is None:
            tools_adapter = get_local_tools_adapter()
        # Should use new-style driver construction via queues/factory (handled elsewhere)
        raise NotImplementedError(
            "create_agent must be constructed via new factory using input/output queues and config."
        )

    @property
    def model_name(self):
        return self._driver_config.model

    @property
    def driver_config(self):
        """Public, read-only access to the provider's LLMDriverConfig object."""
        return self._driver_config

    def execute_tool(self, tool_name: str, event_bus, *args, **kwargs):
        self._tools_adapter.event_bus = event_bus
        return self._tools_adapter.execute_by_name(tool_name, *args, **kwargs)


LLMProviderRegistry.register(OpenAIProvider.NAME, OpenAIProvider)

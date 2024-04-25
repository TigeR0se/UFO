# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json

from abc import ABC, abstractmethod
from logging import Logger
from typing import Type

from ...automator.ui_control.screenshot import PhotographerFacade
from ...config.config import Config


configs = Config.get_instance().config_data
BACKEND = configs["CONTROL_BACKEND"]


class BaseProcessor(ABC):
    """
    The base processor for the session.
    """

    def __init__(self, index: int, log_path: str, photographer: PhotographerFacade, request: str, request_logger: Logger, logger: Logger, 
                 round_step: int, global_step: int, prev_status: str, app_window:Type) -> None:
        """
        Initialize the processor.
        :param log_path: The log path.
        :param photographer: The photographer facade to process the screenshots.
        :param request: The user request.
        :param request_logger: The logger for the request string.
        :param logger: The logger for the response and error.
        :param global_step: The global step of the session.
        :param prev_status: The previous status of the session.
        """

        self.log_path = log_path
        self.photographer = photographer
        self.request = request
        self.request_logger = request_logger
        self.logger = logger
        self._app_window = app_window
        
        self.global_step = global_step
        self.round_step = round_step
        self.prev_status = prev_status
        self.index = index
        
        self._step = 0
        self._status = prev_status
        self._prompt_message = None  
        self._response = None  
        self._cost = 0
        self._control_label = None
        self._control_text = None
        self._response_json = None
        self._results = None
        self.app_root = None

        
    def process(self):
        """
        Process the session.
        The process includes the following steps:
        1. Print the step information.
        2. Capture the screenshot.
        3. Get the control information.
        4. Get the prompt message.
        5. Get the response.
        6. Parse the response.
        7. Execute the action.
        8. Update the memory.
        9. Create the app agent if necessary.
        10. Update the step and status.
        """

        self.print_step_info()
        self.capture_screenshot()
        self.get_control_info()
        self.get_prompt_message()
        self.get_response()

        if self.is_error():
            return
        self.parse_response()

        if self.is_error():
            return
        
        self.execute_action()
        self.update_memory()

        if self.should_create_appagent():
            self.create_app_agent()
        self.update_step_and_status()
        
    
    @abstractmethod
    def print_step_info(self):
        """
        Print the step information.
        """
        pass
    
    @abstractmethod 
    def capture_screenshot(self):
        """
        Capture the screenshot.
        """
        pass
    
    @abstractmethod 
    def get_control_info(self): 
        """
        Get the control information.
        """
        pass
  

    @abstractmethod  
    def get_prompt_message(self):
        """
        Get the prompt message.
        """
        pass  
  
    @abstractmethod  
    def get_response(self):  
        """
        Get the response from the LLM.
        """
        pass  
  
    @abstractmethod  
    def parse_response(self):
        """
        Parse the response.
        """
        pass  

    @abstractmethod  
    def execute_action(self):
        """
        Execute the action.
        """
        pass  

    @abstractmethod
    def update_memory(self):
        """
        Update the memory of the Agent.
        """
        pass


    @abstractmethod  
    def update_status(self):
        """
        Update the status of the session.
        """
        pass

    
    def create_app_agent(self):
        """
        Create the app agent.
        """
        pass


    def update_step_and_status(self):
        """
        Update the step and status of the process.
        """
        self._step += 1  
        self.update_status()


    def get_active_window(self):
        """
        Get the active window.
        :return: The active window.
        """
        return self._app_window
    
    
    def get_active_control_text(self):
        """
        Get the active application.
        :return: The active application.
        """
        return self._control_text
    

    def get_process_status(self):
        """
        Get the process status.
        :return: The process status.
        """
        return self._status
    
    
    def get_process_step(self):
        """
        Get the process step.
        :return: The process step.
        """
        return self._step
    
    
    def get_process_cost(self):
        """
        Get the process cost.
        :return: The process cost.
        """
        return self._cost
    

    def is_error(self):
        """
        Check if the process is in error.
        :return: The boolean value indicating if the process is in error.
        """

        return self._status == "ERROR"
    

    def should_create_appagent(self):
        """
        Check if the app agent should be created.
        :return: The boolean value indicating if the app agent should be created.
        """

        return False


    def log(self, response_json: dict) -> dict:
        """
        Set the result of the session, and log the result.
        result: The result of the session.
        response_json: The response json.
        return: The response json.
        """

        self.logger.info(json.dumps(response_json))


    def error_log(self, response_str: str, error: str) -> None:
        """
        Error handler for the session.
        """
        log = json.dumps({"step": self._step, "status": "ERROR", "response": response_str, "error": error})
        self.logger.info(log)
        


    def get_current_action_memory(self):
        """
        Get the current action memory.
        :return: The current action memory.
        """
        pass
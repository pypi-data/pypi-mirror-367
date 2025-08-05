# Copyright 2024 The MQI Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import logging
from logging.handlers import RotatingFileHandler
import websocket
import json
import time
import threading
from typing import List, Dict, Any
import hashlib
import uuid

class Config:
    LOG_FILE = 'mqi_logs.log'
    LOG_LEVEL = logging.DEBUG
    MAX_LOG_SIZE = 5 * 1024 * 1024
    BACKUP_COUNT = 3


def setup_logger(name: str, use_file_logger: bool) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)
    if use_file_logger:
        fh = RotatingFileHandler(Config.LOG_FILE, Config.MAX_LOG_SIZE, Config.BACKUP_COUNT)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)
    return logger

class MQI:
    
    def __init__(self, hostname : str, port : str, username : str, password : str, useFileLogger: bool= False):
        """
        Initializes the MQI object.

        :param hostname: Hostname for connection.
        :param port: Port for connection.
        :param username: Username for authentication.
        :param password: Password for authentication.

        :returns: None
        """
        self.logger = setup_logger(self.__class__.__name__, useFileLogger)
        self.hostname = hostname 
        self.port = port
        self.ws = None 
        self._msg_lock = threading.Lock()
        self._messages = []
        self._retention = 20 
        self.logger.info("Initializing MQI class.")
        try:
            self.connect()
            self._start_reader()
            self._start_cleanup()
            
            
            status, self.auth_token = self.__gen_auth_token(username, password)
            
            self.logger.info("MQI initialized successfully.")
        except Exception as e:
            self.logger.error(f"Error during initialization: {e}")
            raise

    def __del__(self):
        """
        Destructor for MQI class.
        Sends a LOGOUT command and closes the websocket connection if it's open.
        """
        try:
            if self.ws is not None:
                # Attempt to send LOGOUT message
                logout_message = self.__create_message("LOGOUT", {})
                self.ws.send(json.dumps(logout_message))
                self.logger.info("Sent LOGOUT command.")

                # Optionally, read response (safe to ignore errors here)
                try:
                    _ = self.ws.recv()
                except Exception as e:
                    self.logger.warning(f"Exception while waiting for LOGOUT response: {e}")

                # Close the websocket
                self.ws.close()
                self.logger.info("WebSocket connection closed.")

        except Exception as e:
            self.logger.error(f"Exception during destruction: {e}")
    
    def connect(self):
        """
        connect function will create a connection to the cosen Raspberry Pi websocket. 
        If there is no avaialable a "NotFound" error is returned.

        :returns: None
        """
        self.ws = websocket.WebSocket()
        self.ws.connect(self.hostname + ":" + self.port)
        message = self.ws.recv()

    def _start_reader(self) -> None:
        def reader():
            self.logger.info("Starting message reader thread...")
            while True:
                try:
                    data = json.loads(self.ws.recv())
                    entry = {'msg': data, 'ts': time.time()}
                    with self._msg_lock:
                        self._messages.append(entry)
                except Exception as e:
                    self.logger.error(f"Reader error: {e}")
                    break
        threading.Thread(target=reader, daemon=True).start()

    def _start_cleanup(self) -> None:
        def cleanup():
            self.logger.info("Starting message cleanup thread...")
            while True:
                now = time.time()
                with self._msg_lock:
                    self._messages = [e for e in self._messages if now - e['ts'] <= self._retention]
                time.sleep(self._retention / 2)
        threading.Thread(target=cleanup, daemon=True).start()

    def _next_uid(self) -> str:
        return str(uuid.uuid4())
    
    def _get_response(self, uid: str, timeout: float = 5.0) -> Dict[str, Any]:
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._msg_lock:
                for i, entry in enumerate(self._messages):
                    if entry['msg'].get('uid') == uid:
                        return self._messages.pop(i)['msg']
            time.sleep(0.01)
        raise TimeoutError(f"No response for uid {uid} after {timeout}s")

        
    def __list_to_string(self, lst : List[Any]) -> str:
        """
        Converts a list to a string.

        :param lst: List to convert.

        :returns: String representation of the list.
        """
        result = [str(ch_id) for ch_id in lst]

        return result

        
    def __gen_auth_token(self, username: str, password: str):
        """
        Generates an authentication token.

        :param username: Username.
        :param password: Password.

        :returns: Authentication token.
        """
        password_bytes = password.encode('utf-8')
        
        data = {
                "__MESSAGE__": "message",
                "command": "LOGIN",
                "uid": self._next_uid(),
                "timestamp": str(time.time()),
                "body" : {
                    "username" : username,
                    "password" : hashlib.sha256(password_bytes).hexdigest()
                }
        }
        status, body, uid = self.__send_return_resonse(data)
        # print(f"uid: {response['uid']}, status: {response['status']}")
        print(f"status: {status}, body: {body}")

        return status, body["token"]
    
    def __create_message(self, command: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a message payload for communication with the server.

        :param command: The command to send (e.g., "LOGIN", "REQ_STATUS").
        :param body: The body of the message as a dictionary.
        :returns: A dictionary representing the message payload.
        """
        timestamp = time.time()
        
        message = {
            "__MESSAGE__": "message",
            "command": command,
            "uid": self._next_uid(),
            "timestamp": str(timestamp),
            "body": body
        }
        if self.auth_token!= "":
            message["body"]["token"] = self.auth_token
        return message

    def __send_return_resonse(self, msg):
        try:

            self.ws.send(json.dumps(msg))
            response_dict = self._get_response(msg['uid'])
            
            
            
            return response_dict.get('status', {}), response_dict.get('body', {}), response_dict.get('uid', {})
        except Exception as e:
            self.logger.error(f"Error while sending {json.dumps(msg)}: {e}")
            raise

        
    def get_status(self, biasbox_id : int):
        """
        Requests the status of a specific biasbox.

        :param biasbox_id: The ID of the biasbox.

        :returns: None
        """
        data = self.__create_message("REQ_STATUS", {"biasbox_id" : biasbox_id})
        

        status, body, uid = self.__send_return_resonse(data)

        return status

        
    def set_current(self, biasbox_id : int, chanel_ids : List[int], value : float):
        """
        Sets the current for specific channels on an biasbox.

        :param biasbox_id: The ID of the biasbox.
        :param chanel_ids: List[int] of channels to set the current for.
        :param value: Current value to set.

        :returns: Status of the request.
        """
        data = self.__create_message("SET_CURRENT",
                    {"biasbox_id" : biasbox_id,
                    "channel_ids" : self.__list_to_string(chanel_ids),
                    "value" : value})
        status, body, uid = self.__send_return_resonse(data)


        return status, body

        
    def set_voltage(self, biasbox_id : int, chanel_ids : List[int], value : float):
        """
        Sets the voltage for specific channels on an biasbox.

        :param biasbox_id: The ID of the biasbox.
        :param chanel_ids: List[int] of channels to set the voltage for.
        :param value: Voltage value to set.

        :returns: Status of the request.
        """
        data = self.__create_message("SET_VOLTAGE",
                    {"biasbox_id" : biasbox_id,
                    "channel_ids" : self.__list_to_string(chanel_ids),
                    "value" : value})

        print(data)
        status, body, uid = self.__send_return_resonse(data)

        return status, body

        
    def get_number_of_channels(self, biasbox_id : int):
        """
        Gets the number of channels for a specific biasbox.

        :param biasbox_id: The ID of the biasbox.

        :returns: Number of channels.
        """
        data = self.__create_message("GET_NUMBER_OF_CHANNELS",
                    {"biasbox_id" : biasbox_id})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

        
    def set_channels_active(self, biasbox_id : int, chanel_ids : List[int]):
        """
        Sets specific channels on an biasbox as active.

        :param biasbox_id: The ID of the biasbox.
        :param chanel_ids: List[int] of channels to set as active, rest are set as inactive.

        :returns: Status of the request.
        """
        
        data = self.__create_message("SET_CHANNELS_ACTIVE",
                    {"biasbox_id" : biasbox_id,
                    "channel_ids" : self.__list_to_string(chanel_ids)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

        
    def get_channels_active(self, biasbox_id : int):
        """
        Gets the active channels for a specific biasbox.

        :param biasbox_id: The ID of the biasbox.

        :returns: List of active channel IDs.
        """
        data = self.__create_message("GET_CHANNELS_ACTIVE",
                    {"biasbox_id" : biasbox_id})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

        
    def get_voltage(self, biasbox_id : int, chanel_ids : List[int]):
        """
        Gets the ADC voltage for specific channels on an biasbox.

        :param biasbox_id: The ID of the biasbox.
        :param chanel_ids: List[int] of channels to get the voltage for.

        :returns: Dictionary with channel voltage information.
        """
        data = self.__create_message("GET_VOLTAGE",
                    {"biasbox_id" : biasbox_id,
                    "channel_ids" : self.__list_to_string(chanel_ids)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

        
    def get_current(self, biasbox_id : int, chanel_ids : List[int]):
        """
        Gets the current for specific channels of a Bias Box.

        :param biasbox_id: The ID of the biasbox.
        :param chanel_ids: List[int] of channels to get the current for.

        :returns: Dictionary with channel current information.
        """
        data = self.__create_message("GET_CURRENT",
                    {"biasbox_id" : biasbox_id,
                    "channel_ids" : self.__list_to_string(chanel_ids)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body


        
    def get_target_voltage(self, biasbox_id : int, chanel_ids : List[int]):
        """
        Gets the target voltage for specific channels on an biasbox.

        :param biasbox_id: The ID of the biasbox.
        :param chanel_ids: List[int] of channels to get the target voltage for.

        :returns: Dictionary with channel target voltage information.
        """
        data = self.__create_message("GET_TARGET_VOLTAGE",
                    {"biasbox_id" : biasbox_id,
                    "channel_ids" : self.__list_to_string(chanel_ids)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body


       
    def get_target_current(self, biasbox_id : int, chanel_ids : List[int]):
        """
        Gets the target current for an biasbox.

        :param biasbox_id: The ID of the biasbox.
        :param chanel_ids: List[int] of channels to get the target current for.

        :returns: Dictionary with target current information.
        """
        data = self.__create_message("GET_TARGET_CURRENT",
                    {"biasbox_id" : biasbox_id,
                    "channel_ids" : self.__list_to_string(chanel_ids)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
        
    def get_load_resistance(self, biasbox_id : int, channel_ids : List[int]):

        """
        Gets the load resitance for an Bias Box.

        :param biasbox_id: The ID of the biasbox.
        :param chanel_ids: List[int] of channels to get the load resistance for.

        :returns: Dictionary with load resistance information.
        """
        data = self.__create_message("GET_LOAD_RESISTANCE",
                    {"biasbox_id" : biasbox_id,
                    "channel_ids" : self.__list_to_string(channel_ids)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

        
    def get_max_volt_current(self, biasbox_id : int, channel_ids : List[int]):
        """
        Gets the maximum voltage and current for an biasbox.

        :param biasbox_id: The ID of the biasbox.
        :param chanel_ids: List[int] of channels to get the maximum voltage and current for.

        :returns: Dictionary with maximum voltage and current.
        """
        data = self.__create_message("GET_MAX_VOLT_CURRENT",
                   {"biasbox_id" : biasbox_id,
                    "channel_ids" : self.__list_to_string(channel_ids)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

       
    def restart_biasbox(self, biasbox_id : int):
        """
        Restarts a specific biasbox.

        :param biasbox_id: The ID of the biasbox.

        :returns: Status of the request.
        """
        data = self.__create_message("RESTART_BIASBOX",
                    {"biasbox_id" : biasbox_id})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

       
    def get_id(self, biasbox_id : int):
        """
        Gets the unique ID of a specific biasbox.

        :param biasbox_id: The ID of the biasbox.

        :returns: The unique ID of the biasbox.
        """
        data = self.__create_message("GET_ID",
                    {"biasbox_id" : biasbox_id})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
        
    def get_number_of_biasboxes(self):
        """
        Gets the number of biasboxs connected.

        :returns: Number of connected biasboxs.
        """
        data = self.__create_message("NUMB_OF_BIASBOXES",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

    def restart_rpi(self):

        """
            Restarts the Control Unit.

            :returns: Status of the request.
        """
        data = self.__create_message("RESTART_CONTROL_UNIT",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

    """
        TODO: Gets the configuration of a specific biasbox.

        :param biasbox_id: The ID of the biasbox.

        :returns: config
    """
    def get_config(self):
        data = self.__create_message("GET_CONFIG",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body


    """
        Sets the configuration of the RPi.

        :returns: request status
    """
    def set_config(self, configJson: dict):
        data = self.__create_message("SET_CONFIG",
                    configJson)
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def get_ControlUnit_voltages(self):
        data = self.__create_message("GET_CONTROLUNIT_VOLTAGES",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def get_ControlUnit_temperatures(self):
        data = self.__create_message("GET_CONTROLUNIT_TEMPERATURES",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def get_list_of_Serial_Connections(self):
        data = self.__create_message("GET_LIST_OF_SERIAL_CONNECTIONS",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def set_led_brightness(self,  brightness:float, ):

        data = self.__create_message("SET_LED_BRIGHTNESS",
                {
                    "brightness": brightness
                })
        status, body, uid = self.__send_return_resonse(data)

        return status, body

    def activate_ControlUnit_fan(self, activate: bool):
        data = self.__create_message("ACTIVATE_CONTROLUNIT_FAN",
                    {"activate": activate})
        status, body, uid = self.__send_return_resonse(data)

        return status, body


    def get_BiasBox_temperatures(self, biasbox_id : int):
        data = self.__create_message("GET_BIASBOX_TEMPERATURES",
                    {"biasbox_id" : biasbox_id})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def activate_BiasBox_fan(self, biasbox_id : int, activate: bool):
        data = self.__create_message("ACTIVATE_BIASBOX_FAN",
                    {"biasbox_id" : biasbox_id,
                    "activate": activate})
        status, body, uid = self.__send_return_resonse(data)

        return status, body


    def get_BiasBox_voltchecker(self, biasbox_id : int):
        data = self.__create_message("GET_BIASBOX_VOLTCHECKER",
                    {"biasbox_id" : biasbox_id})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    
    def set_BiasBox_AutoDelatching(self, biasbox_id : int, activate: bool, checkLatchingInterval_ms: int, volt_drop_for_detection: float,
                                   perc_start_fineSweep: float, roughSteps: int, fineSteps: int, sweep_delay_ms: int):
        """
        Configures and controls the auto-de-latching mechanism of a BiasBox.

        :param biasbox_id: The ID of the BiasBox to configure.
        :param activate: Whether to activate (True) or deactivate (False) auto-de-latching.
        :param checkLatchingInterval_ms: Interval (in milliseconds) for checking latch-up conditions.
        :param volt_drop_for_detection: Voltage drop threshold to detect a latch-up in perc of the current voltage.
        :param perc_start_fineSweep: Percentage of previous voltage to start the fine sweep after detection.
        :param roughSteps: Number of steps for the rough voltage sweep.
        :param fineSteps: Number of steps for the fine voltage sweep.
        :param sweep_delay_ms: Delay (in milliseconds) between each voltage step during the sweep process.

        :returns: A tuple containing the status and response body from the BiasBox.
        """
        data = self.__create_message("SET_AUTO_DE_LATCHING_BIASBOX",
                    {"biasbox_id" : biasbox_id,
                     "activate": activate,
                     "checkLatchingInterval_ms": checkLatchingInterval_ms,
                     "volt_drop_for_detection": volt_drop_for_detection,
                     "perc_start_fineSweep": perc_start_fineSweep,
                     "roughSteps": roughSteps,
                     "fineSteps": fineSteps,
                     "sweep_delay_ms": sweep_delay_ms})
        
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def get_BiasBox_AutoDelatching(self, biasbox_id: int):
        """
        Gets the auto-de-latching parameter for a specific BiasBox.
        :param biasbox_id: The ID of the BiasBox to get the auto-de-latching parameter for.
        :returns: A tuple containing the status and response body with the auto-de-latching parameters.
        """
        data = self.__create_message("GET_AUTO_DE_LATCHING_BIASBOX",
                    {"biasbox_id" : biasbox_id})
        status, body, uid = self.__send_return_resonse(data)

        return status, body

    def get_BiasBox_AutoDelatching_Counter(self, biasbox_id : int, channel_ids : List[int]):
        """
        Gets the auto-de-latching counter for specific channels on a BiasBox which is reseted after calling this function.

        :param biasbox_id: The ID of the BiasBox to get the auto-de-latching counter for.
        :param chanel_ids: List[int] of channels to get the auto-de-latching counter for.

        :returns: A tuple containing the status and response body with the counter per channel.

        """
        data = self.__create_message("COUNTER_AUTO_DE_LATCHING_BIASBOX",
                   {"biasbox_id" : int(biasbox_id),
                    "channel_ids" : self.__list_to_string(channel_ids)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def get_temperatur_secoondstage_compressor(self):
        """
        Gets the temperature of the second stage compressor.
        :returns: Temperature of the second stage compressor.
        """
        data = self.__create_message("GET_TEMPERATUR_SECONDSTAGE_COMPRESSOR",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def set_compressor_running(self, activate: bool):
        """
        Sets the compressor running status.

        :param bool: True to start the compressor, False to stop.

        :returns: None
        """
        data = self.__create_message("SET_COMPRESSOR_RUNNING",
                    {"activate" : bool(activate)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def set_compressor_speed(self, speed: float):
        """
        Sets the compressor speed.

        :param float: Speed value to set.

        :returns: None
        """
        data = self.__create_message("SET_COMPRESSOR_SPEED",
                    {"speed" : float(speed)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def set_compressor_coldhead_speed(self, speed: float):
        """
        Sets the compressor coldhead speed.

        :param float: Speed value to set.

        :returns: None
        """
        data = self.__create_message("SET_COMPRESSOR_COLDHEAD_SPEED",
                    {"speed" : float(speed)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def get_compressor_status(self):
        """
        Gets the compressor status values.

        :returns: Compressor status values.
        """
        data = self.__create_message("GET_COMPRESSOR_STATUS",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body


    def set_auth(self, activate: bool):
        """
        Sets the authentication status.

        :param bool: True to enable authentication, False to disable.

        :returns: None
        """
        data = self.__create_message("SET_AUTH",
                    {"activate" : bool(activate)})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    def is_auth_activated(self):
        """
        Gets the authentication status.
        :returns: Authentication status.
        """             
        data = self.__create_message("GET_AUTH",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def create_user(self, username: str, password: str):
        """
        Creates a new user with the given username and password.

        :param username: The username for the new user.
        :param password: The password for the new user.

        :returns: Status of the request.
        """
        password_bytes = password.encode('utf-8')
        data = self.__create_message("CREATE_USER",
                    {"new_username" : username,
                    "new_password" : hashlib.sha256(password_bytes).hexdigest()})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def get_all_users(self):
        """
        Gets all users.

        :returns: List of all users.
        """
        data = self.__create_message("GET_ALL_USERS",
                    {})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def update_user(self, username: str, col: str, value: str):
        """
        Updates the password for an existing user.

        :param username: The username of the user to update.
        :param password: The new password for the user.

        :returns: Status of the request.
        """
        
        data = self.__create_message("UPDATE_USER",
                    {"username" : username,
                    "col" : col, 
                    "value" : value})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def update_user_password(self, username: str, password: str):
        """
        Updates the password for an existing user.

        :param username: The username of the user to update.
        :param password: The new password for the user.

        :returns: Status of the request.
        """
        password_bytes = password.encode('utf-8')
        data = self.__create_message("UPDATE_USER",
                    {"username" : username,
                    "col" : "password",
                    "value" : hashlib.sha256(password_bytes).hexdigest()})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def update_username(self, old_username: str, new_username: str):
        """
        Updates the username for an existing user.

        :param old_username: The current username of the user to update.
        :param new_username: The new username for the user.

        :returns: Status of the request.
        """
        data = self.__create_message("UPDATE_USER",
                    {"username" : old_username,
                    "col" : "username",
                    "value" : new_username})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def update_auth_level(self, username: str, auth_level: str):
        """
        Updates the authentication level for an existing user.

        :param username: The username of the user to update.
        :param auth_level: The new authentication level for the user. BASE, ADMIN, SUPER

        :returns: Status of the request.
        """
        data = self.__create_message("UPDATE_USER",
                    {"username" : username,
                    "col" : "auth",
                    "value" : auth_level})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def delete_user(self, username: str):
        """
        Deletes an existing user.

        :param username: The username of the user to delete.

        :returns: Status of the request.
        """
        data = self.__create_message("DELETE_USER",
                    {"username" : username})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
    
    def get_user(self, username: str):
        """
        Gets the information of a specific user.

        :param username: The username of the user to retrieve.

        :returns: User information.
        """
        data = self.__create_message("GET_USER",
                    {"username" : username})
        status, body, uid = self.__send_return_resonse(data)

        return status, body
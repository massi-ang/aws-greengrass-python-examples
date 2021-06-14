# Copyright 2021 Massimiliano Angelino
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

# Copyright 2021 Massimiliano Angelino
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

from threading import Thread
from typing import Callable, Optional
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    PublishToIoTCoreRequest,
    SubscribeToIoTCoreRequest,
    connect
)
import os
import time
import concurrent.futures
#from awsiot.greengrasscoreipc.model import QOS as QOS

TIMEOUT = 10



ipc_client = connect()

def sync_error_handler(error: Exception) -> None:
    raise error

class SubscribeHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self, handler: Callable[[str, bytes], None], error_handler: Callable[[Exception], None] ):
        self._handler = handler
        self._error_handler = error_handler

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        msg = event.message
        t = Thread(target=self._handler, args=[msg.topic_name, msg.payload])
        t.start()

    def on_stream_error(self, error: Exception)-> bool:
        t = Thread(target=self._error_handler, args=[error])
        t.start()
        return True

    def on_stream_closed(self) -> None:
        pass

def publish_async(topic: str, message: bytes, qos: QOS) -> concurrent.futures.Future:
    request = PublishToIoTCoreRequest()
    request.topic_name = topic
    request.payload = bytes(message, "utf-8")
    request.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(request)
    future = operation.get_response()
    return future

def publish(topic: str, message: bytes, qos: QOS):
    try:
        future = publish_async(topic, message, qos)
        future.result(TIMEOUT)
    except Exception as ex:
        raise ex

def subscribe_async(topic: str, qos: QOS, handler: Callable[[str, bytes], None], error_handler: Callable[[Exception], None]) -> concurrent.futures.Future:
    request = SubscribeToIoTCoreRequest()
    request.topic_name = topic
    request.qos = qos
    handler = SubscribeHandler(handler, error_handler)
    operation = ipc_client.new_subscribe_to_iot_core(handler)
    operation.activate(request)
    future = operation.get_response()
    return future



def subscribe(topic: str, qos: QOS, handler: Callable[[str, bytes], None]):
    try:
        future = subscribe_async(topic, qos, handler, sync_error_handler)
        future.result(TIMEOUT)
    except Exception as ex:
        raise ex
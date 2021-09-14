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

import greengrassipcsdk as gg
import os
import time

client = gg.IPCIotCore()

topic = os.environ.get("TOPIC", "test/helloworld")
message = os.environ.get("MESSAGE", "Hello, World")
qos = gg.QOS.AT_LEAST_ONCE

def message_handler(topic:str, data: bytes):
    print(f"Got {data} on {topic}")

client.subscribe(topic+'/resp', gg.QOS.AT_LEAST_ONCE, message_handler)

while True: 
    try:
        client.publish(topic=topic, qos=0, message=bytes(message, "utf-8"))
    except Exception as ex:
        print(ex)
    time.sleep(5)

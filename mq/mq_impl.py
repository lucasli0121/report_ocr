'''
Author: liguoqiang
Date: 2023-07-14 15:00:31
LastEditors: liguoqiang
LastEditTime: 2025-12-15 19:19:56
Description: a mqtt client to notify stock real-time data to every client who subscribe the topic
'''
import logging
import paho.mqtt.client as mqtt
import os
import uuid
import hmac
import hashlib
import base64

# TODO: implement the mqtt client
class MqImpl:
    # 测试阿里的连接信息
    access_key = os.getenv("ALIYUN_ACCESS_KEY_ID")
    secret_key = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
    group_id = '' #'GID_hjy_h03'

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.host = 'mqtt-cn-ot93vfkv202.mqtt.aliyuncs.com'
        self.port = 1883
        self.user = 'Signature|' + self.access_key + '|mqtt-cn-ot93vfkv202'
        client_id = f'{self.group_id}@@@{uuid.uuid4()}'
        digest = hmac.new(self.secret_key.encode('utf-8'), client_id.encode('utf-8'), hashlib.sha1).digest()
        self.password = base64.b64encode(digest).decode('utf-8')

        self.isconnected = False
        self.client = mqtt.Client(client_id=client_id,
                clean_session=True,
                userdata=None,
                protocol=mqtt.MQTTv311,
                transport="tcp",
                reconnect_on_failure=True)
        # self.client.tls_set(ca_certs=cacert,
        #         certfile=certfile,
        #         keyfile=keyfile,
        #         cert_reqs=ssl.CERT_REQUIRED,
        #         tls_version=ssl.PROTOCOL_TLSv1_2,
        #         ciphers=None)
        self.client.username_pw_set(self.user, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)

    def __del__(self):
        self.disconnect()
    '''
    function: connect
    description: connect to mqtt server
    return {*}
    '''    
    def connect(self):
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        err_code = self.client.connect(self.host, int(self.port), keepalive=20)
        if err_code != 0:
            self.logger.error("mqtt client connect failed, err_code: " + str(err_code))
            return False
        return True

        
    '''
    function: disconnect
    description: 
    return {*}
    '''    
    def disconnect(self) -> None:
        if self.isconnected:
            self.isconnected = False
            self.client.disconnect()
            self.client.loop_stop()

    '''
    function: on_connect
    description: called when connected to mqtt server
    param {*}
    return {*}
    '''
    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code "+str(rc))
        self.isconnected = True
    
    '''
    function: on_disconnect
    description: when connection lost, try to reconnect
    return {*}
    '''
    def on_disconnect(self, client, userdata, rc):
        self.logger.info("mqtt client disconnected, try to reconnect")

    '''
    function: subscribe
    description: subscribe topic
    param {*} topic
    param {*} handle_msg: callback function when received message
    return {bool}
    '''
    def subscribe(self, topic, handle_msg) -> bool:
        if self.isconnected is False:
            self.logger.error("mqtt client not connected")
            return False
        try:
            self.client.subscribe(topic)
            self.logger.info("subscribe topic: " + topic)
        except Exception as err:
            self.logger.error("subscribe topic failed, " + str(err))
            return False
        self.client.message_callback_add(topic, handle_msg)
        return True
    
    def unsubscribe(self, topic) -> bool:
        if self.isconnected is False:
            self.logger.error("mqtt client not connected")
            return False
        try:
            self.client.unsubscribe(topic)
            self.client.message_callback_remove(topic)
            self.logger.info("unsubscribe topic: " + topic)
        except Exception as err:
            self.logger.error("unsubscribe topic failed, " + str(err))
            return False
        return True
    '''
    function: loop_for_thread
    description: loop for mqtt client event in a thread
    param {*} self
    return {*}
    '''    
    def loop_for_thread(self):
        self.client.loop_start()
        
    '''
    function: loopForEnver
    description: 
    return {*}
    '''    
    def loop_forever(self):
        try:
            self.client.loop_forever(timeout=60)
        except Exception as err:
            self.logger.error("mqtt client loop failed, " + str(err))
    '''
    function: on_message
    description: called when received message from mqtt server
    param {*}
    return {*}
    '''
    def on_message(self, client, userdata, msg):
        self.logger.info(msg.topic+" "+str(msg.payload))

    def publish_data(self, topic, jsonstr):
        if self.isconnected is False:
            self.logger.error("mqtt client not connected")
            return
        self.logger.info(" ready publish data, topic:" + topic + ",value:" + jsonstr)
        try:
            mqinfo = self.client.publish(topic, jsonstr)
            mqinfo.wait_for_publish(30)
            if mqinfo.rc != mqtt.MQTT_ERR_SUCCESS:
                self.logger.error("publish mq data failed, topic:" + topic + ",value:" + jsonstr)
        except Exception as err:
            self.logger.error("publish mq data exception: " + str(err))
    
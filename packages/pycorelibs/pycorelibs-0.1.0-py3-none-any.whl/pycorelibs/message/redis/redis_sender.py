# -*- coding: utf-8 -*-
''' ************************************************************ 
### Author: Zeng Shengbo shengbo.zeng@ailingues.com
### Date: 07/03/2025 10:54:08
### LastEditors: Zeng Shengbo shengbo.zeng@ailingues.com
### LastEditTime: 07/03/2025 10:57:17
### FilePath: //pycorelibs//message//redis//sender.py
### Description: 用于发送消息（写入 Redis 队列）支持泛型消息类注入
### 
### Copyright (c) 2025 by AI Lingues, All Rights Reserved. 
********************************************************** '''



from pycorelibs.message.message import MessageModel
from pycorelibs.message.redis.redis_queue import RedisMessageQueue


class MessageSender:
    def __init__(self, queue:RedisMessageQueue, model_class=MessageModel):
        """
        MessageSender构造函数

        Args:
            queue (RedisMessageQueue): RedisMessageQueue队列对象实例
            model_class (_type_, optional): 泛型消息类. Defaults to MessageModel.
        """        
        self.queue:RedisMessageQueue = queue
        self.model_class = model_class  # 支持自定义消息模型（可继承自 MessageModel）

    def send(self, text: str, priority: int = 0, **kwargs):
        """
        消息发送(push到redis消息队列)

        _extended_summary_

        Args:
            text (str): 消息文本字符串
            priority (int, optional): 发送优先级. Defaults to 0. 数值越低，越高优先级
        """        
        message = self.model_class(text=text, priority=priority, **kwargs)
        self.queue.push(message)

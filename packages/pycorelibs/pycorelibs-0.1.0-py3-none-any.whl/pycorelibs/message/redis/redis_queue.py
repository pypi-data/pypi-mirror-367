# -*- coding: utf-8 -*-
"""************************************************************
### Author: Zeng Shengbo shengbo.zeng@ailingues.com
### Date: 07/03/2025 10:54:08
### LastEditors: Zeng Shengbo shengbo.zeng@ailingues.com
### LastEditTime: 07/03/2025 10:55:45
### FilePath: //pycorelibs//message//redis//queue.py
### Description: 底层 Redis 消息队列封装，支持优先级、确认、失败重试等
###
### Copyright (c) 2025 by AI Lingues, All Rights Reserved.
**********************************************************"""

import redis
import time
from typing import Type
from pycorelibs.message.message import MessageModel


class RedisMessageQueue:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        queue_key: str = "message_queue",
        model_class: Type[MessageModel] = MessageModel,
    ):
        """
        Redis消息队列管理器

        _extended_summary_

        Args:
            host (str, optional): redis服务主机地址. Defaults to "localhost".
            port (int, optional): redis服务端口. Defaults to 6379.
            db (int, optional): redis服务数据库索引. Defaults to 0.
            queue_key (str, optional): redis服务数据名. Defaults to "message_queue".
            model_class (Type[MessageModel], optional): redis服务消息类型. Defaults to MessageModel.
        """        
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.queue_key = queue_key  # ZSET for main queue
        self.processing_key = (
            f"{queue_key}_processing"  # HASH to hold processing messages
        )
        self.retry_key = f"{queue_key}_retry"  # ZSET for retrying
        self.model_class = model_class  # ✅ 动态支持 MessageModel 的子类

    def push(self, message: MessageModel):
        """
        消息推送至redis服务中

        Args:
            message (MessageModel): MessageModel消息对象实例
        """        
        score = int(time.time()) + (message.priority or 0)

        self.redis.zadd(self.queue_key, {message.model_dump_json(): score})

    def pop(self) -> MessageModel:
        """
        从redis服务中弹出消息
        
        消息弹出后即从redis服务中删除

        Returns:
            MessageModel: MessageModel消息实例对象
        """        
        now = int(time.time())
        items = self.redis.zrangebyscore(self.queue_key, 0, now, start=0, num=1)
        if not items:
            return None
        message_raw = items[0]
        self.redis.zrem(self.queue_key, message_raw)
        message = self.model_class.model_validate_json(message_raw)  # ✅ 保留所有字段
        self.redis.hset(self.processing_key, message.msg_id, message_raw)
        return message

    def confirm(self, msg_id: str):
        self.redis.hdel(self.processing_key, msg_id)

    def retry_failed(self, delay: int = 10):
        # Move old processing back to retry queue
        now = int(time.time())
        for msg_id, msg_raw in self.redis.hgetall(self.processing_key).items():
            self.redis.zadd(self.retry_key, {msg_raw: now + delay})
            self.redis.hdel(self.processing_key, msg_id)

        # Move retry back to main queue if time comes
        for msg_raw in self.redis.zrangebyscore(self.retry_key, 0, now):
            self.redis.zrem(self.retry_key, msg_raw)
            self.redis.zadd(self.queue_key, {msg_raw: now})

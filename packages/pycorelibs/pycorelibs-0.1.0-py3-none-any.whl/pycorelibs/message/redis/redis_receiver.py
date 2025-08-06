# -*- coding: utf-8 -*-
"""************************************************************
### Author: Zeng Shengbo shengbo.zeng@ailingues.com
### Date: 07/03/2025 10:54:08
### LastEditors: Zeng Shengbo shengbo.zeng@ailingues.com
### LastEditTime: 07/03/2025 10:58:33
### FilePath: //pycorelibs//message//redis//receiver.py
### Description: 用于接收消息并回调处理函数（读取 Redis 队列）
###
### Copyright (c) 2025 by AI Lingues, All Rights Reserved.
**********************************************************"""

import asyncio

from pycorelibs.message.redis.redis_queue import RedisMessageQueue


class MessageReceiver:
    def __init__(
        self, queue: RedisMessageQueue, callback: any, retry_interval: int = 30
    ):
        """
        消息接收器

        _extended_summary_

        Args:
            queue (RedisMessageQueue): 绑定的Redis消息队列
            callback (any): 消息回调函数,用户定义,如果为None则不做回调
            retry_interval (int, optional): 重试的时间间隔(秒). Defaults to 30.
        """        
        self.queue: RedisMessageQueue = queue
        self.callback = callback
        self.retry_interval = retry_interval

    async def run(self):
        while True:
            msg = self.queue.pop()
            if msg:
                try:
                    if self.callback is not None:
                        await self.callback(msg)
                        self.queue.confirm(msg.msg_id) # 消息处理确认
                except Exception as e:
                    print("消息处理失败:", e)
            else:
                await asyncio.sleep(1)

            self.queue.retry_failed(delay=self.retry_interval)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

logger = logging.getLogger("SuperBlog")

# 指定logger输出格式
fmt = "[%(asctime)s] [%(levelname)s]: %(filename)s   %(message)s"
date_fmt = "%y/%m/%d %H:%M:%S"
formatter = logging.Formatter(fmt, date_fmt)

# 文件日志
# file_handler = logging.FileHandler("test.log")
# file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式

# 控制台日志
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  # 也可以直接给formatter赋值

# 为logger添加的日志处理器
# logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 指定日志的最低输出级别，默认为WARN级别
logger.setLevel(logging.INFO)

# 移除一些日志处理器
# logger.removeHandler(file_handler)


import logging

#logging.warning('Watch out!') # will print a message to the console
#logging.info('I told you so') # will not print anything

# log追加写入到文件example.log
#logging.basicConfig(filename='example.log',level=logging.DEBUG)

# log覆盖写入到文件example.log
#logging.basicConfig(filename='example.log',filemode='w',level=logging.DEBUG)

# 格式化log文件内容
#logging.basicConfig(filename='example.log',format='%(levelname)s:%(message)s',filemode='w',level=logging.DEBUG)

# 加时间格式化到文件
#logging.basicConfig(format='%(asctime)s %(message)s',filename='example.log',filemode='w',level=logging.DEBUG)

# more control over the formatting of the date/time
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
logging.warning('%s before you %s', 'Look', 'leap!')


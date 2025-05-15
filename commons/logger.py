import logging
import os


def get_file_handler(
    log_name: str, mode: int, formatter: logging.Formatter, save_path: str = "logs"
):
    os.makedirs(save_path, exist_ok=True)
    # file logs
    file_handler = logging.FileHandler(
        filename=os.path.join(save_path, log_name), mode="a"
    )
    file_handler.setLevel(mode)
    file_handler.setFormatter(formatter)
    return file_handler


def config_logger(logger: logging.Logger, debug_mode: bool = True):
    formatter = logging.Formatter(
        "[pid=%(process)s] - [%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(message)s]"
    )
    console_handler = logging.StreamHandler()  # console handler
    console_handler.setLevel(logging.DEBUG)
    # add formatter to console_handler
    console_handler.setFormatter(formatter)

    # file logs
    debug_logger = get_file_handler(
        log_name="debug.log", mode=logging.DEBUG, formatter=formatter
    )
    # info_logger = get_file_handler(
    #     log_name="info.log", mode=logging.INFO, formatter=formatter
    # )
    # error_logger = get_file_handler(
    #     log_name="error.log", mode=logging.ERROR, formatter=formatter
    # )
    logger.addHandler(debug_logger)
    # logger.addHandler(info_logger)
    # logger.addHandler(error_logger)
    # logging level set to DEBUG
    logger.setLevel(logging.DEBUG)
    return logger


def logger(__name__):
    logging_obj = config_logger(logging.getLogger(__name__))
    return logging_obj


# import logging
# import boto3
# from datetime import datetime
# import os


# class OnDemandCloudWatchHandler(logging.Handler):
#     def __init__(self, log_group_name, region_name):
#         super().__init__()
#         self.log_group_name = log_group_name
#         self.client = boto3.client("logs", region_name=region_name)

#     def emit(self, record):
#         log_stream_name = "analytics-logs"
#         try:
#             # Format the message
#             msg = self.format(record)

#             # Send directly to CloudWatch
#             self.client.put_log_events(
#                 logGroupName=self.log_group_name,
#                 logStreamName=log_stream_name,
#                 logEvents=[{"timestamp": int(record.created * 1000), "message": msg}],
#             )
#         except Exception:
#             self.handleError(record)


# def get_file_handler(
#     log_name: str, mode: int, formatter: logging.Formatter, save_path: str = "logs"
# ):
#     os.makedirs(save_path, exist_ok=True)
#     # file logs
#     file_handler = logging.FileHandler(
#         filename=os.path.join(save_path, log_name), mode="a"
#     )
#     file_handler.setLevel(mode)
#     file_handler.setFormatter(formatter)
#     return file_handler


# def config_file_logger(logger: logging.Logger, debug_mode: bool = True):
#     formatter = logging.Formatter(
#         "[pid=%(process)s] - [%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(message)s]"
#     )
#     console_handler = logging.StreamHandler()  # console handler
#     console_handler.setLevel(logging.DEBUG)
#     # add formatter to console_handler
#     console_handler.setFormatter(formatter)

#     # file logs
#     debug_logger = get_file_handler(
#         log_name="debug.log", mode=logging.DEBUG, formatter=formatter
#     )
#     # info_logger = get_file_handler(
#     #     log_name="info.log", mode=logging.INFO, formatter=formatter
#     # )
#     # error_logger = get_file_handler(
#     #     log_name="error.log", mode=logging.ERROR, formatter=formatter
#     # )
#     logger.addHandler(debug_logger)
#     # logger.addHandler(info_logger)
#     # logger.addHandler(error_logger)
#     # logging level set to DEBUG
#     logger.setLevel(logging.DEBUG)
#     return logger


# def config_logger(logger: logging.Logger, debug_mode: bool = True):
#     formatter = logging.Formatter(
#         "[pid=%(process)s] - [%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(message)s]"
#     )

#     # Console handler
#     console_handler = logging.StreamHandler()
#     console_handler.setFormatter(formatter)
#     console_handler.setLevel(logging.DEBUG)

#     # Custom CloudWatch handler
#     cloudwatch_handler = OnDemandCloudWatchHandler(
#         log_group_name="rsc-application", region_name="us-east-2"
#     )
#     cloudwatch_handler.setFormatter(formatter)

#     logger.addHandler(console_handler)
#     logger.addHandler(cloudwatch_handler)
#     logger.setLevel(logging.DEBUG)

#     return logger


# def logger(__name__):
#     if os.environ.get("local", False):
#         logging_obj = config_file_logger(logging.getLogger(__name__))
#         return logging_obj
#     else:
#         logging_obj = config_logger(logging.getLogger(__name__))
#         return logging_obj

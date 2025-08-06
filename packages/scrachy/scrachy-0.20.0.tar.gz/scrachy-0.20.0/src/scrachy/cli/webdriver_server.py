#  Copyright 2023 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.
"""
A simple server that receives pickled ``SeleniumRequests`` from ``stdin`` and
sends back pickled ``HtmlResponses`` to ``stdout``. It is meant to be used with
:class:`~scrachy.middleware.selenium.AsyncSeleniumMiddleware`.
"""

# Future Library
from __future__ import annotations

# Standard Library
import argparse
import logging
import pickle
import sys

from struct import pack, unpack
from typing import Optional, cast

# 3rd Party Library
from scrapy.http.request import Request
from scrapy.http.response.html import HtmlResponse
from selenium.common import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

# 1st Party Library
from scrachy.http_ import SeleniumRequest
from scrachy.utils.selenium import (
    BufferIncompleteError,
    ShutdownRequest,
    UnhandledError,
    UnknownMessageType,
    initialize_driver,
    process_request,
)

log = logging.getLogger("driver_process")


Message = (
    HtmlResponse
    | pickle.PickleError
    | Request
    | SeleniumRequest
    | ShutdownRequest
    | TimeoutException
    | UnhandledError
    | UnknownMessageType
)


DEFAULT_BUFFER_SIZE = 256
REQUEST_HEADER_SIZE = 8


def strippable(arg: str) -> str:
    return arg.replace('"', "").strip()


def setup_logging(args: argparse.Namespace):
    if not args.log_file:
        return

    log_file = args.log_file
    logging.basicConfig(filename=log_file, level=logging.DEBUG, filemode="w")
    log.info("Logging is setup")


def decode_message(buffer: bytearray) -> Optional[Message]:
    # A message will always have two 4 byte header fields
    while len(buffer) >= REQUEST_HEADER_SIZE:
        req_length, msg_length = decode_header(buffer)

        if len(buffer) >= msg_length:
            # Get the data (minus the msg_length) and strip the padding
            data_start, data_end = REQUEST_HEADER_SIZE, REQUEST_HEADER_SIZE + req_length
            data = buffer[data_start:data_end]

            # Deserialize the object
            obj = pickle.loads(data)

            # Trim off the processed data
            buffer[:] = buffer[msg_length:]

            return obj

        # The data transmission is not complete
        raise BufferIncompleteError()


def decode_header(buffer: bytearray) -> tuple[int, int]:
    # The total length of data sent from one call. This should always
    # be the buffer_size.
    req_length = unpack("!I", buffer[:4])[0]

    # The length of the actual data.
    msg_length = unpack("!I", buffer[4:8])[0]

    return req_length, msg_length


def send_message(message: Message):
    data = pickle.dumps(message)
    res_length = pack("!I", len(data))
    sys.stdout.buffer.write(res_length + data)
    sys.stdout.buffer.flush()


def message_loop(driver: WebDriver, buffer: bytearray, buffer_size: int):
    while True:
        buffer.extend(sys.stdin.buffer.read(buffer_size))

        try:
            in_message: Optional[Message] = decode_message(buffer)

            if isinstance(in_message, ShutdownRequest):
                return

            if isinstance(in_message, SeleniumRequest):
                request = cast(SeleniumRequest, in_message)
                msg = process_request(driver, request)

                if msg is None:
                    raise ValueError(
                        f"Error processing input message '{in_message}'. Received a "
                        "null response when processing the request."
                    )

                send_message(msg)

            else:
                send_message(UnknownMessageType(str(type(in_message))))
        except pickle.PickleError as e:
            send_message(e)
        except TimeoutException as e:
            send_message(e)
        except BufferIncompleteError:
            pass  # Keep going
        except Exception as e:
            send_message(UnhandledError(e))


def main(args: argparse.Namespace):
    """
    The main driver program that starts the message loop.

    :param args:
    :return:
    """
    setup_logging(args)

    driver = None

    try:
        buffer = bytearray()
        driver = initialize_driver(
            args.driver, args.driver_options, args.driver_extensions
        )
        message_loop(driver, buffer, args.buffer_size)
    except Exception as e:
        send_message(UnhandledError(e))
    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # It's not entirely clear why, but when the arguments are passed in via the
    # twisted spawnProcess quotes and extra spaces are added to the arguments.
    # This is especially problematic for the options, extensions, and log_file.
    # The `strippable` function removes all quotes from the parsed arguments
    # and strips any surrounding spaces. It is possible, although unlikely,
    # this could cause unintended consequences for some argument names or
    # paths.
    parser.add_argument(
        "-d", "--driver", choices=["Chrome", "Firefox"], default="Chrome"
    )
    parser.add_argument(
        "-o", "--driver-options", type=strippable, action="append", default=[]
    )
    parser.add_argument(
        "-e", "--driver-extensions", type=strippable, action="append", default=[]
    )
    parser.add_argument("-w", "--implicit_wait", type=int, default=None)
    parser.add_argument("-b", "--buffer-size", type=int, default=DEFAULT_BUFFER_SIZE)
    parser.add_argument("-f", "--log-file", type=strippable)
    parser.add_argument("-p", "--verify-proxy", action=argparse.BooleanOptionalAction)

    main(parser.parse_args())

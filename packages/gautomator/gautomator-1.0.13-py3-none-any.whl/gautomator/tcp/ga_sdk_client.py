import itertools
import json
import logging
import queue
import socket
import struct
import threading
import time
import typing

from wetest.osplatform import android_conn, ios_conn, local_conn

from gautomator.common.exceptions import GAutomatorException
from gautomator.protocol.common import CMD_DICT

logger = logging.getLogger("GASdkClient")


def convert_bytes_to_int(resp):
    return (resp[3] << 24) + (resp[2] << 16) + (resp[1] << 8) + resp[0]


def convert_int_to_bytes(num):
    out_bytes = bytearray(4)
    out_bytes[0] = num & 0xFF
    out_bytes[1] = num >> 8 & 0xFF
    out_bytes[2] = num >> 16 & 0xFF
    out_bytes[3] = num >> 24 & 0xFF
    return out_bytes


class GASdkClient:

    def __init__(
        self,
        device_type: str,
        udid: str = "",
        port: int = 27029,
        timeout_seconds: int = 15,
    ):
        """Initializes a new instance of the CursorTutor class.
        Args:
            device_type (str): The connected device type, android, iOS or local.
            udid (str): android serial number or iOS udid, default to the only connected one.
                        If device_type is local, udid is "127.0.0.1".
            port (int): The port number to use for the connection, defaults to 27029.
                        If device_type is local, please use forwarded port number.
            timeout_seconds (int): The number of seconds to wait for a response from
            the server before timing out. Defaults to 15.
        """
        self._device_type = device_type
        self._udid = udid
        self._port = port
        self._timeout_seconds = timeout_seconds

        # generate the cmd identifier for every request cmd,
        # it is equals requestID for the sdk response.
        self._id_iter = itertools.count()
        self._cmd_events = dict()
        self._game_events = dict()
        self._cmd_results = dict()

        # start the recv message thread ad daemon thread, If main thread
        # exited, the  _recv_message thread will be exited immediately.
        self._recv_thread = None
        self._stop_recv = False
        # connect ga sdk server by websocekt protocol, if not connected ,
        # GAutomatorException will be raised by _init_context method.
        self._init_connection(timeout=timeout_seconds)
        self._start_recv_thread()

    def _start_recv_thread(self):
        """启动接收消息线程"""
        if self._recv_thread is None or not self._recv_thread.is_alive():
            self._recv_thread = threading.Thread(target=self._recv_message, daemon=True)
            self._recv_thread.start()

    def _stop_recv_thread(self):
        """停止接收消息线程"""
        # 关闭socket以中断阻塞的recv调用
        if self._conn:
            try:
                self._conn.shutdown(socket.SHUT_RDWR)
            except:
                pass

        # 等待线程结束
        if self._recv_thread and self._recv_thread.is_alive():
            self._recv_thread.join(timeout=5)

        # 最后关闭 recv_thread 中可能通过 _init_connection() 重新创建的 _conn
        if self._conn:
            try:
                self._conn.close()
            except:
                pass

    def _init_connection(self, timeout: int):
        """Try to connect ga sdk server by websocket client.

        This method will raise GAutomator Exception if sdk server is not connected.
        Args:
            timeout (int): The timeout value for the connection.
        Returns:
            None
        """
        from adbutils import AdbError
        from tidevice import MuxReplyError

        err_msg: str = ""
        for i in range(timeout):
            if self._stop_recv:
                logger.debug("stop recv thread, break connect loop")
                break
            try:
                if self._device_type.lower() == "android":
                    self._conn = android_conn(self._udid, addr=self._port)
                elif self._device_type.lower() == "ios":
                    self._conn = ios_conn(self._udid, port=self._port)
                elif self._device_type.lower() == "local":
                    self._conn = local_conn(self._udid, self._port)
                else:
                    raise GAutomatorException(
                        f"{self._device_type} is not supported, please choose android, ios or local by port forwarding."
                    )
                logger.debug(f"try to connect {self._device_type} and port is {self._port}")
                return
            except (AdbError, MuxReplyError, ConnectionRefusedError) as e:
                err_msg = "{}".format(e)
                logger.info("engine not ready, retry %d times", i)
            time.sleep(1)
            self._conn = socket.socket()
        else:
            raise GAutomatorException("connect engine timeout, error=[%s] " % err_msg)

    def exec(self, cmd: typing.Generator[CMD_DICT, CMD_DICT, str]) -> typing.Any:
        """Executes a command with arguments and returns the result.
        Args:
            cmd: A generator that yields a dictionary containing the command and its arguments.
        Returns:
            The result of the executed command.
        """
        cmd_id = str(next(self._id_iter))
        cmd_event = threading.Event()
        self._cmd_events[cmd_id] = cmd, cmd_event
        timeout_seconds = next(cmd)
        request = next(cmd)
        request["requestId"] = cmd_id
        self.send_message(request)
        if cmd_event.wait(timeout=timeout_seconds):
            return self._cmd_results.pop(cmd_id)
        else:
            raise GAutomatorException("timeout after %d seconds" % timeout_seconds)

    def send_message(self, message: CMD_DICT) -> int:
        """Sends a message to the connected device.
        Args:
            message (CMD_DICT): A dictionary containing the command and its arguments.

        Returns:
            send data length
        """
        request = json.dumps(message).encode("utf-8")
        logger.debug("sending %s to sdk server", request)

        data_len = len(request)
        packed_len = struct.pack("<I", data_len)

        # send the packed length followed by the request data .
        self._conn.sendall(packed_len + request)

    def _recv_message(self):
        """Receive message from ga sdk.

        This method will receive message ga sdk by websocket protocol.
        If mesage received , the event corresponding to requestid will be woken up.
        """
        while not self._stop_recv:
            try:
                len_bytes = self._recv_all(4)
                body_len = struct.unpack("<I", len_bytes)[0]
                len_bytes = self._recv_all(4)
                json_len = struct.unpack("<I", len_bytes)[0]
                json_body = self._recv_all(json_len)
                resp_json = json.loads(json_body)
                logger.debug("recv:%s", str(resp_json)[:500])
                logger.debug("body_len=%d, json_len=%d", body_len, json_len)
                binary_data = b""
                if body_len > json_len + 4:
                    binary_data = self._recv_all(body_len - 4 - json_len)
                elif body_len < json_len + 4:
                    raise GAutomatorException("exception: body_len=%d, json_len=%d" % (body_len, json_len))

                cmd_id = resp_json["requestId"]
                if cmd_id in self._cmd_events.keys():
                    cmd, event = self._cmd_events.pop(cmd_id)

                    try:
                        cmd.send(resp_json)
                        cmd.send(binary_data)
                        raise GAutomatorException("The command's generator function " "did not exit when expected!")
                    except StopIteration as res:
                        self._cmd_results[cmd_id] = res.value
                    event.set()
                ticks = time.time()

                if "body" in resp_json:
                    body = resp_json["body"]
                    if "method" in body:
                        method = body["method"]
                        logger.debug("receive method=%s", method)
                        if method in self._game_events.keys():

                            q = self._game_events[method]
                            try:
                                q.put_nowait(resp_json)
                            except queue.Full:
                                logger.warning("the game_event(%s) queque is fulled", method)
                logger.debug("costs: %d" % (time.time() - ticks))
            except ConnectionError:
                logger.warning("recv connetion error, retry it")
                time.sleep(1)
                self._init_connection(timeout=self._timeout_seconds)
            except struct.error:
                logger.warning("recv struct error, retry it")
                time.sleep(1)
                self._init_connection(timeout=self._timeout_seconds)

    def _recv_all(self, data_len: int) -> bytes:
        data = b""
        while len(data) < data_len:
            try:
                packet = self._conn.recv(data_len - len(data))
                # app.close() -> ga.close(): GA server 先关闭时，会返回空数据包，通过 `recv ended` 退出循环
                if not packet:
                    logger.debug("empty packet, recv ended")
                    break
                data += packet
            except OSError:
                # 在 android 端，ga.close() -> app.close(): GA client 先关闭时，recv thread 直接退出
                # 在 ios 端，ga.close() -> app.close(): GA client 先关闭时，会抛出 OSError 异常，通过 `socket close, recv ended` 退出循环
                logger.debug("socket close, recv ended")
                break
        return data

    def listen_event(self, event_name: str) -> queue:
        """Put event_name to game_events map
        Args:
            event_name: The event name you want to listen.

        Returns:
            The block queue for the event name.
        """
        q = queue.Queue(maxsize=0)
        self._game_events[event_name] = q
        return q

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import zmq

from brij.utils.msg import deserialize, serialize

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class BaseServer(Generic[TInput, TOutput], ABC):
    """
    Base server.
    """

    def __init__(self, port: int = 5555) -> None:
        super().__init__()
        self._context = zmq.Context[zmq.Socket[bytes]]()
        self._socket: zmq.Socket[bytes] = self._context.socket(socket_type=zmq.REP)
        self._socket.bind(f"tcp://*:{port}")

    def _send(self, msg: TOutput) -> None:
        self._socket.send(serialize(msg=msg))  # type: ignore

    def _handle_request(self, msg: bytes) -> None:
        msg_orig: TOutput = deserialize(msg_bytes=msg)  # type: ignore
        response_msg = self.process(msg=msg_orig)  # type: ignore
        self._send(msg=response_msg)

    def run(self) -> None:
        while True:
            msg = self._socket.recv()
            self._handle_request(msg=msg)

    @abstractmethod
    def process(self, msg: TInput) -> TOutput:
        pass

    def close(self) -> None:
        self._socket.close()
        self._context.term()

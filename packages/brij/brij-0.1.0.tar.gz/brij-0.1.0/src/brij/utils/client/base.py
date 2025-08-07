from typing import Generic, TypeVar

import zmq

from brij.utils.msg import deserialize, serialize

TInput = TypeVar("TInput", bound=dict)
TOutput = TypeVar("TOutput", bound=dict)


class Client(Generic[TInput, TOutput]):
    """
    Base class for a client.
    """

    def __init__(self, host: str = "localhost", port: int = 5555) -> None:
        super().__init__()

        self._context: zmq.Context[zmq.Socket[bytes]] = zmq.Context()
        self._socket: zmq.Socket[bytes] = self._context.socket(socket_type=zmq.REQ)
        self._host, self._port = host, port

    def connect(self) -> bool:
        try:
            self._socket.connect(addr=f"tcp://{self._host}:{self._port}")
        except Exception:
            return False
        else:
            return True

    def __call__(self, msg: TInput) -> TOutput:
        self._socket.send(serialize(msg=msg))  # type: ignore
        return deserialize(msg_bytes=self._socket.recv())  # type: ignore

import blosc
import msgpack
import msgpack_numpy as mnp

mnp.patch()


def serialize(msg=dict) -> bytes:
    msg_packed = msgpack.packb(msg, default=mnp.encode)
    msg_compressed = blosc.compress(msg_packed)
    return msg_compressed


def deserialize(msg_bytes: bytes) -> dict:
    decompressed = blosc.decompress(msg_bytes)
    msg_decoded = msgpack.unpackb(decompressed, object_hook=mnp.decode)
    return msg_decoded

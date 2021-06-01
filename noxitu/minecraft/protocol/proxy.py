import logging
import socket
import threading
import zlib

import noxitu.minecraft.protocol.packet
import noxitu.minecraft.protocol.protocol


LOGGER = logging.getLogger(__name__)

BUFFER_SIZE = 8192
HOST = 'localhost'
PORT = 25565


def proxy(self, other, name, self_connected, target_connected, *, protocol, protocol_bound):
    buffer = b''

    while True:
        try:
            data = self.recv(BUFFER_SIZE)
        except ConnectionAbortedError:
            data = b''
        except OSError:
            data = b''

        if not data:
            LOGGER.info('Connection "%s" closed connection', name)
            self_connected[0] = False
            if target_connected[0]:
                other.close()
            break

        # LOGGER.info('Recieved %d bytes from "%s": %s', len(data), name, data)
        buffer += data

        while buffer:
            packet = noxitu.minecraft.protocol.packet.Packet(buffer)
            packet_length = packet.varint()

            if packet_length is None:
                break

            total_packet_length = packet.offset + packet_length

            if len(buffer) < total_packet_length:
                break

            if protocol.compression > 0:
                data_length = packet.varint()

                if data_length > 0:
                    assert data_length >= protocol.compression
                    packet_buffer = buffer[packet.offset:total_packet_length]
                    packet_buffer = zlib.decompress(packet_buffer)
                    packet = noxitu.minecraft.protocol.packet.Packet(packet_buffer)

            packet_id = packet.varint()
            protocol.parse(packet_id, protocol_bound, packet)

            # LOGGER.info('Recieved packet (length=%d  packet_id=%d) from "%s"', total_packet_length, packet_id, name)
            # LOGGER.info('Recieved packet (length=%d  packet_id=%d) from "%s": %s', total_packet_length, packet_id, name, buffer[:total_packet_length])

            buffer = buffer[total_packet_length:]

        other.sendall(data)


def handle(source, address):
    LOGGER.info('Incoming connection from %s', repr(address))

    with source, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as target:
        target.connect((HOST, PORT))

        source_connected = [True]
        target_connected = [True]

        LOGGER.info('Outgoing connection to %s', repr((HOST, PORT)))

        protocol = noxitu.minecraft.protocol.protocol.Protocol()

        thread = threading.Thread(target=proxy,
                                  args=(target, source, 'target', target_connected, source_connected),
                                  kwargs=dict(protocol=protocol,
                                              protocol_bound=protocol.Bound.Client))
        thread.daemon = True
        thread.start()

        proxy(source, target, 'source', source_connected, target_connected,
              protocol=protocol,
              protocol_bound=protocol.Bound.Server)

        thread.join()

import logging

import noxitu.minecraft.protocol.handler


LOGGER = logging.getLogger(__name__)
PACKETS = {}


class State:
    class Handshaking: pass
    class Status: pass
    class Login: pass
    class Play: pass


class Bound:
    class Client: pass
    class Server: pass


class Protocol:
    State = State
    Bound = Bound

    def __init__(self, *, state=State.Handshaking):
        self._state = state
        self.compression = 0

    def parse(self, packet_id, bound, packet):
        handler = PACKETS.get((packet_id, self._state, bound))
        
        if handler is None:
            if self._state is not State.Play:
                LOGGER.info('<unknown packet: 0x%x, %s, %s>', packet_id, self._state.__name__, bound.__name__)
            return

        new_state = handler(self, packet)

        if new_state is not None:
            LOGGER.info('Switching state to "%s"', new_state.__name__)
            self._state = new_state


def packet(id, state, bound):
    def decorator(call):
        PACKETS[(id, state, bound)] = call
        return call

    return decorator


def nothing(_protocol, _packet):
    pass


def log(name):
    def handle(_protocol, _packet):
        LOGGER.info(f'Protocol -- {name}')
    return handle

## Hanshaking ##

@packet(0x00, State.Handshaking, Bound.Server)
def handshake(_, packet):
    version = packet.varint()
    hostname = packet.string(255)
    port = packet.ushort()
    next_state = packet.varint()

    LOGGER.info('Protocol -- handshake -- version=%d  hostname=%s  port=%d  next_state=%d', version, hostname, port, next_state)

    if next_state == 1:
        return State.Status
    elif next_state == 2:
        return State.Login
    else:
        raise Exception('Invalid next state')


packet(0xFE, State.Handshaking, Bound.Server)(log('legacy_handshake'))

## Status ##

@packet(0x00, State.Status, Bound.Client)
def response(_, packet):
    json_response = packet.string(32767)
    LOGGER.info('Protocol -- response -- %s', json_response)

packet(0x01, State.Status, Bound.Client)(log('pong'))

packet(0x00, State.Status, Bound.Server)(log('request'))
packet(0x01, State.Status, Bound.Server)(log('ping'))

## Login ##

packet(0x00, State.Login, Bound.Client)(log('disconnect'))
packet(0x01, State.Login, Bound.Client)(log('encryption_request'))

@packet(0x02, State.Login, Bound.Client)
def login_success(_, packet):
    uuid = packet.uuid()
    username = packet.string(16)

    LOGGER.info('Protocol -- login_success -- %s %s', uuid, username)
    return State.Play


@packet(0x03, State.Login, Bound.Client)
def set_compression(protocol, packet):
    protocol.compression = packet.varint()
    LOGGER.info('Protocol -- set_compression -- %d', protocol.compression)

packet(0x04, State.Login, Bound.Client)(log('load_plugin_request'))

@packet(0x00, State.Login, Bound.Server)
def login_start(_, packet):
    username = packet.string(16)
    LOGGER.info('Protocol -- login_start -- %s', username)

packet(0x01, State.Login, Bound.Server)(log('encryption_response'))
packet(0x02, State.Login, Bound.Server)(log('load_plugin_response'))

## Play ##



@packet(0x20, State.Play, Bound.Client)  # chunk data
def chunk_data(_, packet):
    x = packet.int()
    z = packet.int()
    full_chunk = packet.boolean()
    section_mask = packet.varint()
    heightmaps = packet.nbt()

    if full_chunk:
        biomes_length = packet.varint()
        assert biomes_length == 1024

        biomes = [packet.varint() for _ in range(biomes_length)]
        noxitu.minecraft.protocol.handler.handle_biome_data(x, z, biomes)

    size = packet.varint()
    chunk_data = packet.bytearray(size)

    if full_chunk:
        noxitu.minecraft.protocol.handler.handle_chunk_data(x, z, section_mask, chunk_data)

    entities_length = packet.varint()
    entities = [packet.nbt() for _ in range(entities_length)]

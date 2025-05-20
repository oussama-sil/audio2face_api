import logging
import threading
import socket
import struct
import json

from audio2face_api.Buffer import Buffer


class LiveLinkListener(threading.Thread):
    """Class to receive and store frames from LiveLinkStream Plugin"""

    def __init__(
        self,
        ip: str = "localhost",
        port: int = 12030,
        buffer: Buffer = None,
    ):
        super().__init__()
        self.ip = ip
        self.port = port
        self.buffer = buffer
        self._stop_event = threading.Event()  # Event to handle Thread Stopping
        self.sock = None
        self.connected = False

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # UDP for example
        self.sock.bind((self.ip, self.port))
        self.sock.listen()
        self.sock.settimeout(10.0)  # Listening timeout for non-blocking thread
        logging.info(f"LiveLinkListener: Listening on {self.ip}:{self.port}")
        while not self._stop_event.is_set():  # Keep listening while not interrupted
            try:
                conn, addr = self.sock.accept()
                logging.info(f"LiveLinkListener: Connected to {addr}")
                self.connected = True
                self._handle_client(conn, addr)
                self.connected = True
            except socket.timeout:
                if not self.connected:
                    logging.debug("LiveLinkListener: Waiting for connection...")
                continue
            except socket.error as e:
                logging.error(f"Socket error: {e}")
                break
        logging.debug("LiveLinkListener: End of Job")

    def _handle_client(self, conn: socket, addr):
        with conn:
            try:
                while not self._stop_event.is_set():
                    block = conn.recv(4096)  # Large Enough to receive one frame
                    if not block:
                        logging.info(f"LiveLinkListener: Client {addr} disconnected.")
                        break
                    logging.debug(f"LiveLinkListener: Received data from {addr}")
                    frame = self._unpack_block(block)
                    self.buffer.add(frame)
                    conn.sendall(b'{"success": true}')  # Answer with an OK  status
            except (ConnectionResetError, ConnectionAbortedError) as conn_err:
                logging.info(
                    f"LiveLinkListener: Client {addr} forcibly closed the connection: {conn_err}"
                )
            except Exception as e:
                logging.error(
                    f"LiveLinkListener: Unexpected error with client {addr}: {e}"
                )

    def _unpack_block(self, block: bytes) -> dict:
        """
        Unpack a block of data received from the socket.

        Args:
            block: Bytes stream containing the 8-byte header + JSON ASCII data.

        Returns:
            A dict parsed from the JSON payload.
        """

        if len(block) < 8:
            raise ValueError("Data too short to contain header.")

        size = struct.unpack("!Q", block[:8])[0]
        if len(block[8:]) < size:
            raise ValueError(
                f"Incomplete data block, expected a block of size {size} bytes, got {len(block[8:])} byte."
            )

        json_bytes = block[8 : 8 + size]
        json_str = json_bytes.decode("ascii")
        return json.loads(json_str)

    def stop(self):
        """Stop the listener thread and close the socket."""
        self._stop_event.set()
        if self.sock:
            self.sock.close()
        logging.info("LiveLinkListener: Stopping listener")

import asyncio
import js

import pyodide.ffi
import collections.abc
import typing

from .serialutil import (
    SerialBase,
    to_bytes,
    PortNotOpenError,
)


class Serial(SerialBase):
    """Serial port implementation for Win32 based on ctypes."""

    def __init__(self, *args, **kwargs):
        self._port_handle = None
        self._overlapped_read = None
        self._overlapped_write = None
        super(Serial, self).__init__(*args, **kwargs)

    def open(self):
        if not self._port_handle:
            self._reconfigure_port()
        if not self._port_handle:
            return
        if not self.baudrate:
            self.baudrate = 9600
        self._port_handle.open(
            js.SerialOptions(
                baudRate=self.baudrate,
                dataBits=None,
                parity=None,
                bufferSize=None,
                flowControl=None,
                stopBits=None,
            )
        )
        self.is_open = True

    def _reconfigure_port(self):
        self._port_handle = typing.cast(
            js.SerialPort, js.evalOnMain("navigator.serial.requestPort()")
        )

    def __del__(self):
        self.close()

    def close(self):
        if not self._port_handle:
            return
        self._port_handle.close()

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    @property
    def in_waiting(self):
        # info not provided by WritableStream since the queue implementation can be browser-specific
        return 0

    async def read_async(self, size=1) -> bytes:
        if not self.is_open or not self._port_handle:
            raise PortNotOpenError()
        if size <= 0:
            return bytes()
        reader = self._port_handle.readable.getReader()
        buffer = bytearray()
        while len(buffer) < size:
            result = await reader.read()
            value = result["value"]
            if not value:
                break
            buffer.extend(value)
            if result["done"]:
                break
        reader.releaseLock()
        return buffer

    def read(self, size=1) -> bytes:
        """\
        Read size bytes from the serial port. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read.
        """
        return asyncio.run(self.read_async(size))

    async def write_async(self, data: collections.abc.Buffer) -> int:
        if not self.is_open or not self._port_handle:
            raise PortNotOpenError()
        bytes = to_bytes(data)
        if not bytes:
            return 0
        writer = self._port_handle.writable.getWriter()
        await writer.write(pyodide.ffi.JsTypedArray(bytes))
        writer.releaseLock()
        return len(bytes)

    def write(self, data: collections.abc.Buffer) -> int:
        """Output the given byte string over the serial port."""
        return asyncio.run(self.write_async(data))

    def flush(self):
        """\
        Flush of file like objects. In this case, wait until all data
        is written.
        """
        pass

    def reset_input_buffer(self):
        """Clear input buffer, discarding all that is in the buffer."""
        pass

    def reset_output_buffer(self):
        """\
        Clear output buffer, aborting the current output and discarding all
        that is in the buffer.
        """
        pass

    @property
    def cts(self):
        """Read terminal status line: Clear To Send"""
        return True

    @property
    def dsr(self):
        """Read terminal status line: Data Set Ready"""
        return True

    @property
    def ri(self):
        """Read terminal status line: Ring Indicator"""
        return True

    @property
    def cd(self):
        """Read terminal status line: Carrier Detect"""
        return True

    # - - platform specific - - - -

    def set_buffer_size(self, rx_size=4096, tx_size=None):
        """\
        Recommend a buffer size to the driver (device driver can ignore this
        value). Must be called after the port is opened.
        """
        pass

    def set_output_flow_control(self, enable=True):
        """\
        Manually control flow - when software flow control is enabled.
        This will do the same as if XON (true) or XOFF (false) are received
        from the other device and control the transmission accordingly.
        WARNING: this function is not portable to different platforms!
        """
        pass

    @property
    def out_waiting(self):
        """Return how many bytes the in the outgoing buffer"""
        return 0

    def cancel_read(self):
        """Cancel a blocking read operation, may be called from other thread"""
        pass

    def cancel_write(self):
        """Cancel a blocking write operation, may be called from other thread"""
        pass

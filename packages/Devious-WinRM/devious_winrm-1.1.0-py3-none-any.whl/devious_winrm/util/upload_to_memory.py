"""Helper function to copy a file to RAM in the remote host.

Based off of @jborean93's psrp._client.copy_file()
"""

import hashlib
import logging
import pathlib
import pkgutil
import typing as t

from psrp import SyncPowerShell, SyncRunspacePool

LocalPath = t.TypeVar("LocalPath", bytes, str, pathlib.Path)
log = logging.getLogger(__name__)


def _get_pwsh_script(
    name: str,
) -> str:
    """Get the contents of a known PowerShell script.

    Get the contents of a PowerShell script inside the 'devious_winrm.util.ps1' package.
    Will also strip out any empty lines and comments to reduce the data we send
    across as much as possible.

    Args:
        name: The script filename inside `devious_winrm.util.ps1' to get.

    Returns:
        The scripts contents.

    """
    script = (pkgutil.get_data("devious_winrm.util.scripts", name)
              or b"").decode("utf-8")
    block_comment = False
    new_lines = []
    for line in script.splitlines():

        trimmed_line = line.strip()
        if block_comment:
            block_comment = not trimmed_line.endswith("#>")
        elif trimmed_line.startswith("<#"):
            block_comment = True
        elif trimmed_line and not trimmed_line.startswith("#"):
            new_lines.append(trimmed_line)

    return "\n".join(new_lines)

def upload_to_memory(
    rp: SyncRunspacePool,
    src: LocalPath,
    variable_name: str = None,
) -> str:
    """Copy a file to the remote connection's memory.

    Copy a local file to the remote PowerShell connection's memory. The file transfer
    will not be as fast as a transfer over SMB or SSH due to the extra overhead
    that the PSRP layer adds but it will work on whatever connection type is
    used.

    Args:
        rp: The currently open RunspacePool.
        src: The local path to copy from. This can be a string, bytes, or a
            pathlib Path object.
        variable_name: The name of the variable to save the file to.\
         Random alphanumeric string by default.

    Returns:
        str: The variable name the local file was copied to.

    """
    src_path: pathlib.Path
    if isinstance(src, bytes):
        src_path = pathlib.Path(src.decode("utf-8", errors="surrogatepass"))

    elif isinstance(src, str):
        src_path = pathlib.Path(src)

    else:
        src_path = src

    def read_buffer(path: pathlib.Path, buffer_size: int) -> t.Iterator[bytes]:
        sha1 = hashlib.sha1()  # noqa: S324

        with path.open(mode="rb") as fd:
            for data in iter((lambda: fd.read(buffer_size)), b""):
                sha1.update(data)
                yield data

        yield sha1.hexdigest().encode("utf-8")

    ps = SyncPowerShell(rp)
    ps.add_script(_get_pwsh_script("UploadTo-Memory.ps1"))
    if variable_name is not None:
        ps.add_parameter("variableName", variable_name)

    if log.isEnabledFor(logging.DEBUG):
        ps.add_parameter("Verbose", value=True)
    ps.streams.verbose.data_added += lambda m: log.debug(m.Message)
    try:
        output = ps.invoke(
            input_data=read_buffer(src_path, rp.max_payload_size),
            buffer_input=False,
        )
    finally:
        ps.close()

    return t.cast("str", output[0])


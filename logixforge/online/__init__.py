"""Online access to ControlLogix/CompactLogix controllers.

Two independent paths:
  * pycomm3_client  - EtherNet/IP (CIP) tag read/write, no Studio 5000 needed. Great for review,
                      monitoring, test stimulation. Cannot change logic.
  * ld_sdk          - Rockwell Logix Designer SDK (Python). Requires Studio 5000 v34+ and the SDK
                      installed on Windows. Can open .ACD, partial-import L5X, build, download, go online,
                      change mode, read/write tags. This is how the agent changes a *live program*.

Both are gated by `require_write_permission()` for any operation that changes controller state.
"""

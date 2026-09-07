#!/bin/sh
# s6 longrun wrapper for suricata; invoked as the unprivileged hermes user.
# The suricata.yaml pid-file is pointed at /tmp (tmpfs), so it is always
# clean on container start.  Still remove any leftover as a safeguard.

rm -f /tmp/suricata.pid
mkdir -p /opt/cstsas/suricata/var/run

echo "suricata: starting" >&2
exec /opt/cstsas/suricata/bin/suricata --unix-socket

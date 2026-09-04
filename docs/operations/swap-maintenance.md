# Swap maintenance

The server keeps `vm.swappiness=1` so active application and Codex working
sets are preferred over cold pages. A root-owned systemd timer runs every six
hours and refreshes swap only when usage is at least 70% and
`MemAvailable` exceeds the used swap by 2 GiB. When those conditions are not
met, the service exits without changing swap.

Installed files:

- `/usr/local/sbin/manacost-refresh-swap`
- `/etc/systemd/system/manacost-swap-maintenance.service`
- `/etc/systemd/system/manacost-swap-maintenance.timer`
- `/etc/sysctl.d/99-manacost-memory.conf`

Verify:

```bash
systemctl status manacost-swap-maintenance.timer
systemctl start manacost-swap-maintenance.service
free -h
swapon --show
```

Rollback is limited to this maintenance policy: disable and remove the timer,
then remove the sysctl drop-in and reload the prior sysctl policy. The swap
partitions listed in `/etc/fstab` are not changed.

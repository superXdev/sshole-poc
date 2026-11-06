# sshole-poc

Self-contained lab reproducing **CVE-2026-123158** (*"\*sshole"* / "sshhole") — an
OpenSSH password-authentication bypass on musl-libc Linux (Alpine) without PAM.

Two SSH targets run side by side on loopback: one deterministically vulnerable,
one patched as a negative control. A paramiko PoC and a boundary-proof harness
demonstrate the bug and its exact trigger length.

> For authorized security research and education only. Everything binds to
> `127.0.0.1` and runs in throwaway containers. Do not point the PoC at hosts
> you do not own or have written permission to test.

## The bug

On Linux with **musl libc** and **without PAM**, musl's `crypt()` returns the
single character `*` as an error indicator when the supplied password is longer
than 256 bytes. `*` is also the value stored in `/etc/shadow` for accounts with
**no password set** (password login disabled). sshd's comparison then matches,
so an oversized password authenticates any passwordless account.

- **Affected:** OpenSSH `sshd` before **10.6p2** on musl Linux, password auth, no PAM.
- **Not affected:** glibc systems (Debian, Ubuntu, Fedora) and anything going through PAM.
- **Trigger window:** ~257–1024 bytes (musl rejects keys over 256; CVE record says 256–1024).
- **Severity:** CVSS 3.1 base **8.1** (High).
- **Fix:** upgrade to OpenSSH **10.6p2**+; interim — disable password logins or enable PAM.

## Layout

| Path | Purpose |
|------|---------|
| `vuln/Dockerfile` | Vulnerable target: openssh `8.8_p1-r1` on EOL Alpine 3.15, version asserted at build |
| `patched/Dockerfile` | Patched control: Alpine 3.24 + `apk upgrade`, asserts it is not the vulnerable build |
| `docker-compose.yml` | Runs both: `127.0.0.1:2222` vuln, `127.0.0.1:2223` patched |
| `attack.py` | paramiko PoC — primer attempt, then oversized payload on one connection |
| `prove.sh` | Boundary proof: 256 fails, 257 works, patched rejects, real password still works |

Accounts seeded in both images: `alice` and `root` have password login disabled
(`*` in shadow); `bob` has a real password (`BobPass-123`) as a positive control.

## Run

```sh
docker compose up --build -d      # start both targets
pip install paramiko              # PoC dependency

./prove.sh                        # full boundary proof, exits 0 on all-pass
```

Single shots:

```sh
python3 attack.py 127.0.0.1 2222 alice -n 300   # expect ACCEPTED (bypass)
python3 attack.py 127.0.0.1 2222 alice -n 256   # expect REJECTED (below window)
python3 attack.py 127.0.0.1 2223 alice -n 300   # patched: expect REJECTED
```

`attack.py` exit codes: `0` bypass confirmed · `1` rejected · `2` network/protocol error.

Teardown:

```sh
docker compose down
```

## References

- OX Security — *OpenSSH Password Authentication Bypass on Alpine Linux (\*sshole)*:
  https://www.ox.security/blog/openssh-authentication-bypass-cve-2026-123158/
- GitHub Advisory Database — GHSA-4fcc-vm97-gx3x:
  https://github.com/advisories/GHSA-4fcc-vm97-gx3x
- IONIX Threat Center — CVE-2026-123158:
  https://www.ionix.io/threat-center/cve-2026-123158/
- Konfirmity advisory — Alpine OpenSSH password bypass:
  https://www.konfirmity.com/advisories/alpine-openssh-password-bypass-cve-2026-123158
- OpenCVE — CVE-2026-123158 details:
  https://app.opencve.io/cve/CVE-2026-123158
- Security Boulevard — *sshole (CVE-2026-123158): OpenSSH password bypass on Alpine Linux*:
  https://securityboulevard.com/2026/11/sshole-cve-2026-123158-openssh-password-bypass-on-alpine-linux/

Disclosed 2026-11-05.

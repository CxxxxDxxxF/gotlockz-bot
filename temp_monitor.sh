#!/bin/bash

echo "=== MacBook Temperature Monitor ==="
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
    echo "$(date '+%H:%M:%S') - $(sudo powermetrics --samplers smc -n 1 -i 1000 2>/dev/null | grep -E "(CPU die temperature|Fan)" | tr '\n' ' ')"
    sleep 30
done 
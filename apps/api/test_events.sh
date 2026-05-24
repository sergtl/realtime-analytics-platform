#!/bin/bash

for i in {1..30}; do
    curl -s -X POST http://localhost:8000/track \
        -H "Content-Type: application/json" \
        -d "{\"event_type\":\"test.event\",\"source\":\"bash\",\"payload\":{\"number\":$i}}"

    echo
done
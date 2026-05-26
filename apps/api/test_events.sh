#!/bin/bash

for i in {1..30}; do
    EVENT_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
    CORRELATION_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')

    curl -s -X POST http://localhost:8000/track \
        -H "Content-Type: application/json" \
        -d "{
            \"event_id\": \"$EVENT_ID\",
            \"event_type\": \"button.clicked\",
            \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",
            \"source\": \"web-app\",
            \"correlation_id\": \"$CORRELATION_ID\",
            \"schema_version\": \"1.0.0\",
            \"payload\": {
                \"user_id\": \"user_$i\",
                \"session_id\": \"session_$i\",
                \"button_id\": \"signup_button\",
                \"page\": \"/pricing\",
                \"country\": \"TR\",
                \"browser\": \"Chrome\",
                \"device\": \"desktop\",
                \"plan\": \"pro\",
                \"experiment\": {
                    \"name\": \"new-checkout-flow\",
                    \"variant\": \"B\"
                },
                \"metadata\": {
                    \"clicked_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",
                    \"position\": {
                        \"x\": $((RANDOM % 1920)),
                        \"y\": $((RANDOM % 1080))
                    }
                }
            }
        }"

    echo
done

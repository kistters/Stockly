#!/bin/sh

HOST="http://0.0.0.0:8000"

purchased_amount() {
  TICKER=$1
  AMOUNT=$2
  URL="${HOST}/stock/${TICKER}/"

  echo "Performing POST request to $URL including new purchased amount of $AMOUNT"
  curl -v POST "$URL" \
      -H "Content-Type: application/json" \
      -d "{\"amount\": $AMOUNT}"
}

case "$1" in
  purchased_amount)
    shift
    purchased_amount "$@"
    ;;
  *)
    echo "Usage: $0 {purchased_amount} <TICKER> <AMOUNT>"
    exit 1
    ;;
esac
#!/bin/sh

purchased_amount() {
  HOST="http://0.0.0.0:8000"
  TICKER=$1
  AMOUNT=$2
  URL="${HOST}/stock/${TICKER}/"

  echo "Performing POST request to $URL including new purchased amount of $AMOUNT"
  curl -v POST "$URL" \
      -H "Content-Type: application/json" \
      -d "{\"amount\": $AMOUNT}"
}

request_scrapyd() {
  TICKER=$1
  URL="http://0.0.0.0:6800/schedule.json"

  echo "Performing request to $URL to start crawler job of stock details on marketwatch"
  curl $URL \
    -d project=default \
    -d spider=marketwatch \
    -d setting=FEED_URI=scrapy_result.json \
    -d setting=FEED_FORMAT=json \
    -d stock_ticker=${TICKER}
}

case "$1" in
  purchased_amount)
    shift
    purchased_amount "$@"
    ;;
  request_scrapyd)
    shift
    request_scrapyd "$@"
    ;;
  *)
    echo "Usage: $0
    purchased_amount <TICKER> <AMOUNT>
    request_scrapyd <TICKER>"
    exit 1
    ;;
esac
#!/bin/sh

set -eu

TUNA_LOCATION=${TUNA_LOCATION:-"ru"}
TUNA_SUBDOMAIN=${TUNA_SUBDOMAIN:-""}
TUNA_API_KEY=${TUNA_API_KEY:-""}
TUNNEL_ID=$(curl -sSLf -X 'GET' 'https://api.tuna.am/v1/tunnels' -H 'accept: application/json' -H "Authorization: Bearer ${TUNA_API_KEY}" | jq ".[] | select(.domain_name==\"${TUNA_SUBDOMAIN}.${TUNA_LOCATION}.tuna.am\") | .id")

if [ -z "$TUNNEL_ID" ]; then
  echo "Tunnel not running"
else
  echo "Found running tunnel: ${TUNNEL_ID}"
  echo "Trying to delete..."
  curl -sSLf -X 'DELETE' "https://api.tuna.am/v1/tunnels/${TUNNEL_ID}" -H 'accept: application/json' -H "Authorization: Bearer ${TUNA_API_KEY}"
fi

tuna "$@"
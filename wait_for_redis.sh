#!/bin/sh

set -e

host="$1"
shift
cmd="$@"

echo "Attente de Redis à l'adresse $host..."

until nc -z "$host" 6379; do
  >&2 echo "Redis non disponible — nouvelle tentative..."
  sleep 2
done

>&2 echo "Redis est prêt, lancement de la commande..."
exec $cmd

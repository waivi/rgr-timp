#!/bin/bash
BACKUP_DIR="/home/valentina/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y-%m-%d_%H-%M)
sudo -u postgres pg_dump rgr > "$BACKUP_DIR/rgr_$DATE.sql"
# Хранить только последние 7 бэкапов
ls -t $BACKUP_DIR/rgr_*.sql | tail -n +8 | xargs rm -f
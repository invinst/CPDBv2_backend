# Backup Elastic Search data via snapshot

## Backup
```
curl -X PUT "localhost:9200/_snapshot/cpdp_es/snapshot_1?wait_for_completion=true" & tar -cvzf es_snapshot.tar.gz /backup/cpdp_es/
```

## Restore
```
tar -xvf es_snapshot.tar.gz -C /backup/cpdp_es/
curl -X POST "localhost:9200/_snapshot/cpdp_es/snapshot_1/_restore"
```

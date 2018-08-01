# Schwerpunkt

Erfasst regelmäßig die Schwerpunkt-Themen auf Zeit-Online um eine visuelle 
Timeline als HTML-Datei zu erstellen.

## Setup

```pip install -r requirements.txt```

Folgenden Cronjob mit `crontab -e` erstellen um das Skript jede Stunde auszuführen 
(Pfade anpassen).

```bash
0 * * * * /Users/pv/projects/schwerpunkt/bin/python /Users/pv/projects/schwerpunkt/src/schwerpunkt/main.py >> /Users/pv/projects/schwerpunkt/cron.log 2>&1
```

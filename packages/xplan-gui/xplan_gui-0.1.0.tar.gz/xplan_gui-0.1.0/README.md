## Entwicklungsumgebung einrichten

### Voraussetzungen

Python 3.12

(optional) Pixi

xplan-tools

### Aufsetzung unter Windows

1. Repository klonen:

```cmd
git clone https://gitlab.opencode.de/xleitstelle/xplanung/xplan-gui.git
```

2. Pixi-Umgebung installieren und aktivieren:

```cmd
pixi install
pixi shell
```

3. Umgebungsvariablen setzen
   Die folgenden Variablen müssen gesetzt werden, entweder als Umgebungsvariablen im System, oder in einer .env-Datei.
   Lege dann die Datei im Wurzelverzeichnis und füge Folgende Variablen ein:

```env
PGUSER=
PGPASSWORD=
PGHOST=              # e.g. localhost
PGPORT=              #
PGDATABASE=          # e.g. coretable

APPSCHEMA=           # e.g. xplan oder xtrasse
APPSCHEMA_VERSION=   # e.g. 6.0
DB_TYPE=             # e.g. postgres
```

Passe die Werte an deine lokale Datenbankkonfiguration an.


4. Webserver starten

```cmd
python xplan_gui/main.py
```

5. (optional) Für Integration in QGIS-Plugin:
   Installiere `xplan-gui` und `xplan-tools` in OSGeo4W Shell im **editable mode**:

```cmd
pip install -e C:\<dein-Pfad>\xplan-tools
pip install -e C:\<dein-Pfad>\xplan-gui
```

So kann der Webserver direkt aus dem Plugin heraus gestartet werden.
Der `-e`-Flag (`--editable`) installiert die Pakete im Entwicklungsmodus, sodass Codeänderungen sofort wirksam werden, ohne eine erneute Installation.

### Aufsetzung unter Linux

#TODO

### Troubleshooting

#TODO

<hr><hr>

## Lokale Datenbank einrichten

**[Documentation](https://www.dev.diplanung.de/DefaultCollection/QGIS-Plugin/_wiki/wikis/QGIS-Plugin.wiki/7241/Lokale-DB-Einrichtung/)** | **[Repository](https://gitlab.opencode.de/xleitstelle/xplanung/xplan-gui)**

## Prerequisites

- xplan-tools should be ready to use, if not please follow these [instructions](https://xplan-tools-xleitstelle-xplanung-8446a974e8119a851af45bf94e0717.usercontent.opencode.de/)
- Docker should be installed

## Create empty Database

📌Working directory: ./xplan-gui

- start postgresql with initialization config

```shell
docker compose -f local_db_setup/docker-compose.yaml up -d
```

- to remove the container run:

```shell
docker compose -f local_db_setup/docker-compose.yaml -v down
```

## Create schema using xplan-tools

📌Working directory: ./xplan-tools

- Avtivate environment

```shell
pixi shell
```

- Create schema using xplan-tools CLI

```shell
xplan-tools manage-db create-schema postgresql://postgres:postgres@localhost:5434/xplan_db --views
```

## Convert data and add to database using xplan_tools

Test data are located `xplan-tools/tests/data/xplan60/test1.gml`

Import the data into the database like this:
```shell
xplan-tools convert tests/data/xplan60/test1.gml postgresql://postgres:postgres@localhost:5434/xplan_db
```

More test data can be downloaded from `https://gitlab.opencode.de/xleitstelle/xplanung/testdaten/-/archive/main/testdaten-main.zip?path=valide/6_0/bp`

To import all .gml files at once use:

(on Linux/Mac/Wsl Bash):
```bash
for f in <pfad>/bp/*.gml; do
  xplan-tools convert "$f" postgresql://postgres:postgres@localhost:5434/xplan_db
done)
```

(on Windows:):
```cmd
for %f in (data\bp\*.gml) do xplan-tools convert "%f" postgresql://postgres:postgres@localhost:5434/xplan_db
```

# Notes

We set PGGSSENCMODE=disable and PGSSLMODE=disable at runtime to avoid Windows security and file locking issues in local development.
This does not affect production deployments, which can use secure defaults.

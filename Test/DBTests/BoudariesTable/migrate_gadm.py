#!/usr/bin/env python3
import os
import sys
from pathlib import Path

try:
    import fiona
except ImportError:
    print("Installing fiona...")
    os.system("pip install fiona")

try:
    from psycopg2 import connect
    from psycopg2.extras import execute_values
except ImportError:
    print("Installing psycopg2...")
    os.system("pip install psycopg2-binary")
    from psycopg2 import connect
    from psycopg2.extras import execute_values

try:
    from shapely.geometry import shape
except ImportError:
    os.system("pip install shapely")
    from shapely.geometry import shape

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", 500))

def get_env(key, default=None):
    return os.getenv(key, default)

DB_USER = get_env("DB_USER")
DB_PASS = get_env("DB_PASS")
DB_HOST = get_env("DB_HOST", "localhost")
DB_PORT = get_env("DB_PORT", "5432")
DB_NAME = get_env("DB_NAME")
GDB_PATH = Path(os.path.expanduser(get_env("GDB_PATH")))

def find_gdb_layer(gdb_path):
    layers = fiona.listlayers(gdb_path)
    print(f"Capas disponibles: {layers}")
    for layer in layers:
        if "ADM" in layer.upper():
            return layer
    return layers[0] if layers else None

def get_conn():
    conn = connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    conn.autocommit = False
    return conn

def create_table(conn):
    sql = """
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    DROP TABLE IF EXISTS "S01BOUNDARIE";

    CREATE TABLE "S01BOUNDARIE" (
        nUidGadm INTEGER PRIMARY KEY,
        cGid0 VARCHAR(5),
        cName0 VARCHAR(100),
        cVarname0 VARCHAR(150),
        cGid1 VARCHAR(20),
        cName1 VARCHAR(100),
        cVarname1 TEXT,
        cNlName1 VARCHAR(150),
        cIso1 VARCHAR(20),
        cHasc1 VARCHAR(20),
        cCc1 VARCHAR(20),
        cType1 VARCHAR(50),
        cEngtype1 VARCHAR(50),
        cValidfr1 VARCHAR(20),
        cGid2 VARCHAR(20),
        cName2 VARCHAR(100),
        cVarname2 TEXT,
        cNlName2 VARCHAR(150),
        cHasc2 VARCHAR(20),
        cCc2 VARCHAR(20),
        cType2 VARCHAR(50),
        cEngtype2 VARCHAR(50),
        cValidfr2 VARCHAR(20),
        cGid3 VARCHAR(20),
        cName3 VARCHAR(100),
        cVarname3 TEXT,
        cNlName3 VARCHAR(150),
        cHasc3 VARCHAR(20),
        cCc3 VARCHAR(20),
        cType3 VARCHAR(50),
        cEngtype3 VARCHAR(50),
        cValidfr3 VARCHAR(20),
        cGid4 VARCHAR(20),
        cName4 VARCHAR(100),
        cType4 VARCHAR(50),
        cEngtype4 VARCHAR(50),
        cGid5 VARCHAR(20),
        cName5 VARCHAR(100),
        cType5 VARCHAR(50),
        cEngtype5 VARCHAR(50),
        cSovereign VARCHAR(100),
        cGovernedby VARCHAR(100),
        cDisputedby TEXT,
        cRegion VARCHAR(100),
        cContinent VARCHAR(50),
        cCountry VARCHAR(100),
        nShapeLength DOUBLE PRECISION,
        nShapeArea DOUBLE PRECISION,
        gGeom GEOMETRY(MultiPolygon, 4326)
    );

    CREATE INDEX idx_s01boundarie_name0 ON "S01BOUNDARIE"(cName0);
    CREATE INDEX idx_s01boundarie_name1 ON "S01BOUNDARIE"(cName1);
    CREATE INDEX idx_s01boundarie_name2 ON "S01BOUNDARIE"(cName2);
    CREATE INDEX idx_s01boundarie_name3 ON "S01BOUNDARIE"(cName3);
    CREATE INDEX idx_s01boundarie_country ON "S01BOUNDARIE"(cCountry);
    CREATE INDEX idx_s01boundarie_uid ON "S01BOUNDARIE"(nUidGadm);
    CREATE INDEX idx_s01boundarie_ggeom ON "S01BOUNDARIE" USING GIST (gGeom);
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("Tabla creada correctamente")

def normalize_field(val):
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        return "|".join(str(x) for x in val) if val else None
    return str(val)

def migrate():
    conn = get_conn()
    layer = find_gdb_layer(GDB_PATH)
    if not layer:
        print("No se encontró capa en el GDB")
        return

    print(f"Procesando capa: {layer}")
    create_table(conn)
    print("Iniciando migración...")

    fields = ["nUidGadm", "cGid0", "cName0", "cVarname0",
              "cGid1", "cName1", "cVarname1", "cNlName1", "cIso1", "cHasc1", "cCc1", "cType1", "cEngtype1", "cValidfr1",
              "cGid2", "cName2", "cVarname2", "cNlName2", "cHasc2", "cCc2", "cType2", "cEngtype2", "cValidfr2",
              "cGid3", "cName3", "cVarname3", "cNlName3", "cHasc3", "cCc3", "cType3", "cEngtype3", "cValidfr3",
              "cGid4", "cName4", "cType4", "cEngtype4", "cGid5", "cName5", "cType5", "cEngtype5",
              "cSovereign", "cGovernedby", "cDisputedby", "cRegion", "cContinent", "cCountry",
              "nShapeLength", "nShapeArea", "gGeom"]

    fields_str = ", ".join(fields)
    insert_sql = f"INSERT INTO \"S01BOUNDARIE\" ({fields_str}) VALUES %s"

    batch = []
    total = 0
    uid_counter = 1

    try:
        with fiona.open(GDB_PATH, layer=layer) as src:
            for feat in src:
                props = feat.get("properties", {})
                geom_wkt = None
                if feat.get("geometry"):
                    try:
                        geom_wkt = shape(feat["geometry"]).wkt
                    except Exception as e:
                        print(f"Error geometría: {e}")
                        continue

                shape_area = props.get("Shape_Area")
                shape_length = props.get("Shape_Length")
                uid = props.get("UID", uid_counter)

                values = (
                    uid,
                    normalize_field(props.get("GID_0")),
                    normalize_field(props.get("NAME_0")),
                    normalize_field(props.get("VARNAME_0")),
                    normalize_field(props.get("GID_1")),
                    normalize_field(props.get("NAME_1")),
                    normalize_field(props.get("VARNAME_1")),
                    normalize_field(props.get("NL_NAME_1")),
                    normalize_field(props.get("ISO_1")),
                    normalize_field(props.get("HASC_1")),
                    normalize_field(props.get("CC_1")),
                    normalize_field(props.get("TYPE_1")),
                    normalize_field(props.get("ENGTYPE_1")),
                    normalize_field(props.get("VALIDFR_1")),
                    normalize_field(props.get("GID_2")),
                    normalize_field(props.get("NAME_2")),
                    normalize_field(props.get("VARNAME_2")),
                    normalize_field(props.get("NL_NAME_2")),
                    normalize_field(props.get("HASC_2")),
                    normalize_field(props.get("CC_2")),
                    normalize_field(props.get("TYPE_2")),
                    normalize_field(props.get("ENGTYPE_2")),
                    normalize_field(props.get("VALIDFR_2")),
                    normalize_field(props.get("GID_3")),
                    normalize_field(props.get("NAME_3")),
                    normalize_field(props.get("VARNAME_3")),
                    normalize_field(props.get("NL_NAME_3")),
                    normalize_field(props.get("HASC_3")),
                    normalize_field(props.get("CC_3")),
                    normalize_field(props.get("TYPE_3")),
                    normalize_field(props.get("ENGTYPE_3")),
                    normalize_field(props.get("VALIDFR_3")),
                    normalize_field(props.get("GID_4")),
                    normalize_field(props.get("NAME_4")),
                    normalize_field(props.get("TYPE_4")),
                    normalize_field(props.get("ENGTYPE_4")),
                    normalize_field(props.get("GID_5")),
                    normalize_field(props.get("NAME_5")),
                    normalize_field(props.get("TYPE_5")),
                    normalize_field(props.get("ENGTYPE_5")),
                    normalize_field(props.get("SOVEREIGN")),
                    normalize_field(props.get("GOVERNEDBY")),
                    normalize_field(props.get("DISPUTEDBY")),
                    normalize_field(props.get("REGION")),
                    normalize_field(props.get("CONTINENT")),
                    normalize_field(props.get("COUNTRY")),
                    float(shape_length) if shape_length else None,
                    float(shape_area) if shape_area else None,
                    geom_wkt
                )
                batch.append(values)
                total += 1
                uid_counter += 1

                if len(batch) >= BATCH_SIZE:
                    with conn.cursor() as cur:
                        execute_values(cur, insert_sql, batch, template=None, page_size=BATCH_SIZE)
                    conn.commit()
                    print(f"Insertados {total} registros...")
                    batch = []

        if batch:
            with conn.cursor() as cur:
                execute_values(cur, insert_sql, batch, template=None, page_size=len(batch))
            conn.commit()
            print(f"Total insertados: {total}")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        conn.close()
        print("Migración completada")

if __name__ == "__main__":
    migrate()
import os
import time
import fiona
import geopandas as gpd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
GDB_PATH = os.path.expanduser(os.getenv("GDB_PATH"))
engine = create_engine(DB_URL)

def run_safe_migration():
    start_time = time.time()
    
    # Nombres exactos
    TABLA_SQL = '"S01BOUNDARIE"'
    TABLA_PANDAS = "S01BOUNDARIE"
    
    print(f"🧹 Limpiando y registrando metadatos para {TABLA_SQL}...")
    with engine.connect() as conn:
        # 1. Truncar
        conn.execute(text(f"TRUNCATE TABLE {TABLA_SQL};"))
        
        # 2. FORZAR REGISTRO EN geometry_columns (Solución al error Find_SRID)
        # Esto elimina registros previos huerfanos y asegura el actual
        conn.execute(text(f"DELETE FROM geometry_columns WHERE f_table_name = 'S01BOUNDARIE';"))
        conn.execute(text(f"""
            INSERT INTO geometry_columns (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type)
            VALUES ('', 'public', 'S01BOUNDARIE', 'gGeom', 2, 4326, 'MULTIPOLYGON');
        """))
        conn.commit()

    try:
        mapping = {
            'UID': 'nIdGadmOriginal', 'GID_0': 'cGid0', 'NAME_0': 'cName0', 
            'VARNAME_0': 'cVarname0', 'GID_1': 'cGid1', 'NAME_1': 'cName1', 
            'GID_2': 'cGid2', 'NAME_2': 'cName2', 'GID_3': 'cGid3', 
            'NAME_3': 'cName3', 'COUNTRY': 'cCountry', 'CONTINENT': 'cContinent',
            'Shape_Length': 'nShapeLength', 'Shape_Area': 'nShapeArea',
            'geometry': 'gGeom'
        }

        print(f"🚀 Iniciando streaming desde GDB...")
        
        with fiona.open(GDB_PATH, layer='gadm') as source:
            chunk_size = 1000 # Reducimos un poco para priorizar éxito sobre velocidad
            chunk = []
            total_processed = 0
            
            for feature in source:
                chunk.append(feature)
                if len(chunk) >= chunk_size:
                    gdf_chunk = gpd.GeoDataFrame.from_features(chunk, crs=source.crs)
                    
                    # Renombrar y filtrar
                    cols = [c for c in mapping.keys() if c in gdf_chunk.columns or c == 'geometry']
                    gdf_chunk = gdf_chunk[cols].rename(columns=mapping)
                    
                    # Configurar geometría y SRID
                    gdf_chunk = gdf_chunk.set_geometry("gGeom")
                    gdf_chunk.set_crs(epsg=4326, inplace=True, allow_override=True)

                    # Inserción. Usamos dtype para forzar a SQLAlchemy a no preguntar a la DB
                    from geoalchemy2 import Geometry
                    gdf_chunk.to_postgis(
                        name=TABLA_PANDAS, 
                        con=engine, 
                        if_exists='append', 
                        index=False,
                        dtype={'gGeom': Geometry(geometry_type='MULTIPOLYGON', srid=4326)}
                    )
                    
                    total_processed += len(chunk)
                    print(f"📦 Procesados: {total_processed} registros...")
                    chunk = []

            if chunk:
                gdf_chunk = gpd.GeoDataFrame.from_features(chunk, crs=source.crs)
                cols = [c for c in mapping.keys() if c in gdf_chunk.columns or c == 'geometry']
                gdf_chunk = gdf_chunk[cols].rename(columns=mapping).set_geometry("gGeom")
                gdf_chunk.set_crs(epsg=4326, inplace=True, allow_override=True)
                gdf_chunk.to_postgis(
                    TABLA_PANDAS, engine, if_exists='append', index=False,
                    dtype={'gGeom': Geometry(geometry_type='MULTIPOLYGON', srid=4326)}
                )
                total_processed += len(chunk)

        print(f"\n✨ Proceso terminado: {total_processed} filas en {TABLA_SQL}.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("\n" + "="*40)
        input("Presiona ENTER para cerrar...")

if __name__ == "__main__":
    run_safe_migration()

import fiona

gdb_path = "/home/arelyxl/Downloads/Repos/Geo/gadm_410-gdb/gadm_410.gdb/"
layers = fiona.listlayers(gdb_path)

for layer_name in layers:
    print(f"\n--- Capa: {layer_name} ---")
    with fiona.open(gdb_path, layer=layer_name) as layer:
        for field_name, field_type in layer.schema['properties'].items():
            print(f"Campo: {field_name} | Tipo: {field_type}")

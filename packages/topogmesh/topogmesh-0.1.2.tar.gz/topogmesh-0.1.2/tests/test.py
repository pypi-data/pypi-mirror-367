import topogmesh

everest_mesh = topogmesh.mesh_from_shape_file(
    shp_path='everest.geojson',
    tif_paths=['N27E086.tif', 'N28E086.tif', 'N29E086.tif'],
    base_height=5,
    scale=0.1
)

topogmesh.export_mesh_to_3mf(everest_mesh, 'everest.3mf')
var berlin_bbox = ee.Geometry.Rectangle([13.088, 52.338, 13.761, 52.676]);

// Get least cloudy summer image — use mosaic to combine multiple paths
var l8_collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterBounds(berlin_bbox)
  .filterDate('2019-06-01', '2022-09-30')
  .filter(ee.Filter.lt('CLOUD_COVER', 20))
  .filter(ee.Filter.calendarRange(6, 8, 'month'))
  .sort('CLOUD_COVER');

print('Number of scenes:', l8_collection.size());

// Mosaic all valid scenes — takes best pixel where scenes overlap
var l8_mosaic = l8_collection.mosaic();

// LST in Celsius
var lst_celsius = l8_mosaic.select('ST_B10')
  .multiply(0.00341802).add(149.0).subtract(273.15);

// NDVI
var optical = l8_mosaic.select(['SR_B4','SR_B5'])
  .multiply(0.0000275).add(-0.2);
var ndvi = optical.normalizedDifference(['SR_B5','SR_B4']).rename('NDVI');

// Visualise — check this covers all of Berlin before exporting
var lstViz = {min: 20, max: 45, palette: ['blue','cyan','yellow','orange','red']};
Map.centerObject(berlin_bbox, 10);
Map.addLayer(lst_celsius.clip(berlin_bbox), lstViz, 'LST Celsius');
Map.addLayer(ndvi.clip(berlin_bbox), 
  {min: -0.1, max: 0.6, palette: ['brown','white','green']}, 'NDVI');

// Export LST
Export.image.toDrive({
  image: lst_celsius.clip(berlin_bbox),
  description: 'LST_Berlin_mosaic',
  folder: 'GEE_Exports',
  fileNamePrefix: 'lst_berlin',
  region: berlin_bbox,
  scale: 30,
  crs: 'EPSG:25833',
  maxPixels: 1e9
});

// Export NDVI
Export.image.toDrive({
  image: ndvi.clip(berlin_bbox),
  description: 'NDVI_Berlin_mosaic',
  folder: 'GEE_Exports',
  fileNamePrefix: 'ndvi_berlin',
  region: berlin_bbox,
  scale: 30,
  crs: 'EPSG:25833',
  maxPixels: 1e9
});
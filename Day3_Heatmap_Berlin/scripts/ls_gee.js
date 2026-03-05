// Select Landsat 8 Level-2 for Berlin in summer
var berlin = ee.FeatureCollection('FAO/GAUL/2015/level1')
                .filter(ee.Filter.eq('ADM1_NAME', 'Berlin'));


var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterBounds(berlin)
  .filterDate('2021-07-01', '2021-08-31')
  .filter(ee.Filter.lt('CLOUD_COVER', 5))
  .sort('CLOUD_COVER')
  .first();


print('Scene ID:', l8.get('SYSTEM:ID'));
print('Cloud cover:', l8.get('CLOUD_COVER'));

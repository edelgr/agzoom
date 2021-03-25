from django.urls import path, include
from data_annotator import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('anotador/', views.anotador, name='anotador'),
                  path('anotador/', views.add_category, name='add_category'),

                  path('', views.index, name='index'),
                  path('active_project/', views.active_project, name='active_project'),

                  path('annotation/', views.annotation, name='annotation'),
                  path('data_explorer_img/', views.data_explorer_img, name='data_explorer_img'),
                  path('data_explorer_shp/', views.data_explorer_shp, name='data_explorer_shp'),

                  path('prog_corte/', views.prog_corte, name='prog_corte'),
                  path('prepare_prog_corte/', views.prepare_prog_corte, name='prepare_prog_corte'),

                  path('init_sampling/', views.init_sampling, name='init_sampling'),
                  path('save_feature_json/', views.save_feature_json, name='save_feature_json'),
                  path('load_feature_json/<project_id>/<name_pk>/<date_sentinel>/', views.load_feature_json,
                       name='load_feature_json'),

                  path('delete_point_in_polygon/', views.delete_point_in_polygon, name='delete_point_in_polygon'),
                  path('add_point_in_polygon/', views.add_point_in_polygon, name='add_point_in_polygon'),

                  path('delete_point_in_line/', views.delete_point_in_line, name='delete_point_in_line'),
                  path('add_point_in_line/', views.add_point_in_line, name='add_point_in_line'),

                  path('get_dates/', views.get_dates, name='get_dates'),
                  path('get_repo_images/', views.get_repo_images, name='get_repo_images'),

                  path('get_album_image/<int:project_id>/<image_name>', views.get_album_image, name='get_album_image'),

                  path('get_all_image/', views.get_all_image, name='get_all_image'),
                  path('get_shape_pk/', views.get_shape_pk, name='get_shape_pk'),

                  path('get_date_image/', views.get_date_image, name='get_date_image'),

                  path('explorer', views.explorer, name='explorer'),

                  path('templates_image/', views.templates_image, name='templates_image'),

                  path('cut_image/', views.cut_image, name='cut_image'),

                  path(
                      'sentinel_background_image_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z'
                      '>/<slug:x>/<slug:y>/',
                      views.sentinel_background_image_mbtiles, name='sentinel_background_image_mbtiles'),

                  path(
                      'drones_background_image_mbtiles/<int:project_id>/<slug:date_drones>/<slug:name>/<slug:z'
                      '>/<slug:x>/<slug:y>/',
                      views.drones_background_image_mbtiles, name='drones_background_image_mbtiles'),

                  path(
                      'sentinel_sentinel_color_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_color_mbtiles, name='sentinel_color_mbtiles'),

                  path(
                      'sentinel_classification_tiles/<int:project_id>/<slug:date_sentinel>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_classification_tiles, name='sentinel_classification_tiles'),

                  path(
                      'sentinel_ripe_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_ripe_mbtiles, name='sentinel_ripe_mbtiles'),

                  path(
                      'sentinel_ndvi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_ndvi_mbtiles, name='sentinel_ndvi_mbtiles'),
                  path(
                      'sentinel_gndvi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_gndvi_mbtiles, name='sentinel_gndvi_mbtiles'),
                  path(
                      'sentinel_ndmi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_ndmi_mbtiles, name='sentinel_ndmi_mbtiles'),
                  path(
                      'sentinel_gci_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_gci_mbtiles, name='sentinel_gci_mbtiles'),
                  path(
                      'sentinel_msi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_msi_mbtiles, name='sentinel_msi_mbtiles'),
                  path(
                      'sentinel_sipi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_sipi_mbtiles, name='sentinel_sipi_mbtiles'),
                  path(
                      'sentinel_ndwi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_ndwi_mbtiles, name='sentinel_ndwi_mbtiles'),
                  path(
                      'sentinel_yvimss_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_yvimss_mbtiles, name='sentinel_yvimss_mbtiles'),
                  path(
                      'sentinel_evi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_evi_mbtiles, name='sentinel_evi_mbtiles'),
                  path(
                      'sentinel_lai_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_lai_mbtiles, name='sentinel_lai_mbtiles'),
                  path(
                      'sentinel_savi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_savi_mbtiles, name='sentinel_savi_mbtiles'),
                  path(
                      'sentinel_gli_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_gli_mbtiles, name='sentinel_gli_mbtiles'),
                  path(
                      'sentinel_tci_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_tci_mbtiles, name='sentinel_tci_mbtiles'),
                  path(
                      'sentinel_bsi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_bsi_mbtiles, name='sentinel_bsi_mbtiles'),
                  path(
                      'sentinel_nbri_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_nbri_mbtiles, name='sentinel_nbri_mbtiles'),
                  path(
                      'sentinel_endvi_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_endvi_mbtiles, name='sentinel_endvi_mbtiles'),
                  path(
                      'sentinel_classification_mbtiles/<int:project_id>/<slug:date_sentinel>/<slug:name>/<slug:z>/<slug:x>/<slug:y>/',
                      views.sentinel_classification_mbtiles, name='sentinel_classification_mbtiles'),

                  path('delete_sites', views.delete_sites, name='delete_sites'),

                  path('add_image', views.add_image, name='add_image'),
                  path('salvar_imagen', views.salvar_imagen, name='salvar_imagen'),

                  path('add_shape_file', views.add_shape_file, name='add_shape_file'),
                  path('salvar_shape_file', views.salvar_shape_file, name='salvar_shape_file'),

                  path('background_image', views.background_image, name='background_image'),
                  path('prepare_background', views.prepare_background, name='prepare_background'),

                  path('cloud_mask', views.cloud_mask, name='cloud_mask'),
                  path('prepare_cloud_mask', views.prepare_cloud_mask, name='prepare_cloud_mask'),

                  path('spectral_features', views.spectral_features, name='spectral_features'),
                  path('prepare_spectral_features', views.prepare_spectral_features, name='prepare_spectral_features'),

                  path('create_mbtiles', views.create_mbtiles, name='create_mbtiles'),
                  path('prepare_tiles', views.prepare_tiles, name='prepare_tiles'),

                  path('iv', views.iv, name='iv'),
                  path('prepare_iv', views.prepare_iv, name='prepare_iv'),

                  path('prepare_tiles', views.prepare_tiles, name='prepare_tiles'),

                  path('cloud_mask', views.cloud_mask, name='cloud_mask'),

                  path('ripe_image', views.ripe_image, name='ripe_image'),
                  path('prepare_ripe', views.prepare_ripe, name='prepare_ripe'),

                  path('shp2geojson', views.shp2geojson, name='shp2geojson'),
                  path('convert_shp2geojson', views.convert_shp2geojson, name='convert_shp2geojson'),

                  path('render_vector_json/<int:project_id>/<slug:shape>', views.render_vector_json,
                       name='render_vector_json'),

                  path('extract_sites', views.extract_sites, name='extract_sites'),
                  path('prepare_extract_sites', views.prepare_extract_sites, name='prepare_extract_sites'),

                  path('train_validation_test', views.train_validation_test, name='train_validation_test'),

                  path('unify_samples', views.unify_samples, name='unify_samples'),

                  path('accounts/', include('django.contrib.auth.urls')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

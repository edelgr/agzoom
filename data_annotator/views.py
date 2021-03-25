import base64
import string
from datetime import datetime, date
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.core.serializers import serialize
from django.contrib.gis.geos import Point, Polygon, LineString
from .models import Samplesproject, Image, Label, Site, Macroproject, Shape, Corte
from anotador import settings
import random
from .forms import NewImageModelForm, NewShapeFileModelForm
from data_annotator import geoFunctions
from data_annotator import createTiles, spectralFeatures, texturalFeatures, cloud_sentinel_detector
from data_annotator import cutSentinelSite, cutDronesSite, cut_sentinel
from data_annotator import maduracion, create_iv
from data_annotator import createMacroProyectDataset, createMacroProyectUnitedDataset
from os import listdir
import os
from os.path import isfile, isdir
from osgeo import ogr, osr
from django.utils.dateparse import parse_date
import json
import ogr
from django.contrib.auth.decorators import login_required, permission_required

project_data_path = settings.MEDIA_ROOT


@login_required
def anotador(request):
    status = 'ok'
    project_list = Samplesproject.objects.all()
    longitude = -79.96
    latitude = 22.39

    context = {"project_list": project_list,
               'longitude': longitude,
               'latitude': latitude,
               "status": status}

    return render(request, 'data_annotator/anotador.html', context=context)


@login_required
def add_category(request):
    status = 'ok'
    project_list = Samplesproject.objects.all()
    longitude = -79.96
    latitude = 22.39

    context = {"project_list": project_list,
               'longitude': longitude,
               'latitude': latitude,
               "status": status}

    return render(request, 'data_annotator/anotador.html', context=context)


@login_required
def sentinel_ndvi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/ndvi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_lai_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/lai_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_evi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/evi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_yvimss_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/yvimss_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_ndwi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/ndwi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_sipi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/sipi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_gci_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/gci_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_gndvi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/gndvi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_ndmi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/ndmi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_msi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/msi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_savi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/savi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_gli_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/gli_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_tci_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/tci_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_bsi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/bsi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_nbri_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/nbri_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()



@login_required
def sentinel_classification_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/classification_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()


@login_required
def sentinel_endvi_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/endvi_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()

@login_required
def sentinel_color_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/sentinel_color_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()


@login_required
def sentinel_background_image_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/background_image_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()


@login_required
def drones_background_image_mbtiles(request, project_id, date_drones, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/drones/' + date_drones + "/" + name + "/background_image_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()


@login_required
def sentinel_ripe_mbtiles(request, project_id, date_sentinel, name, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/" + name + "/ripe_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()


@login_required
def sentinel_classification_tiles(request, project_id, date_sentinel, z, x, y):
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    image_path = project_data_path + 'images/' + project_name
    path = image_path + '/sentinel/' + date_sentinel + "/classification_parcels_total_mbtiles" + "/" + z + "/" + x + "/" + y + ".png"
    try:
        image = open(path, 'rb')
        return FileResponse(image)
    except:
        pass
    return HttpResponse()


@login_required
def explorer(request):
    print("explorer")
    project_id = request.POST['pid']
    label_name = request.POST['label_name']

    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    print(project_name)

    # qs = Image.objects.get(pk=pk)
    # date_image = qs.date_captured
    # y = date_image.year
    # if date_image.month < 10:
    #     m = '0' + str(date_image.month)
    # else:
    #     m = str(date_image.month)
    #
    # if date_image.day < 10:
    #     d = '0' + str(date_image.day)
    # else:
    #     d = str(date_image.day)
    #
    # ff = str(y) + str(m) + str(d)
    ff = '20200720'
    cutDronesSite.cla_drones_site(project_name, ff, label_name, 'natural_color.tif')
    return


@login_required
def templates_image(request):
    print("templete_image")
    project_id = request.POST['pid']
    label_name = request.POST['label_name']

    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name

    templates_path = project_data_path + 'album_patrones_drones/' + project_name
    templates_path = templates_path + '/Clases/' + label_name + '/'

    templates_image_list = []
    for img_path in os.listdir(templates_path):
        image = open(os.path.join(templates_path, img_path), 'rb').read()
        ib64 = base64.b64encode(image)
        templates_image_list.append(ib64.decode('utf-8'))

    json_dict = {
        'status': "Ok",
        'templates_image_list': templates_image_list,
    }

    return JsonResponse(json_dict)


@login_required
def get_album_image(request, project_id, image_name):
    print("get_album_image")

    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    repositorio_path = project_data_path + '/album_patrones_drones/' + project_name
    repositorio_path = repositorio_path + '/Repositorio Imagenes'

    try:
        img = open(os.path.join(repositorio_path, image_name), 'rb')
        # ib64 = base64.b64encode(img)
        # img = ib64.decode('utf-8')
        return FileResponse(img)
    except:
        pass
    return HttpResponse()


@login_required
def init_sampling(request):
    print("init_sampling")
    project_id = request.POST['proj_pk']
    status = 'ok'
    legend_list = []
    legend_pk_list = []
    legend_color_list = []

    project = Samplesproject.objects.get(pk=project_id)
    macro_project_id = project.macro_project_id

    legend = Label.objects.filter(macro_project=macro_project_id)
    for lab in legend:
        legend_list.append(lab.label_name)
        legend_pk_list.append(lab.pk)
        legend_color_list.append(lab.color)

    longitude = project.Longitud_site
    latitude = project.Latitud_site

    context = {
        'legend_list': legend_list,
        'legend_pk_list': legend_pk_list,
        'legend_color_list': legend_color_list,
        'longitude': longitude,
        'latitude': latitude,
        "status": status
    }
    return JsonResponse(context)


@login_required
def index(request):
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    # sp = Samplesproject.objects.first()
    # u = sp.users.all()

    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/index.html', context=context)


@login_required
def active_project(request):
    print("active_project")
    active_proj = request.POST['proj_pk']
    profile = request.user.profile
    profile.active_proj = active_proj
    profile.save()

    status = 'ok'
    context = {"status": status}
    return JsonResponse(context)


@login_required
def prog_corte(request):
    print("prog_corte")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()


    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/prog_corte.html', context=context)


@login_required
def prepare_prog_corte(request):
    print("prepare_prog_corte")
    status = 'ok'
    project_id = request.POST['proj_pk']
    rows_json = request.POST.get('rows_list')
    row_list = json.loads(rows_json)

    for row in row_list:
        try:
            f = row['fecha']
            fecha = datetime.strptime(f, "%Y-%m-%d")
            bloque = row['bloque']
            campo = row['campo']
            campo_list = Corte.objects.filter(sample_project_id=project_id,
                                              fecha=fecha,
                                              bloque=bloque,
                                              campo=campo)

            if campo_list.count() > 0:
                # si el campo ya estaba en la base de datos, entonces no se agrega
                continue
            else:
                corte = Corte()
                corte.sample_project = Samplesproject.objects.get(pk=project_id)
                corte.cpa = row['cpa']
                corte.fecha = row['fecha']
                corte.bloque = row['bloque']
                corte.campo = row['campo']
                corte.variedad = row['variedad']
                corte.cepa = row['cepa']
                corte.edad = row['edad']
                corte.pol_cana = row['pol_cana']
                corte.pol_jugo = row['pol_jugo']
                corte.pureza = row['pureza']
                corte.index = row['index']
                corte.brix = row['brix']
                corte.brix_inf = row['brix_inf']
                corte.brix_sup = row['brix_sup']
                corte.im = row['im']
                corte.fibra = row['fibra']
                corte.rendimiento = row['rendimiento']
                corte.ha = row['ha']
                corte.t_ha = row['t_ha']
                corte.t = row['t']
                corte.save()
        except:
            pass

    print("prepare_prog_corte")
    return JsonResponse({'status': status})


@login_required
def data_explorer_img(request):
    print("data_explorer_img")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/data_explorer_img.html', context=context)


@login_required
def add_image(request):
    print("data_explorer_img")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "form": NewImageModelForm(),
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/add_image.html', context=context)


from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect


@login_required
def salvar_imagen(request):
    print("salvar_imagen")
    if request.method == 'POST':
        form = NewImageModelForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image_file']
            platform = request.POST['platform']
            date_captured = request.POST['date_captured']
            date_obj = parse_date(date_captured)

            project_id = request.POST['sample_project']
            name = request.POST['name']
            project = Samplesproject.objects.get(pk=project_id)

            insert = Image(image_file=image_file, platform=platform, name=name, date_captured=date_obj,
                           sample_project=project)
            insert.save()

            return HttpResponseRedirect(reverse('data_explorer_img'))
        else:
            messages.error(request, "Error al procesar el formulario")
    else:
        return HttpResponseRedirect(reverse('data_explorer_img'))


@login_required
def data_explorer_shp(request):
    print("data_explorer_shp")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/data_explorer_shp.html', context=context)


@login_required
def add_shape_file(request):
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "form": NewShapeFileModelForm(),
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/add_shp.html', context=context)


@login_required
def salvar_shape_file(request):
    print("salvar_shape_file")
    if request.method == 'POST':
        form = NewShapeFileModelForm(request.POST, request.FILES)
        if form.is_valid():
            shape_file = request.FILES['shape_file']
            description = request.POST['description']

            date_captured = request.POST['date_captured']
            date_obj = parse_date(date_captured)

            project_id = request.POST['sample_project']
            project = Samplesproject.objects.get(pk=project_id)
            insert = Shape(shape_file=shape_file, description=description, date_captured=date_obj,
                           sample_project=project)
            insert.save()

            return HttpResponseRedirect(reverse('data_explorer_shp'))
        else:
            messages.error(request, "Error al procesar el formulario")
    else:
        return HttpResponseRedirect(reverse('data_explorer_shp'))


@login_required
def cloud_mask(request):
    print("cloud_mask")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/cloud_mask.html', context=context)


@login_required
def prepare_cloud_mask(request):
    print("prepare_cloud_mask  - inicio")
    project_id = request.POST['proj_pk']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    checked_image_id_list = request.POST.getlist('checked_image_id_list[]')

    for pk in checked_image_id_list:
        qs = Image.objects.get(pk=pk)
        date_image = qs.date_captured
        y = date_image.year
        if date_image.month < 10:
            m = '0' + str(date_image.month)
        else:
            m = str(date_image.month)

        if date_image.day < 10:
            d = '0' + str(date_image.day)
        else:
            d = str(date_image.day)

        ff = str(y) + str(m) + str(d)
        if qs.platform == '1':
            plat = 'sentinel'
        else:
            continue

        path = project_data_path + 'images/' + project_name
        dir_images = path + '/' + plat + '/' + ff + "/"
        cloud_sentinel_detector.create_cloud_mask(dir_images)

    json_dict = {
        'status': "ok",
    }

    print("prepare_cloud_mask - fin")
    return JsonResponse(json_dict)


@login_required
def spectral_features(request):
    print("spectral_features")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/spectral_features.html', context=context)


@login_required
def prepare_spectral_features(request):
    print("prepare_spectral_features - inicio")
    project_id = request.POST['proj_pk']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    checked_image_id_list = request.POST.getlist('checked_image_id_list[]')

    for pk in checked_image_id_list:
        qs = Image.objects.get(pk=pk)
        date_image = qs.date_captured
        y = date_image.year
        if date_image.month < 10:
            m = '0' + str(date_image.month)
        else:
            m = str(date_image.month)

        if date_image.day < 10:
            d = '0' + str(date_image.day)
        else:
            d = str(date_image.day)

        ff = str(y) + str(m) + str(d)

        nombre = qs.name

        if qs.platform == '1':
            plat = 'sentinel'
            path = project_data_path + 'images/' + project_name
            dir_images = path + '/' + plat + '/' + ff + "/" + nombre + "/"
            spectralFeatures.create_spectralfeatures(dir_images)
        else:
            plat = 'drones'
            path = project_data_path + 'images/' + project_name
            dir_images = path + '/' + plat + '/' + ff + "/" + nombre + "/"
            processing_image_path = dir_images + 'natural_color.tif'
            output_file = dir_images + 'texture_features.tif'
            texturalFeatures.CreateRasterTextureFeatures(processing_image_path, output_file)

    json_dict = {
        'status': "ok",
    }

    print("prepare_spectral_features - fin")
    return JsonResponse(json_dict)


@login_required
def background_image(request):
    print("background_image")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/background_image.html', context=context)


@login_required
def prepare_background(request):
    print("prepare_background - inicio")
    messages.info(request, "prepare_background - inicio")
    project_id = request.POST['proj_pk']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name

    checked_image_id_list = request.POST.getlist('checked_image_id_list[]')
    for pk in checked_image_id_list:
        qs = Image.objects.get(pk=pk)
        date_image = qs.date_captured
        y = date_image.year
        if date_image.month < 10:
            m = '0' + str(date_image.month)
        else:
            m = str(date_image.month)

        if date_image.day < 10:
            d = '0' + str(date_image.day)
        else:
            d = str(date_image.day)

        ff = str(y) + str(m) + str(d)

        nombre = qs.name
        if qs.platform == '1':
            plat = 'sentinel'
        else:
            plat = 'drones'

        path = project_data_path + 'images/' + project_name
        dir_images = path + '/' + plat + '/' + ff + "/" + nombre + "/"
        dirs = listdir(dir_images)
        if plat == 'sentinel':
            path_image = None
            for directory in dirs:
                t = directory[-4:]
                if t == 'SAFE':
                    path_image = directory
                    break
            if path_image is not None:
                path_image = path_image + '/GRANULE/'
                full_path = dir_images + path_image
                path_image = path_image + listdir(full_path)[0] + '/IMG_DATA'
                geoFunctions.sentinel_background_image(dir_images, path_image)
        else:
            path_image = None
            for directory in dirs:
                t = directory[-4:]
                if t == 'ORTO':
                    path_image = directory
                    break
            input_file = None
            tfw_jgw = None
            full_path = dir_images + path_image
            dirs_orto = listdir(full_path)
            for directory in dirs_orto:
                t = directory[-4:]
                if t == '.tif':
                    input_file = directory
                if t == '.j2w':
                    tfw_jgw = directory
                if t == '.tfw':
                    tfw_jgw = directory
                if t == '.jpg':
                    input_file = directory
                if t == '.jp2':
                    input_file = directory
                if t == '.jgw':
                    tfw_jgw = directory

            input_file = full_path + '/' + input_file
            if tfw_jgw is not None:
                tfw_jgw = full_path + '/' + tfw_jgw
            output_file = dir_images + "background_image.tif"
            geoFunctions.drones_background_image(input_file, tfw_jgw, output_file)

    json_dict = {
        'status': "ok",
    }

    print("prepare_background - fin")
    return JsonResponse(json_dict)


@login_required
def create_mbtiles(request):
    print("create_mbtiles")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/create_mbtiles.html', context=context)


@login_required
def prepare_tiles(request):
    print("prepare_tiles  - inicio")
    project_id = request.POST['proj_pk']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    checked_image_list = request.POST.getlist('checked_image_list[]')
    checked_imageid_list = request.POST.getlist('checked_imageid_list[]')
    for img, pk in zip(checked_image_list, checked_imageid_list):
        qs = Image.objects.get(pk=pk)
        date_image = qs.date_captured
        y = date_image.year
        if date_image.month < 10:
            m = '0' + str(date_image.month)
        else:
            m = str(date_image.month)

        if date_image.day < 10:
            d = '0' + str(date_image.day)
        else:
            d = str(date_image.day)

        ff = str(y) + str(m) + str(d)
        if qs.platform == '1':
            plat = 'sentinel'
        else:
            plat = 'drones'

        nombre = qs.name

        path = project_data_path + 'images/' + project_name + '/' + plat + '/' + ff + "/" + nombre + "/"

        from shutil import rmtree
        input_file = path + img
        output_dir = path + img[0:-4] + '_mbtiles/'
        if os.path.isdir(output_dir):
            rmtree(output_dir)
        createTiles.tiler(plat, input_file, output_dir)

    json_dict = {
        'status': "ok",
    }
    print("prepare_tiles  - fin")
    return JsonResponse(json_dict)


@login_required
def iv(request):
    print("iv")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/iv.html', context=context)


@login_required
def prepare_iv(request):
    print("prepare_iv  - inicio")
    project_id = request.POST['proj_pk']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    checked_image_list = request.POST.getlist('checked_image_list[]')
    checked_imageid_list = request.POST.getlist('checked_imageid_list[]')
    checked_iv_list = request.POST.getlist('checked_iv_list[]')

    status = "OK"
    path = ""
    for pk, name in zip(checked_imageid_list, checked_image_list):
        qs = Image.objects.get(pk=pk)
        date_image = qs.date_captured
        y = date_image.year
        if date_image.month < 10:
            m = '0' + str(date_image.month)
        else:
            m = str(date_image.month)

        if date_image.day < 10:
            d = '0' + str(date_image.day)
        else:
            d = str(date_image.day)

        ff = str(y) + str(m) + str(d)
        if qs.platform == '1':
            plat = 'sentinel'
        else:
            plat = 'drones'

        path = project_data_path + 'images/' + project_name + '/' + plat + '/' + ff + "/" + name + "/"
        status = create_iv.create_iv(path, checked_iv_list)
        if status == "Error":
            break

    json_dict = {
        'status': status,
        'image': path,
    }
    print("prepare_iv  - fin")
    return JsonResponse(json_dict)


@login_required
@permission_required('add_samples', raise_exception=True)
@permission_required('delete_samples', raise_exception=True)
def annotation(request):
    status = 'ok'
    project_list = Samplesproject.objects.all()
    longitude = -79.96
    latitude = 22.39
    context = {"project_list": project_list,
               'longitude': longitude,
               'latitude': latitude,
               "status": status
               }
    return render(request, 'data_annotator/anotacion.html', context=context)


@login_required
def data_explorer_shp(request):
    status = 'ok'
    project_list = Samplesproject.objects.all()
    longitude = -79.96
    latitude = 22.39

    context = {"project_list": project_list,
               'longitude': longitude,
               'latitude': latitude,
               "status": status
               }
    return render(request, 'data_annotator/data_explorer_shp.html', context=context)


@login_required
def download_muestras(request, project_id, name_pk, date_sentinel):
    print("download_muestras")

    date_captured = datetime.strptime(date_sentinel, "%Y%m%d")
    qs = Site.objects.filter(sample_project_id=project_id,
                             label_id=name_pk,
                             date_satellite=date_captured)

    geojson = serialize('geojson', qs, geometry_field='point')
    file = Label.objects.get(pk=name_pk).label_name + '.json'

    response = HttpResponse(geojson, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="' + file + '"'

    return response


@login_required
def delete_sites(request):
    print("delete_sites")

    project_id = request.POST['pid']
    name_pk = request.POST['name_pk']
    date_sentinel = request.POST['date_sentinel']

    date_captured = datetime.strptime(date_sentinel, "%Y%m%d")
    point_list = Site.objects.filter(sample_project_id=project_id,
                                     label_id=name_pk,
                                     date_satellite=date_captured)
    point_list.delete()

    # for point_name in point_list:
    #     qs = Site.objects.filter(site_name=point_name)
    #     qs[0].delete()

    json_dict = {
        'status': "Ok",
    }

    return JsonResponse(json_dict)


# solicita las fechas de las imagenes y los shpe y devuelve listas
# que se usan para llenar los select
@login_required
def get_dates(request):
    print("get_dates")
    project_id = request.POST['proj_pk']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name

    qsdrones = Image.objects.filter(sample_project_id=project_id, platform='2')
    qssentinel = Image.objects.filter(sample_project_id=project_id, platform='1')
    qsshape = Shape.objects.filter(sample_project_id=project_id)
    date_drones_list = []
    if qsdrones.exists():
        for f in qsdrones:
            y = f.date_captured.year
            if f.date_captured.month < 10:
                m = '0' + str(f.date_captured.month)
            else:
                m = str(f.date_captured.month)

            if f.date_captured.day < 10:
                d = '0' + str(f.date_captured.day)
            else:
                d = str(f.date_captured.day)

            ff = str(y) + str(m) + str(d)
            if ff not in date_drones_list:
                date_drones_list.append(ff)

    date_sentinel_list = []
    if qssentinel.exists():
        for f in qssentinel:
            y = f.date_captured.year
            if f.date_captured.month < 10:
                m = '0' + str(f.date_captured.month)
            else:
                m = str(f.date_captured.month)

            if f.date_captured.day < 10:
                d = '0' + str(f.date_captured.day)
            else:
                d = str(f.date_captured.day)
            ff = str(y) + str(m) + str(d)
            if ff not in date_sentinel_list:
                date_sentinel_list.append(ff)

    date_shape_list = []
    if qsshape.exists():
        for f in qsshape:
            y = f.date_captured.year
            if f.date_captured.month < 10:
                m = '0' + str(f.date_captured.month)
            else:
                m = str(f.date_captured.month)

            if f.date_captured.day < 10:
                d = '0' + str(f.date_captured.day)
            else:
                d = str(f.date_captured.day)
            ff = str(y) + str(m) + str(d)
            if ff not in date_shape_list:
                date_shape_list.append(ff)

    json_dict = {
        'status': "Ok",
        'proj_name': project_name,
        'date_drones_list': date_drones_list,
        'date_sentinel_list': date_sentinel_list,
        'date_shape_list': date_shape_list
    }

    return JsonResponse(json_dict)


@login_required
def get_repo_images(request):
    print("get_repo_images")
    project_id = request.POST['proj_pk']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name

    repositorio_path = project_data_path + 'album_patrones_drones/' + project_name
    repositorio_path = repositorio_path + '/Repositorio Imagenes/'

    repositorio_list = []
    try:
        for a in os.listdir(repositorio_path):
            repositorio_list.append(a)
    except:
        pass

    json_dict = {
        'status': "Ok",
        'proj_name': project_name,
        'repositorio_list': repositorio_list,
    }

    return JsonResponse(json_dict)


@login_required
def get_all_image(request):
    print("get_all_image")
    project_id = request.POST['proj_pk']
    # op = request.POST['op']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name

    qs = Image.objects.filter(sample_project_id=project_id).order_by('date_captured')
    date_list = []
    name_list = []
    plat_list = []
    pk_list = []
    img_tif_list = []

    if qs.exists():
        for f in qs:
            pk_list.append(f.id)
            plat_list.append(f.platform)
            y = f.date_captured.year
            if f.date_captured.month < 10:
                m = '0' + str(f.date_captured.month)
            else:
                m = str(f.date_captured.month)

            if f.date_captured.day < 10:
                d = '0' + str(f.date_captured.day)
            else:
                d = str(f.date_captured.day)

            ff = str(y) + str(m) + str(d)
            date_list.append(ff)

            name_list.append(f.name)

            if f.platform == '1':
                plat = 'sentinel'
            else:
                plat = 'drones'

            nombre = f.name
            path = project_data_path + 'images/' + project_name
            dir_images = path + '/' + plat + '/' + ff + "/" + nombre + "/"
            files1 = [f for f in listdir(dir_images) if isfile(dir_images + '/' + f)]
            tif_list = []
            for name in files1:
                if name[-3:] == 'tif':
                    if name != 'spectral_features.tif' and name != 'sentinel.tif' and name != 'iv.tif':
                        tif_list.append(name)
            img_tif_list.append(tif_list)

    json_dict = {
        'status': "Ok",
        'pk_list': pk_list,
        'plat_list': plat_list,
        'date_list': date_list,
        'name_list': name_list,
        'img_tif_list': img_tif_list,
    }

    return JsonResponse(json_dict)


@login_required
def get_shape_pk(request):
    print("get_shape_pk")
    project_id = request.POST['proj_pk']
    qs = Shape.objects.filter(sample_project_id=project_id)
    date_list = []
    desc_list = []
    pk_list = []
    if qs.exists():
        for f in qs:
            pk_list.append(f.id)
            desc_list.append(f.description)
            y = f.date_captured.year
            if f.date_captured.month < 10:
                m = '0' + str(f.date_captured.month)
            else:
                m = str(f.date_captured.month)

            if f.date_captured.day < 10:
                d = '0' + str(f.date_captured.day)
            else:
                d = str(f.date_captured.day)

            ff = str(y) + str(m) + str(d)
            if ff not in date_list:
                date_list.append(ff)

    json_dict = {
        'status': "Ok",
        'pk_list': pk_list,
        'desc_list': desc_list,
        'date_list': date_list,
    }

    return JsonResponse(json_dict)


@login_required
def get_date_image(request):
    print("get_date_image  init")
    project_id = request.POST['proj_pk']
    date = request.POST['date']
    date_captured = datetime.strptime(date, "%Y%m%d")
    platform = request.POST['platform']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name

    qs = Image.objects.filter(sample_project_id=project_id, platform=platform, date_captured=date_captured)
    name_list = []
    mbtiles_list = []

    if platform == '1':
        plat = 'sentinel'
    else:
        plat = 'drones'

    if qs.exists():
        for f in qs:
            path = project_data_path + 'images/' + project_name
            dir_images = path + '/' + plat + '/' + date + "/" + f.name + "/"

            files2 = [f for f in listdir(dir_images) if isdir(dir_images + '/' + f)]
            for name in files2:
                if name[-7:] == 'mbtiles':
                    mbtiles_list.append(name)
                    name_list.append(f.name)

    json_dict = {
        'status': "Ok",
        'name_list': name_list,
        'mbtiles_list': mbtiles_list
    }
    print("get_date_image  Fin")
    return JsonResponse(json_dict)


@login_required
def cut_image(request):
    print("cut_image")
    project_id = request.POST['pid']
    feature_list = request.POST['features']
    date_sentinel = request.POST['date_sentinel']
    name = request.POST['name']

    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    path = project_data_path + 'images/' + project_name
    dir_images = path + '/' + 'sentinel' + '/' + date_sentinel + "/" + name + "/"
    dirs = listdir(dir_images)

    features = json.loads(feature_list)
    for feat in features:
        envelopes = feat['geometryChangeKey_']['target']['flatCoordinates']

        path_image = None
        for directory in dirs:
            t = directory[-4:]
            if t == 'SAFE':
                path_image = directory
                break
        if path_image is not None:
            path_image = path_image + '/GRANULE/'
            full_path = dir_images + path_image
            path_image = path_image + listdir(full_path)[0] + '/IMG_DATA'
            cut_sentinel.spectral_features(dir_images, path_image, envelopes)

    print("saliendo cut_image")
    status = 'OK'
    return JsonResponse({'status': status})


@login_required
def delete_point_in_polygon(request):
    print("delete_point_in_polygon")
    status = 'ok'
    project_id = request.POST['pid']
    name_pk = request.POST['name_pk']
    feature_list = request.POST['features']
    date_sentinel = request.POST['date_sentinel']
    date_captured = datetime.strptime(date_sentinel, "%Y%m%d")
    features = json.loads(feature_list)

    point_list = Site.objects.filter(sample_project_id=project_id,
                                     label_id=name_pk,
                                     date_satellite=date_captured)
    for feat in features:
        c = feat['geometryChangeKey_']['target']['flatCoordinates']
        lista = []
        x = 0
        y = 0
        for i, c in enumerate(c):
            if (i % 2) == 0:
                x = c
            else:
                y = c
                lista.append((x, y))

        poly = Polygon(lista)
        counter = 0
        for e in point_list:
            if poly.contains(e.point):
                try:
                    qs = Site.objects.get(sample_project_id=project_id,
                                          point=e.point,
                                          site_name=e,
                                          date_satellite=date_captured)
                    qs.delete()
                    counter += 1
                except:
                    pass
    print("salinedo delete_point_in_polygon")
    return JsonResponse({'status': status, 'np': counter})


@login_required
def add_point_in_polygon(request):
    print("add_point_in_polygon")
    status = 'ok'
    project_id = request.POST['pid']
    name_pk = request.POST['name_pk']
    feature_list = request.POST['features']
    date_sentinel = request.POST['date_sentinel']
    date_captured = datetime.strptime(date_sentinel, "%Y%m%d")
    features = json.loads(feature_list)

    for feat in features:
        c = feat['geometryChangeKey_']['target']['flatCoordinates']
        lista = []
        x = 0
        y = 0
        for i, c in enumerate(c):
            if (i % 2) == 0:
                x = c
            else:
                y = c
                lista.append((x, y))

        poly = Polygon(lista)

        xmin, ymin, xmax, ymax = poly.extent
        num_points = 50
        counter = 0
        while counter < num_points:
            x = random.uniform(xmin, xmax)
            y = random.uniform(ymin, ymax)

            point = Point(x, y)
            if poly.contains(Point(x, y)):
                try:
                    point_list = Site.objects.filter(sample_project_id=project_id,
                                                     point=point,
                                                     label_id=name_pk,
                                                     date_satellite=date_captured)
                    if point_list.count() > 0:
                        # si el punto ya estaba en la base de datos, entonces no se agrega
                        continue
                    else:
                        name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                        site = Site()
                        site.sample_project = Samplesproject.objects.get(pk=project_id)
                        site.label = Label.objects.get(pk=name_pk)
                        site.ground_photos = None
                        site.mpoly = None
                        site.point = point
                        site.line = None
                        site.site_type = "1"
                        site.site_name = str(name_pk) + "-" + name
                        site.date_satellite = date_captured
                        site.save()
                        counter += 1
                        print("counter" + str(counter))
                except:
                    pass

    print("saliendo add_point_in_polygon")
    return JsonResponse({'status': status, 'np': counter})


@login_required
def delete_point_in_line(request):
    from shapely.geometry import LineString, Point

    print("delete_point_in_line")
    status = 'ok'
    project_id = request.POST['pid']
    name_pk = request.POST['name_pk']
    feature_list = request.POST['features']
    date_sentinel = request.POST['date_sentinel']
    date_captured = datetime.strptime(date_sentinel, "%Y%m%d")
    features = json.loads(feature_list)

    point_list = Site.objects.filter(sample_project_id=project_id,
                                     label_id=name_pk,
                                     date_satellite=date_captured)
    for feat in features:
        c = feat['geometryChangeKey_']['target']['flatCoordinates']
        lista = []
        x = 0
        y = 0
        for i, c in enumerate(c):
            if (i % 2) == 0:
                x = c
            else:
                y = c
                lista.append((x, y))

        line = LineString(lista)
        counter = 0
        for e in point_list:
            point = Point(e.point.x, e.point.y)
            dist = line.distance(point)
            print(dist)
            if dist < 1e-4:
                print("entro")
                try:
                    qs = Site.objects.get(sample_project_id=project_id,
                                          point=e.point,
                                          site_name=e,
                                          date_satellite=date_captured)
                    qs.delete()
                    counter += 1
                except:
                    pass
    print("salinedo delete_point_in_line")
    return JsonResponse({'status': status, 'np': counter})


@login_required
def add_point_in_line(request):
    from shapely.geometry import LineString

    print("add_point_in_line")
    status = 'ok'
    project_id = request.POST['pid']
    name_pk = request.POST['name_pk']
    feature_list = request.POST['features']
    date_sentinel = request.POST['date_sentinel']
    date_captured = datetime.strptime(date_sentinel, "%Y%m%d")
    features = json.loads(feature_list)

    for feat in features:
        c = feat['geometryChangeKey_']['target']['flatCoordinates']
        lista = []
        x = 0
        y = 0
        for i, c in enumerate(c):
            if (i % 2) == 0:
                x = c
            else:
                y = c
                lista.append((x, y))

        line = LineString(lista)
        counter = 50

        for i in range(counter):
            pt = line.interpolate(random.random(), True)
            point = Point(pt.x, pt.y)

            point_list = Site.objects.filter(sample_project_id=project_id,
                                             point=point,
                                             label_id=name_pk,
                                             date_satellite=date_captured)
            if point_list.exists():
                # si el punto ya estaba en la base de datos, entonces no se agrega
                continue
            else:
                name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                site = Site()
                site.sample_project = Samplesproject.objects.get(pk=project_id)
                site.label = Label.objects.get(pk=name_pk)
                site.ground_photos = None
                site.mpoly = None
                site.point = point
                site.line = None
                site.site_type = "1"
                site.site_name = str(name_pk) + "-" + name
                site.date_satellite = date_captured
                site.save()

    print("saliendo add_point_in_line")
    return JsonResponse({'status': status, 'np': counter})


# Recibe el identificador del proyecto, el listado de features adicionados y borrados y
# la imagen de satelite de fondo
# convierte el json de los features en una lista de marcas. Recorre los features y
# en dependencia del status los adiciona o borra del modelo Site de django
@login_required
def save_feature_json(request):
    print("save_feature_json")
    status = 'ok'
    project_id = request.POST['pid']
    feature_list = request.POST['features']
    date_sentinel = request.POST['date_sentinel']
    date_captured = datetime.strptime(date_sentinel, "%Y%m%d")
    features = json.loads(feature_list)
    for i, feat in enumerate(features):
        st = feat['status']
        name_pk = feat['name_pk']
        point = Point(feat['feature']['flatCoordinates'])
        if st == 1:
            try:
                point_list = Site.objects.filter(sample_project_id=project_id,
                                                 point=point,
                                                 date_satellite=date_captured)
                if point_list.count() > 0:
                    # si el punto ya estaba en la base de datos, entonces no se agrega
                    continue
                else:
                    name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                    site = Site()
                    site.sample_project = Samplesproject.objects.get(pk=project_id)
                    site.label = Label.objects.get(pk=name_pk)
                    site.point = point
                    site.site_name = str(name_pk) + "-" + name
                    site.date_satellite = date_captured
                    site.save()
            except:
                pass
        if st == 2:
            try:
                qs = Site.objects.get(sample_project_id=project_id,
                                      point=point,
                                      label_id=name_pk,
                                      date_satellite=date_captured)
                qs.delete()

            except:
                pass
    return JsonResponse({'status': status})


# @login_required
# def process_shapes(request, project_id):
#     selected_project = Samplesproject.objects.get(pk=project_id)
#
#     geojson = {}
#     return JsonResponse(geojson)

# URL asociadas a la barra de edicion
@login_required
def load_feature_json(request, project_id, name_pk, date_sentinel):
    print("load_feature_json")
    date_captured = datetime.strptime(date_sentinel, "%Y%m%d")
    geojson = serialize('geojson',
                        Site.objects.filter(label_id=name_pk,
                                            sample_project_id=project_id,
                                            date_satellite=date_captured
                                            ),
                        geometry_field='point')
    res = json.loads(geojson)
    return JsonResponse(res)


# @login_required
# def select_samples(request, n_samples):
#     n_parcel = Site.objects.count()
#     n_parcel = 2000
#     places = []
#     for i in range(n_samples):
#         val = random.randint(0, n_parcel - 1)
#         if not places.__contains__(val):
#             places.append(val)
#
#     for i, v in enumerate(places):
#         print(i, v)
#     return


#  Cuando se crea el Grupo Shape se llama esta URL, para agregar a la capa
@login_required
def render_vector_json(request, project_id, shape):
    print("render_vector_json")
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name

    shp_dir_path = project_data_path + 'shape/' + project_name + '/' + shape
    shp_dir_path = shp_dir_path + '/' + os.listdir(shp_dir_path)[0]

    data = ""
    for a in os.listdir(shp_dir_path):
        fileName, ext = os.path.splitext(a)
        if ext.lower() == '.json':
            json_path = os.path.join(shp_dir_path, a)
            with open(json_path) as file:
                data = json.load(file)

    return JsonResponse(data)


@login_required
def unify_samples(request):
    print("unify_samples")
    project_id = request.POST['proj_pk']
    checked_image_id_list = request.POST.getlist('checked_image_id_list[]')

    project = Samplesproject.objects.get(pk=project_id)
    macro_project_id = project.macro_project_id
    macro_project = Macroproject.objects.get(pk=macro_project_id)

    project_name = str(project_id) + '-' + project.project_name
    macro_project_name = str(macro_project_id) + '-' + macro_project.macro_project_name

    creation_date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    for pk in checked_image_id_list:
        qs = Image.objects.get(pk=pk)
        date_image = qs.date_captured
        y = date_image.year
        if date_image.month < 10:
            m = '0' + str(date_image.month)
        else:
            m = str(date_image.month)

        if date_image.day < 10:
            d = '0' + str(date_image.day)
        else:
            d = str(date_image.day)

        ff = str(y) + str(m) + str(d)

        if qs.platform == '1':
            createMacroProyectUnitedDataset.create_dataset_unify(macro_project_name, creation_date,
                                                                 project_name,
                                                                 'sentinel', ff)
        else:
            createMacroProyectUnitedDataset.create_dataset_unify(macro_project_name, creation_date,
                                                                 project_name,
                                                                 'drones', ff)

    json_dict = {
        'status': "ok",
    }

    print("unify_samples ----FIN")
    return redirect('dashboard_home')
    # return JsonResponse(json_dict)


@login_required
def train_validation_test(request):
    print("train_validation_test")
    project_id = request.POST['proj_pk']
    checked_image_id_list = request.POST.getlist('checked_image_id_list[]')

    project = Samplesproject.objects.get(pk=project_id)
    macro_project_id = project.macro_project_id
    macro_project = Macroproject.objects.get(pk=macro_project_id)

    project_name = str(project_id) + '-' + project.project_name
    macro_project_name = str(macro_project_id) + '-' + macro_project.macro_project_name

    for pk in checked_image_id_list:
        qs = Image.objects.get(pk=pk)
        date_image = qs.date_captured
        y = date_image.year
        if date_image.month < 10:
            m = '0' + str(date_image.month)
        else:
            m = str(date_image.month)

        if date_image.day < 10:
            d = '0' + str(date_image.day)
        else:
            d = str(date_image.day)

        ff = str(y) + str(m) + str(d)
        if qs.platform == '1':
            createMacroProyectDataset.create_dataset(macro_project_name, project_name, 'sentinel', ff)
        else:
            createMacroProyectDataset.create_dataset(macro_project_name, project_name, 'drones', ff)

    json_dict = {
        'status': "ok",
    }

    print("train_validation_test ----FIN")
    return redirect('dashboard_home')
    # return JsonResponse(json_dict)


@login_required
def extract_sites(request):
    print("extract_sites")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/extract_sites.html', context=context)


@login_required
def prepare_extract_sites(request):
    print("prepare_extract_sites  -- inicio")
    project_id = request.POST['proj_pk']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    checked_image_id_list = request.POST.getlist('checked_image_id_list[]')

    for pk in checked_image_id_list:
        qs = Image.objects.get(pk=pk)
        date_image = qs.date_captured
        y = date_image.year
        if date_image.month < 10:
            m = '0' + str(date_image.month)
        else:
            m = str(date_image.month)

        if date_image.day < 10:
            d = '0' + str(date_image.day)
        else:
            d = str(date_image.day)

        ff = str(y) + str(m) + str(d)

        path = project_data_path + 'images/' + project_name
        if qs.platform == '1':
            dir_images = path + '/sentinel/' + ff + "/"
            cutSentinelSite.cut_sentinel_site(dir_images, project_id, project_name, ff)
        else:
            dir_images = path + '/drones/' + ff + "/"
            cutDronesSite.cut_drones_site(project_id, project_name, ff, 'natural_color.tif')
            # cutDronesSite.cut_drones_site(project_id, ff, 'texture_features.tif')

    json_dict = {
        'status': "ok",
    }

    print("prepare_extract_sites ----FIN")
    return JsonResponse(json_dict)


@login_required
def ripe_image(request):
    print("ripe_image")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/cane_ripe.html', context=context)


@login_required
def prepare_ripe(request):
    print("prepare_ripe  - inicio")
    project_id = request.POST['proj_pk']
    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name
    checked_image_id_list = request.POST.getlist('checked_image_id_list[]')

    for pk in checked_image_id_list:
        qs = Image.objects.get(pk=pk)
        date_image = qs.date_captured
        y = date_image.year
        if date_image.month < 10:
            m = '0' + str(date_image.month)
        else:
            m = str(date_image.month)

        if date_image.day < 10:
            d = '0' + str(date_image.day)
        else:
            d = str(date_image.day)

        ff = str(y) + str(m) + str(d)
        if qs.platform == '1':
            plat = 'sentinel'
        else:
            continue

        name = qs.name
        path = project_data_path + 'images/' + project_name
        dir_images = path + '/' + plat + '/' + ff + "/" + name + "/"
        maduracion.create_ripe(dir_images)

    json_dict = {
        'status': "ok",
    }

    print("ripe_image - fin")
    return JsonResponse(json_dict)


@login_required
def shp2geojson(request):
    print("shp2geojson")
    status = 'ok'
    project_list = request.user.samplesproject_set.all()
    context = {
        "project_list": project_list,
        "status": status
    }
    return render(request, 'data_annotator/shp2geojson.html', context=context)


@login_required
def convert_shp2geojson(request):
    print("shp2geojson - init")
    project_id = request.POST['proj_pk']
    checked_shape_id_list = request.POST.getlist('checked_shape_id_list[]')

    project = Samplesproject.objects.get(pk=project_id)
    project_name = str(project_id) + '-' + project.project_name

    for pk in checked_shape_id_list:
        qs = Shape.objects.get(pk=pk)
        date_shape = qs.date_captured
        y = date_shape.year
        if date_shape.month < 10:
            m = '0' + str(date_shape.month)
        else:
            m = str(date_shape.month)

        if date_shape.day < 10:
            d = '0' + str(date_shape.day)
        else:
            d = str(date_shape.day)

        ff = str(y) + str(m) + str(d)

        driver = ogr.GetDriverByName('ESRI Shapefile')

        shp_dir_path = project_data_path + 'shape/' + project_name + '/' + ff
        shp_dir_path = shp_dir_path + '/' + os.listdir(shp_dir_path)[0]

        for a in os.listdir(shp_dir_path):
            file_name, ext = os.path.splitext(a)
            if ext.lower() == '.shp':
                shp_path = os.path.join(shp_dir_path, a)
                data_source = driver.Open(shp_path, 0)

                fc = {
                    'type': 'FeatureCollection',
                    'features': []
                }

                lyr = data_source.GetLayer(0)

                # input SpatialReference
                in_spatial_ref = lyr.GetSpatialRef()

                # output SpatialReference
                out_spatial_ref = osr.SpatialReference()
                out_spatial_ref.ImportFromEPSG(4326)

                # create the CoordinateTransformation
                coord_trans = osr.CoordinateTransformation(in_spatial_ref, out_spatial_ref)

                for feature in lyr:
                    geom = feature.GetGeometryRef()
                    geom.Transform(coord_trans)
                    feature.SetGeometry(geom)
                    fc['features'].append(feature.ExportToJson(as_object=True))

                out_file = os.path.join(shp_dir_path, file_name + '.json')
                with open(out_file, 'w') as f:
                    json.dump(fc, f)

    json_dict = {
        'status': "ok",
    }
    print("shp2geojson  - fin")
    return JsonResponse(json_dict)

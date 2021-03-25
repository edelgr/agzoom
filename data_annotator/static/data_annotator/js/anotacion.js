$(document).ready(function () {
    window.pt = 0;
    window.nclasses = 0;
    window.legend_name = [];
    window.legend_pk = [];
    window.legend_color = [];
    window.drawLayer = [];
    window.samplingSource = [];
    window.deletedSource = [];
    window.addedSource = [];
    window.style_sampling = [];
    window.inter_sampling = [];
    window.inter_deleting = [];
    window.vector = 0
    window.layer_list = []

    let proj = window.ap

    if (proj !== "") {
        init(proj)

        let ruta_drone_tiles = "/serving_drone_tiles/";
        let ruta_classification_tiles = "/serving_classification_tiles/";

        let projExtent = ol.proj.get('EPSG:3857').getExtent();
        let startResolution = ol.extent.getWidth(projExtent) / 256;
        let resolutions = new Array(24);
        for (let i = 0, ii = resolutions.length; i < ii; ++i) {
            resolutions[i] = startResolution / Math.pow(2, i);
        }

        let pedit
        let editbar

        function edit_toolbar() {

            map.removeControl(mainbar)

            // Main control bar
            mainbar = new ol.control.Bar();
            map.addControl(mainbar);
            // Edit control bar
            editbar = new ol.control.Bar({
                toggleOne: true,	// one control active at the same time
                group: false			// group controls together
            });
            mainbar.addControl(editbar);
            // Add selection tool:
            //  1- a toggle control with a select interaction
            //  2- an option bar to delete / get information on the selected feature
            var sbar = new ol.control.Bar();
            sbar.addControl(new ol.control.Button({
                html: '<i class="fa fa-times"></i>',
                title: "Borrar muestras puntuales",
                handleClick: function () {
                    let clase_pk = $("#label-select").val();
                    let index = indexInClasses_list(clase_pk);

                    let selectedFeatures = selectCtrl.getInteraction().getFeatures();
                    if (!selectedFeatures.getLength()) {
                        info("Seleccione primero un objeto...");
                    } else {
                        var feature_0 = selectedFeatures.item(0);

                        if (feature_0.getGeometry().getType() === "Point") {
                            for (var i = 0; i < selectedFeatures.getLength(); i++) {
                                let feature = selectedFeatures.item(i)
                                window.samplingSource[index].removeFeature(feature);
                                if (include(window.addedSource[index], feature))
                                    window.addedSource[index].removeFeature(feature);
                                window.deletedSource[index].addFeature(feature);
                            }
                            let nsamples = window.samplingSource[index].getFeatures().length
                            $("#nsamples").text(nsamples.toString())
                            info(selectedFeatures.getLength() + " objectos borrados.");
                        }

                        if (feature_0.getGeometry().getType() === "LineString") {
                            let features = []
                            for (let i = 0; i < selectedFeatures.getLength(); i++) {
                                let feature = selectedFeatures.item(i)
                                let newFeature = new ol.Feature(feature.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326'));
                                features.push(newFeature)
                                let myjson = JSON.stringify(features)

                                let pid = $("#proj-select").val()
                                let date_sentinel = $("#sentinel-select").val();
                                $.post('/delete_point_in_line/',
                                    {
                                        'pid': pid,
                                        'name_pk': window.legend_pk[index],
                                        'features': myjson,
                                        'date_sentinel': date_sentinel
                                    },
                                    function (data) {
                                        let np = data['np']
                                        info("Borrados " + np.toString() + " puntos.");
                                        clean_class_selected()
                                        load_class_selected()
                                    })
                                window.vector.getSource().removeFeature(feature);
                            }
                            selectCtrl.getInteraction().getFeatures().clear();
                        }

                        if (feature_0.getGeometry().getType() === "Polygon") {
                            let features = []
                            for (let i = 0; i < selectedFeatures.getLength(); i++) {
                                let feature = selectedFeatures.item(i)
                                let newFeature = new ol.Feature(feature.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326'));
                                features.push(newFeature)
                                let myjson = JSON.stringify(features)

                                let pid = $("#proj-select").val()
                                let date_sentinel = $("#sentinel-select").val();
                                $.post('/delete_point_in_polygon/',
                                    {
                                        'pid': pid,
                                        'name_pk': window.legend_pk[index],
                                        'features': myjson,
                                        'date_sentinel': date_sentinel
                                    },
                                    function (data) {
                                        let np = data['np']
                                        info("Borrados " + np.toString() + " puntos.");
                                        clean_class_selected()
                                        load_class_selected()
                                    })
                                window.vector.getSource().removeFeature(feature);
                            }
                            selectCtrl.getInteraction().getFeatures().clear();
                        }
                    }
                }
            }));

            sbar.addControl(new ol.control.Button({
                    html: '<i class="fa fa-plus"></i>',
                    title: "Adicionar muestras puntuales",
                    handleClick: function () {
                        let clase_pk = $("#label-select").val();
                        let index = indexInClasses_list(clase_pk);

                        let selectedFeatures = selectCtrl.getInteraction().getFeatures();
                        if (!selectedFeatures.getLength()) {
                            info("Seleccione primero un objeto...");
                        } else {
                            var feature_0 = selectedFeatures.item(0);

                            // Point
                            if (feature_0.getGeometry().getType() === "Point") {
                                info("El punto ya estaba adicionado.");
                            }

                            // LineString
                            if (feature_0.getGeometry().getType() === "LineString") {
                                let features = []
                                for (let i = 0; i < selectedFeatures.getLength(); i++) {
                                    let feature = selectedFeatures.item(i)
                                    let newFeature = new ol.Feature(feature.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326'));
                                    features.push(newFeature)
                                    let myjson = JSON.stringify(features)

                                    let pid = $("#proj-select").val()
                                    let date_sentinel = $("#sentinel-select").val();
                                    $.post('/add_point_in_line/',
                                        {
                                            'pid': pid,
                                            'name_pk': window.legend_pk[index],
                                            'features': myjson,
                                            'date_sentinel': date_sentinel
                                        },
                                        function (data) {
                                            let np = data['np']
                                            info("Adicionados " + np.toString() + " puntos.");
                                            clean_class_selected()
                                            load_class_selected()
                                        })
                                    window.vector.getSource().removeFeature(feature);
                                }
                                selectCtrl.getInteraction().getFeatures().clear();
                            }

                            // Polygon
                            if (feature_0.getGeometry().getType() === "Polygon") {
                                let features = []
                                for (let i = 0; i < selectedFeatures.getLength(); i++) {
                                    let feature = selectedFeatures.item(i)
                                    let newFeature = new ol.Feature(feature.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326'));
                                    features.push(newFeature)
                                    let myjson = JSON.stringify(features)

                                    let pid = $("#proj-select").val()
                                    let date_sentinel = $("#sentinel-select").val();
                                    $.post('/add_point_in_polygon/',
                                        {
                                            'pid': pid,
                                            'name_pk': window.legend_pk[index],
                                            'features': myjson,
                                            'date_sentinel': date_sentinel
                                        },
                                        function (data) {
                                            let np = data['np']
                                            info("Adicionados " + np.toString() + " puntos.");
                                            clean_class_selected()
                                            load_class_selected()
                                        })
                                    window.vector.getSource().removeFeature(feature);
                                }
                                selectCtrl.getInteraction().getFeatures().clear();
                            }
                        }
                    }
                }
                )
            );

            sbar.addControl(new ol.control.Button({
                    html: '<i class="fa fa-scissors"></i>',
                    title: "Cortar imagen",
                    handleClick: function () {
                        let selectedFeatures = selectCtrl.getInteraction().getFeatures();
                        if (!selectedFeatures.getLength()) {
                            info("Seleccione primero un objeto...");
                        } else {
                            var feature_0 = selectedFeatures.item(0);
                            if (feature_0.getGeometry().getType() === "Polygon") {
                                let features = []
                                for (let i = 0; i < selectedFeatures.getLength(); i++) {
                                    let feature = selectedFeatures.item(i)
                                    let newFeature = new ol.Feature(feature.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326'));
                                    features.push(newFeature)
                                }

                                let myjson = JSON.stringify(features)

                                let pid = $("#proj-select").val()
                                let date_sentinel = $("#sentinel-select").val();
                                let vl = visible_layers()

                                if (vl.length > 1) {
                                    alert("Mas de una imagen visible")
                                } else {
                                    if (vl.length === 0) {
                                        alert("No hay imagen visible")
                                    } else {
                                        let name = vl[0].get('title')[0]
                                        $.post('/cut_image/',
                                            {
                                                'pid': pid,
                                                'features': myjson,
                                                'date_sentinel': date_sentinel,
                                                'name': name
                                            },
                                            function (data) {
                                                window.vector.getSource().clear()
                                            })
                                    }
                                }
                            }
                            selectCtrl.getInteraction().getFeatures().clear();
                        }
                    }
                })
            );

            sbar.addControl(new ol.control.Button({
                html: '<i class="fa fa-info"></i>',
                title: "Informaciones",
                handleClick: function () {
                    switch (selectCtrl.getInteraction().getFeatures().getLength()) {
                        case 0:
                            info("Seleccion primero un objeto...");
                            break;
                        case 1:
                            let selectedFeatures = selectCtrl.getInteraction().getFeatures();
                            if (!selectedFeatures.getLength()) {
                                info("Seleccione primero un objeto...");
                            } else {
                                var feature_0 = selectedFeatures.item(0);
                                show_feature_info(feature_0)
                            }

                            let clase_pk = $("#label-select").val();
                            let index = indexInClasses_list(clase_pk);
                            // info("Intentando procesar objetos de la clase " + window.legend_name[index]);
                            window.vector.getSource().clear()
                            break;
                        default:
                            info(selectCtrl.getInteraction().getFeatures().getLength() + " objetos seleccionados.");
                            window.vector.getSource().clear()
                            break;
                    }
                }
            }));

            var selectCtrl = new ol.control.Toggle({
                html: '<i class="fa fa-hand-pointer"></i>',
                title: "Seleccionar puntos, polígonos, rectángulo o líneas",
                interaction: new ol.interaction.Select({hitTolerance: 2}),
                bar: sbar,
                autoActivate: true,
                active: true
            });

            editbar.addControl(selectCtrl);


            let clase_pk = $("#label-select").val();
            let index = indexInClasses_list(clase_pk);
            pedit = new ol.control.Toggle({
                html: '<i class="fa fa-map-marker" ></i>',
                title: 'Marcar muestras puntuales',
                interaction: window.inter_sampling[index]
            })

            editbar.addControl(pedit);

            var ledit = new ol.control.Toggle({
                html: '<i class="fa fa-share-alt" ></i>',
                title: 'Marcar linea para adicionar o borrar muestras',
                interaction: new ol.interaction.Draw({
                    type: 'LineString',
                    source: window.vector.getSource(),
                    // Count inserted points
                    geometryFunction: function (coordinates, geometry) {
                        if (geometry) geometry.setCoordinates(coordinates);
                        else geometry = new ol.geom.LineString(coordinates);
                        this.nbpts = geometry.getCoordinates().length;
                        return geometry;
                    }
                }),
                // Options bar associated with the control
                bar: new ol.control.Bar({
                    controls: [
                        new ol.control.TextButton({
                            html: 'undo',
                            title: "Borrar el ultimo punto",
                            handleClick: function () {
                                if (ledit.getInteraction().nbpts > 1) ledit.getInteraction().removeLastPoint();
                            }
                        }),
                        new ol.control.TextButton({
                            html: 'Finish',
                            title: "terminar",
                            handleClick: function () {
                                // Prevent null objects on finishDrawing
                                if (ledit.getInteraction().nbpts > 2) ledit.getInteraction().finishDrawing();
                            }
                        })
                    ]
                })
            });
            editbar.addControl(ledit);


            var fedit = new ol.control.Toggle({
                html: '<i class="fa fa-bookmark fa-rotate-270" ></i>',
                title: 'Marcar poligono para adicionar o borrar muestras',
                interaction: new ol.interaction.Draw({
                    type: 'Polygon',
                    source: window.vector.getSource(),
                    geometryFunction: function (coordinates, geometry) {
                        save_all_classes()

                        this.nbpts = coordinates[0].length;
                        if (geometry) geometry.setCoordinates([coordinates[0].concat([coordinates[0][0]])]);
                        else geometry = new ol.geom.Polygon(coordinates);
                        return geometry;
                    }
                }),
                // Options bar associated with the control
                bar: new ol.control.Bar({
                    controls: [new ol.control.TextButton({
                        html: 'undo',//'<i class="fa fa-mail-reply"></i>',
                        title: "borrar ultimo punto",
                        handleClick: function () {
                            if (fedit.getInteraction().nbpts > 1) fedit.getInteraction().removeLastPoint();
                        }
                    }),
                        new ol.control.TextButton({
                            html: 'finish',
                            title: "terminar",
                            handleClick: function () {
                                // Prevent null objects on finishDrawing
                                if (fedit.getInteraction().nbpts > 3) fedit.getInteraction().finishDrawing();
                            }
                        })
                    ]
                })
            });
            editbar.addControl(fedit);

            var redit = new ol.control.Toggle({
                html: '<i class="fa fa-bookmark" ></i>',
                title: 'Marcar un rectangulo para adicionar o borrar muestras',
                interaction: new ol.interaction.Draw({
                    type: 'LineString',
                    source: window.vector.getSource(),
                    maxPoints: 2,
                    geometryFunction: function (coordinates, geometry) {
                        if (!geometry) {
                            geometry = new ol.geom.Polygon(coordinates);
                        }
                        var start = coordinates[0];
                        var end = coordinates[1];
                        geometry.setCoordinates([
                            [start, [start[0], end[1]], end, [end[0], start[1]], start]
                        ]);
                        return geometry;
                    }
                }),
            });
            editbar.addControl(redit);

            // Add a simple push button to clean all features
            var erase = new ol.control.Button({
                html: '<i class="fa fa-eraser"></i>',
                title: "Borrar todas las muestras de la clase",
                handleClick: function (e) {
                    let name_pk = $("#label-select").val();
                    let pid = $("#proj-select").val()
                    let date_sentinel = $("#sentinel-select").val();
                    $.post('/delete_sites/',
                        {
                            'pid': pid,
                            'name_pk': name_pk,
                            "date_sentinel": date_sentinel
                        },
                        function (data) {
                            let status = data['status']
                            clean_class_selected()
                            $("#label-select").val("")
                            $("#nsamples").hide()
                        }
                    )
                }
            });

            mainbar.addControl(erase);

            // Add a simple push button to clean all features
            var marker = new ol.control.Button({
                html: '<i class="fa fa-map-marked"></i>',
                title: "Cargar las muestras de todas las clases",
                handleClick: function (e) {
                    load_all_classes()
                    $("#label-select").val("")
                    $("#nsamples").hide()
                }
            });

            mainbar.addControl(marker);

            var upload = new ol.control.Button({
                html: '<i class="fa fa-upload"></i>',
                title: "Subir las muestras de la clase",
                handleClick: function (e) {
                    // save_all_classes()
                    // clean_all_classes()
                    $("#import-id").show()
                }
            });
            mainbar.addControl(upload);

            // Add a simple push button to save features
            //var download = new ol.control.Button({
            var download = new customControl();
            mainbar.addControl(download);

            // Add a simple push button to save features
            var save = new ol.control.Button({
                html: '<i class="fa fa-save"></i>',
                title: "Guardar las muestras de la clase",
                handleClick: function (e) {
                    save_all_classes()
                    clean_all_classes()
                    $("#label-select").val("")
                    $("#nsamples").hide()
                }
            });
            mainbar.addControl(save);
        }


        let customControl = function (opt_options) {
            let pid = $("#proj-select").val()
            let clase_pk = $("#label-select").val();
            let date_sentinel = $("#sentinel-select").val();

            var anchor = document.createElement('a');
            anchor.href = '/download_muestras/' + pid + '/' + clase_pk + '/' + date_sentinel + '/';
            anchor.type = 'button';
            anchor.innerHTML = '<i class="fa fa-download"></i>';
            anchor.className = 'download-a';
            anchor.title = 'Bajar las muestras de la clase';

            var element = document.createElement('div');
            element.className = 'ol-button ol-unselectable ol-control';
            element.appendChild(anchor);

            ol.control.Control.call(this, {
                element: element
            });
        };
        ol.inherits(customControl, ol.control.Control);


        // Show info
        function info(i) {
            $("#information-feature").html(i || "");
        }


        function load_all_classes() {
            let pid = $("#proj-select").val()
            let date_sentinel = $("#sentinel-select").val();
            for (let i = 0; i < window.nclasses; i++) {
                load_class(pid, i, date_sentinel)
            }
        }

        function load_class_selected() {
            let index = indexInClasses_list($("#label-select").val());
            let pid = $("#proj-select").val()
            let date_sentinel = $("#sentinel-select").val();
            load_class(pid, index, date_sentinel)
        }

        function load_class(pid, index, date_sentinel) {
            window.deletedSource[index] = new ol.source.Vector();
            window.addedSource[index] = new ol.source.Vector();
            let url = '/load_feature_json/' + pid + '/' + window.legend_pk[index] + '/' + date_sentinel
            $.get(url, function (data, status) {
                var format = new ol.format.GeoJSON({
                    featureProjection: "EPSG:3857"
                });
                window.samplingSource[index] = new ol.source.Vector({
                    features: format.readFeatures(data),
                });
                window.drawLayer[index].setSource(window.samplingSource[index]);

                let intera = new ol.interaction.Draw({
                    source: window.samplingSource[index],
                    type: 'Point',
                    style: window.style_sampling[index]
                })
                intera.on('drawstart', function (evt) {
                    window.addedSource[index].addFeature(evt.feature)
                    window.samplingSource[index].addFeature(evt.feature)
                    show_nsamples()

                });
                window.inter_sampling[index] = intera
                show_nsamples()
            })
        }

        function show_nsamples() {
            let index = indexInClasses_list($("#label-select").val());
            $("#circle").show()
            $("#circle").css("background-color", window.legend_color[index]);
            $("#nsamples").show()
            let nsamples = window.samplingSource[index].getFeatures().length
            $("#nsamples").text(nsamples.toString())
        }

        function save_all_classes() {
            let pid = $("#proj-select").val()
            let date_sentinel = $("#sentinel-select").val();
            let features = [];
            for (let i = 0; i < window.nclasses; i++) {
                window.addedSource[i].forEachFeature(function (feature) {
                    let newFeature = new ol.Feature(feature.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326'));
                    let feat_added = {}
                    feat_added['status'] = 1
                    feat_added['name_pk'] = window.legend_pk[i]
                    feat_added['feature'] = newFeature.getGeometry()
                    features.push(feat_added)
                });
            }
            for (let i = 0; i < window.nclasses; i++) {
                window.deletedSource[i].forEachFeature(function (feature) {
                    let newFeature = new ol.Feature(feature.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326'));
                    let feat_deleted = {}
                    feat_deleted['status'] = 2
                    feat_deleted['name_pk'] = window.legend_pk[i]
                    feat_deleted['feature'] = newFeature.getGeometry()
                    features.push(feat_deleted)
                });
            }

            let myjson = JSON.stringify(features)
            $.post('/save_feature_json/',
                {
                    'pid': pid,
                    'features': myjson,
                    'date_sentinel': date_sentinel
                },
                function (data) {
                }
            )
        }

        $("#import-id").on('change', function (e) {
            console.log("import id changed")
            var filename = this.files[0];
            console.log(filename)
            import_class(filename)
        })

        function import_class(filename) {
            console.log("entro a import-id")
            var reader = new FileReader();

            reader.onload = function (e) {
                var aa = JSON.parse(e.target.result)
                console.log(aa)

                let features = [];
                let clase_pk = $("#label-select").val();

                for (let k = 0; k < aa.features.length; k++) {
                    let feature = aa.features[k]
                    let lon = feature.geometry.coordinates[0]
                    let lat = feature.geometry.coordinates[1]
                    let geometry = new ol.geom.Point([lon, lat])

                    let feat_added = {}
                    feat_added['status'] = 1
                    feat_added['name_pk'] = clase_pk
                    feat_added['feature'] = geometry
                    features.push(feat_added)
                }

                let myjson = JSON.stringify(features)

                let pid = $("#proj-select").val()
                let date_sentinel = $("#sentinel-select").val();
                $.post('/save_feature_json/',
                    {
                        'pid': pid,
                        'features': myjson,
                        'date_sentinel': date_sentinel
                    },
                    function (data) {
                        load_class_selected()
                    });

                $("#import-id").hide()
            }
            reader.readAsText(filename, "json");
        }

        function clean_class_selected() {
            let clase_pk = $("#label-select").val();
            let index = indexInClasses_list(clase_pk);
            window.samplingSource[index].clear()
            window.addedSource[index].clear()
            window.deletedSource[index].clear()

            $("#circle").hide()
            $("#nsamples").hide()
        }

        function clean_all_classes() {
            for (let i = 0; i < window.nclasses; i++) {
                window.samplingSource[i].clear()
                window.addedSource[i].clear()
                window.deletedSource[i].clear()
            }

            $("#circle").hide()
            $("#nsamples").hide()
        }

        $("#label-select").on('change', (function () {
            let clase_pk = $("#label-select").val();
            if (clase_pk !== "") {
                save_all_classes()
                clean_all_classes()
                load_class_selected()

                show_parcels(clase_pk)
            }


            // let pid = $("#proj-select").val()
            // let label_name = window.legend_name[index]
            // $.post('/templates_image/',
            //     {'pid': pid, 'label_name': label_name},
            //     function (data) {
            //         let status = data['status']
            //         let templates_image_list = data['templates_image_list']
            //         var carousel_inner = ''
            //         for (let i = 0; i < templates_image_list.length; i++) {
            //             let img = templates_image_list[i]
            //             if (i == 0) {
            //                 var image_carousel = '<div class="carousel-item active">'
            //             } else {
            //                 var image_carousel = '<div class="carousel-item">'
            //             }
            //             image_carousel += '<img class="d-block w-100" src=' + '"data:image/png;base64,' + img + '"' + '   alt="' + i.toString() + '">'
            //             image_carousel += '</div>'
            //             // console.log(image_carousel)
            //             carousel_inner += image_carousel
            //         }
            //         console.log(carousel_inner)
            //         $('.carousel-inner').html(carousel_inner);
            //         $('.carousel').carousel()
            //     })

        }));

        $("#button-ortofoto").click(function () {
            $('#drones-select').css("display", "block")
            $('#sentinel-select').css("display", "block")
            $('#shape-select').css("display", "block")
            $('#image-select').css("display", "none")
            $("#carouselExampleIndicators").css("display", "block")
            prepare_selects_drones_sentinel()
            prepare_selects_shape()
        });

        function visible_layers() {
            let visible_layers = [];
            map.getLayers().forEach(function (layer) {
                if (layer.get('name') === 'Sentinel') {
                    layer.getLayers().forEach(function (l) {
                        if (l.get('visible') === true) {
                            visible_layers.push(l)
                        }
                    })
                }
                if (layer.get('name') === 'Drones' && layer.get('visible') === true) {
                    visible_layers.push(layer)
                }
            })
            return visible_layers
        }

        function shape_muestras_to_top() {
            let shapeTemp = null
            map.getLayers().forEach(function (layer) {
                if (layer.get('name') !== undefined && layer.get('name') === 'Shape') {
                    shapeTemp = layer;
                }
            })
            if (shapeTemp !== null) {
                map.removeLayer(shapeTemp);
                map.getLayers().push(shapeTemp);
            }
            let muestrasTemp = null
            map.getLayers().forEach(function (layer) {
                if (layer.get('name') !== undefined && layer.get('name') === 'Muestras') {
                    muestrasTemp = layer;
                }
            })
            if (muestrasTemp !== null) {
                map.removeLayer(muestrasTemp);
                map.getLayers().push(muestrasTemp);
            }
            let auxiliarTemp = null
            map.getLayers().forEach(function (layer) {
                if (layer.get('name') !== undefined && layer.get('name') === 'Auxiliar') {
                    auxiliarTemp = layer;
                }
            })
            if (auxiliarTemp !== null) {
                map.removeLayer(auxiliarTemp);
                map.getLayers().push(auxiliarTemp);
            }
        }

        $("#drones-select").on('change', (function () {
            let proj = $("#proj-select").val()
            let date_drones = $("#drones-select").val();
            if (proj !== "" && date_drones !== "") {
                let dronesTemp = null
                map.getLayers().forEach(function (layer) {
                    if (layer.get('name') !== undefined && layer.get('name') === 'Drones') {
                        dronesTemp = layer;
                    }
                })
                if (dronesTemp !== null) map.removeLayer(dronesTemp)
                createGroupDrones(proj, date_drones);

                edit_toolbar()
            }
        }))

        function createGroupDrones(proj, date_drones) {
            if (proj !== "" && date_drones !== "") {
                $.post('/get_date_image/',
                    {
                        'proj_pk': proj,
                        'date': date_drones,
                        'platform': '2'
                    },
                    function (data) {
                        let mbtiles_list = data['mbtiles_list'];
                        let name_list = data['name_list'];
                        window.layer_list = []
                        for (let j = 0; j < mbtiles_list.length; j++) {
                            window.layer_list.push(new ol.layer.Tile(
                                {
                                    name: "Drones",
                                    title: name_list[j] + "-" + mbtiles_list[j],
                                    visible: true,
                                    opacity: 0.8,
                                    source: new ol.source.TileImage({
                                        projection: 'EPSG:3857',
                                        tileUrlFunction: function (tileCoord) {
                                            if (tileCoord === null) return undefined;
                                            let z = tileCoord[0];
                                            let x = tileCoord[1];
                                            let y = tileCoord[2];
                                            y = (1 << z) - y - 1;
                                            return "/drones_" + mbtiles_list [j] + "/" + proj + "/" + date_drones + "/" + name_list[j] + "/" + z + "/" + x + "/" + y + "/"
                                        }
                                    })
                                }))
                        }

                        map.getLayers().push(new ol.layer.Group({
                            name: 'Drones',
                            title: 'Drones' + '-' + date_drones,
                            fold: 'open',
                            layers: window.layer_list
                        }))
                        shape_muestras_to_top()
                    })
            }

        }

        $("#sentinel-select").on('change', (function () {
            let proj = $("#proj-select").val()
            let date_sentinel = $("#sentinel-select").val();

            console.log('proj ' + proj + ' date_sentinel ' + date_sentinel)
            if (proj !== "" && date_sentinel !== "") {
                let sentinelTemp = null
                map.getLayers().forEach(function (layer) {
                    if (layer.get('name') !== undefined && layer.get('name') === 'Sentinel') {
                        sentinelTemp = layer;
                    }
                })
                if (sentinelTemp != null) map.removeLayer(sentinelTemp)
                createGroupSentinel(proj, date_sentinel);

                edit_toolbar()
            }
        }))

        function createGroupSentinel(proj, date_sentinel) {
            if (proj !== "" && date_sentinel !== "") {
                $.post('/get_date_image/',
                    {
                        'proj_pk': proj,
                        'date': date_sentinel,
                        'platform': '1'
                    },
                    function (data) {
                        let mbtiles_list = data['mbtiles_list'];
                        let name_list = data['name_list'];
                        window.layer_list = []
                        for (let j = 0; j < mbtiles_list.length; j++) {
                            console.log(mbtiles_list)
                            window.layer_list.push(new ol.layer.Tile(
                                {
                                    name: "Sentinel",
                                    title: name_list[j] + "-" + mbtiles_list[j],
                                    visible: true,
                                    opacity: 0.8,
                                    source: new ol.source.TileImage({
                                        projection: 'EPSG:3857',
                                        tileUrlFunction: function (tileCoord) {
                                            if (tileCoord === null) return undefined;
                                            let z = tileCoord[0];
                                            let x = tileCoord[1];
                                            let y = tileCoord[2];
                                            y = (1 << z) - y - 1;
                                            return "/sentinel_" + mbtiles_list [j] + "/" + proj + "/" + date_sentinel + "/" + name_list[j] + "/" + z + "/" + x + "/" + y + "/"
                                        }
                                    })
                                }))
                        }

                        map.getLayers().push(new ol.layer.Group({
                            name: 'Sentinel',
                            title: 'Sentinel' + '-' + date_sentinel,
                            fold: 'open',
                            layers: window.layer_list
                        }))
                        shape_muestras_to_top()
                    })
            }

        }

        $("#shape-select").on('change', (function () {
            let proj = $("#proj-select").val()
            let shape = $("#shape-select").val()
            if (proj !== "" && shape !== "") {
                let shapeTemp = null
                map.getLayers().forEach(function (layer) {
                    if (layer.get('name') !== undefined && layer.get('name') === 'Shape') {
                        shapeTemp = layer;
                    }
                })
                if (shapeTemp !== null) map.removeLayer(shapeTemp)
                createLayerShape(proj, shape);

                edit_toolbar()
            }
        }))

        function createLayerShape(proj, shape) {
            let vectorSource = new ol.source.Vector({
                projection: 'EPSG:3857',
                url: '/render_vector_json/' + proj + '/' + shape,
                format: new ol.format.GeoJSON()
            });

            let layer_shape = new ol.layer.Vector({
                name: 'Shape',
                title: 'Shape' + '-' + shape,
                visible: true,
                opacity: 0.5,
                source: vectorSource,
            });

            layer_shape.setStyle(function (feature) {
                let fillColor = 'rgb(0, 0, 0, 0.5)';
                return new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: fillColor
                    }),
                    stroke: new ol.style.Stroke({
                        color: 'rgba(4, 4, 4, 1)',
                        width: 1
                    })
                });
            });
            map.getLayers().push(layer_shape)
            shape_muestras_to_top()
        }

        function init(proj) {
            $("#panel-id").css("display", "block");
            $.post('/init_sampling/',
                {'proj_pk': proj},
                function (data) {
                    let status = data['status']
                    window.pt = data['project_type']
                    window.legend_name = data['legend_list']
                    window.legend_pk = data['legend_pk_list']
                    window.legend_color = data['legend_color_list']
                    window.nclasses = window.legend_name.length;

                    var layerArray, len, layer;
                    layerArray = map.getLayers().getArray();
                    len = layerArray.length;
                    while (len > 0) {
                        layer = layerArray[len - 1];
                        map.removeLayer(layer);
                        len = layerArray.length;
                    }

                    window.vector = new ol.layer.Vector({
                        name: 'Auxiliar',
                        source: new ol.source.Vector(),
                        title: 'Auxiliar'
                    })

                    let layers = map.getLayers();
                    layers.push(window.vector);
                    layers.push(createGroupMuestras());
                    layers.push(createGroupBase())

                    //////////////////////////////////////////////////////////////////

                    var options = '<option value="">Selecciona la clase</option>';
                    $('#legend-table > tbody:last-child').empty()
                    for (let i = 0; i < window.nclasses; i++) {
                        let pk = window.legend_pk[i]
                        let color = window.legend_color[i]
                        let nombre = window.legend_name[i]
                        options += '<option value="' + pk + '" data-color="' + color + '">' + nombre + '</option>'
                        $('#legend-table > tbody:last-child').append(
                            '<tr>   ' +
                            '<td class="color-sample" style="background-color: ' + color + '"></td>' +
                            '<td class="nombre-sample">' + nombre + '</td>' +
                            '</tr>'
                        );
                    }
                    $("#label-select").html(options)

                    let lon = data['longitude']
                    let lat = data['latitude']
                    centerMap(lon, lat);

                    prepare_selects_drones_sentinel()
                    prepare_selects_shape()
                })
        }

        $("#proj-select").on('change', (function () {
            let proj = $("#proj-select").val()
            if (proj !== "") {
                init(proj)
            } else {
                console.log("No esta seleccionado el proyecto")
            }
        }))


//cuando se selecciona un proyecto se envia una url para buscar todas las imagenes
//del repositorio  del album de patrones asociadas con el proyecto,
//con esta informacion se rellena la  lista de seleccion
//     function prepare_select_image_repositorio() {
//         console.log("prepare_select_image_repositorio")
//         let proj = $("#proj-select").val()
//         if (proj !== "") {
//             $.post('/get_repo_images/',
//                 {'proj_pk': proj},
//                 function (data) {
//                     let repositorio_list = data['repositorio_list']
//                     var options = '<option value="">Selecciona imagen de repositorio</option>';
//                     for (var i = 0; i < repositorio_list.length; i++) {
//                         options += '<option value=' + repositorio_list[i].toString() + '>' + repositorio_list[i].toString() + '</option>';
//                     }
//                     $("#image-select").html(options)
//                 });
//         } else {
//             let options1 = '<option value="">Selecciona imagen de repositorio</option>';
//             $("#image-select").html(options1)
//         }
//     }

//cuando se selecciona un proyecto se envia una url para buscar todas las imagenes
//de drones y de satelite  asociadas con el proyecto,
//con esta informacion se rellenan las dos listas de seleccion del menu (drones, sentinel)
        function prepare_selects_drones_sentinel() {
            let proj = $("#proj-select").val()
            if (proj !== "") {
                $.post('/get_dates/',
                    {'proj_pk': proj},
                    function (data) {
                        let proj_name = data['proj_name']
                        let date_drones_list = data['date_drones_list']
                        let date_sentinel_list = data['date_sentinel_list'];
                        let shp_list = data['shp_list'];

                        var options = '<option value="">Selecciona fecha imagen de drones</option>';
                        for (var i = 0; i < date_drones_list.length; i++) {
                            options += '<option value=' + date_drones_list[i].toString() + '>' + 'drones - ' + date_drones_list[i].toString() + '</option>';
                        }
                        $("#drones-select").html(options)

                        options = '<option value="">Selecciona fecha imagen de sentinel</option>';
                        for (var i = 0; i < date_sentinel_list.length; i++) {
                            options += '<option value=' + date_sentinel_list[i].toString() + '>' + 'sentinel - ' + date_sentinel_list[i].toString() + '</option>';
                        }
                        $("#sentinel-select").html(options)
                    });
            } else {
                let options1 = '<option value="">Selecciona fecha imagen de drones</option>';
                $("#drones-select").html(options1)
                let options2 = '<option value="">Selecciona fecha imagen de sentinel</option>';
                $("#sentinel-select").html(options2)
            }
        }

        function prepare_selects_shape() {
            let proj = $("#proj-select").val()
            if (proj !== "") {
                $.post('/get_dates/',
                    {'proj_pk': proj},
                    function (data) {
                        let date_shape_list = data['date_shape_list'];
                        options = '<option value="">Selecciona shape file</option>';
                        for (var i = 0; i < date_shape_list.length; i++) {
                            options += '<option value=' + date_shape_list[i].toString() + '>' + 'shape - ' + date_shape_list[i].toString() + '</option>';
                        }
                        $("#shape-select").html(options)
                    });
            } else {
                let options3 = '<option value="">Selecciona fecha shape files</option>';
                $("#shape-select").html(options3)
            }
        }


//esto tiene que ver con el clasificador de patrones sobre la imagen de drones
        $("#explorar-id").click(function (evt) {
            let clase_pk = $("#label-select").val();
            if (clase_pk !== "") {
                let index = indexInClasses_list(clase_pk);
                let pid = $("#proj-select").val()
                let label_name = window.legend_name[index]
                $.post('/explorer/',
                    {'pid': pid, 'image': label_name},
                    function (data) {
                        let status = data['status']
                    }
                )
            }
        })


        function loadAlbumImage(proj, image_name) {
            let geoimg = new ol.layer.GeoImage({
                name: "Repositorio",
                opacity: 1.0,
                source: new ol.source.GeoImage({
                    url: '/get_album_image/' + proj + "/" + image_name,
                    imageCenter: ol.proj.transform([lon, lat], 'EPSG:4326', 'EPSG:3857'),
                    //imageCenter: [-8900953.60, 2560325.15],
                    imageScale: [10, 10],
                    //imageCrop: [xmin, ymin, xmax, ymax],
                    //imageMask: [[273137.343,6242443.14],[273137.343,6245428.14],[276392.157,6245428.14],[276392.157,6242443.14],[273137.343,6242443.14]],
                    //imageRotate: Number($("#rotate").val() * Math.PI / 180),
                    projection: 'EPSG:3857',
                    //attributions: ["<a href='http://www.geoportail.gouv.fr/actualite/181/telechargez-les-cartes-et-photographies-aeriennes-historiques'>Photo historique &copy; IGN</a>"]
                })
            });
            return geoimg;
        }


        function show_parcels(clase_pk) {
            //Create an empty extent that we will gradually extend
            var extent = ol.extent.createEmpty();

            var lay = null
            map.getLayers().forEach(function (layer) {
                //If this is actually a group, we need to create an inner loop to go through its individual layers
                if (layer instanceof ol.layer.Group) {
                    layer.getLayers().forEach(function (groupLayer) {
                        //If this is a vector layer, add it to our extent
                        if (layer instanceof ol.layer.Vector) {
                            lay = layer
                            ol.extent.extend(extent, groupLayer.getSource().getExtent());
                        }
                    });
                } else if (layer instanceof ol.layer.Vector) {
                    lay = layer
                    ol.extent.extend(extent, layer.getSource().getExtent());
                }
            });

            //Finally fit the map's view to our combined extent
            map.getView().fit(extent, map.getSize());

            if (lay !== null) {
                var features = lay.getSource().getFeatures();
                for (let i = 0; i < features.length; ++i) {
                    let fillColor1 = 'rgb(0, 0, 0, 0.5)';
                    var newStyle = new ol.style.Style({
                        fill: new ol.style.Fill({color: fillColor1}),
                        stroke: new ol.style.Stroke({color: 'rgba(4, 4, 4, 1)', width: 1})
                    });
                    features[i].setStyle(newStyle)

                    const uso = features[i].get('Uso_de_la_');
                    let index = indexInClasses_list(clase_pk)

                    if (uso === window.legend_name[index]) {
                        // fillColor = window.legend_color[index];
                        let fillColor1 = 'rgb(255, 255, 255, 0.5)';
                        var newStyle2 = new ol.style.Style({
                            fill: new ol.style.Fill({color: fillColor1}),
                            stroke: new ol.style.Stroke({color: 'rgba(4, 4, 4, 1)', width: 1})
                        });
                        features[i].setStyle(newStyle2)
                    }
                }
            }
        }


        function createGroupMuestras() {
            function createMuestras(i) {
                window.deletedSource.push(new ol.source.Vector());
                window.addedSource.push(new ol.source.Vector());
                window.samplingSource.push(new ol.source.Vector());
                window.style_sampling.push(new ol.style.Style({
                    image: new ol.style.Circle({
                        radius: 5,
                        fill: new ol.style.Fill({
                            color: window.legend_color[i],
                        }),
                    }),
                }));
                window.drawLayer.push(new ol.layer.Vector({
                    title: window.legend_name[i],
                    visible: true,
                    source: window.samplingSource[i],
                    style: window.style_sampling[i]
                }));

                let intera = new ol.interaction.Draw({
                    source: window.samplingSource[i],
                    type: 'Point',
                    style: window.style_sampling[i]
                })

                intera.on('drawstart', function (evt) {
                    window.addedSource[i].addFeature(evt.feature)
                    window.samplingSource[i].addFeature(evt.feature)

                    let nsamples = window.samplingSource[i].getFeatures().length
                    $("#nsamples").text(nsamples.toString())
                });

                window.inter_sampling.push(intera)
            }

            window.deletedSource.length = 0;
            window.addedSource.length = 0;
            window.samplingSource.length = 0;
            window.style_sampling.length = 0;
            window.drawLayer.length = 0;
            window.inter_sampling.length = 0;

            $("#circle").css("background-color", window.legend_color[0]);
            for (let i = 0; i < window.nclasses; i++) {
                createMuestras(i)
            }
            return new ol.layer.Group({
                name: 'Muestras',
                title: 'Muestras',
                fold: 'open',
                layers: window.drawLayer
            })
        }

        function centerMap(long, lat) {
            map.getView().setCenter(ol.proj.transform([long, lat], 'EPSG:4326', 'EPSG:3857'));
            map.getView().setZoom(13);
        }

        let view = new ol.View({
            extent: projExtent,
            projection: 'EPSG:3857',
            center: ol.proj.transform([lon, lat], 'EPSG:4326', 'EPSG:3857'),
            zoom: 10,
            maxZoom: 23
        })

        let src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEAAQMAAABmvDolAAAAA1BMVEX///+nxBvIAAAAH0lEQVQYGe3BAQ0AAADCIPunfg43YAAAAAAAAAAA5wIhAAAB9aK9BAAAAABJRU5ErkJggg=="

        function createGroupBase() {
            return new ol.layer.Group({
                title: 'Mapas bases',
                fold: 'open',
                layers: [
                    new ol.layer.Tile({
                        // A layer must have a title to appear in the layerswitcher
                        title: 'OSM',
                        // Again set this layer as a base layer
                        type: 'base',
                        visible: true,
                        source: new ol.source.OSM()
                    }),
                    new ol.layer.Tile({
                        title: 'GEOLOC',
                        type: 'base',
                        visible: true,
                        source: new ol.source.XYZ({
                            url: 'http://mapas.geocuba.cu/osm_tiles/{z}/{x}/{y}.png'
                        })
                    }),
                    new ol.layer.Image({
                        title: 'Fondo blanco',
                        type: 'base',
                        visible: false,
                        imageExtent: view.getProjection().getExtent(),
                        imageLoadFunction: function (image) {
                            image.getImage().src = src;
                        },
                        projection: view.getProjection(),
                        url: ''
                    })
                ]
            })
        }

        let map = new ol.Map({
            numZoomLevels: 23,
            target: 'map',
            layers: [createGroupBase()],
            view: view
        });


// Main control bar
        let mainbar = new ol.control.Bar();
        map.addControl(mainbar);

        let layerSwitcher = new ol.control.LayerSwitcher({
            tipLabel: 'Légende', // Optional label for button
            groupSelectStyle: 'children' // Can be 'children' [default], 'group' or 'none'
        });
        map.addControl(layerSwitcher);

        let mousePositionControl = new ol.control.MousePosition({
            coordinateFormat: ol.coordinate.createStringXY(4),
            projection: 'EPSG:4326',
            // comment the following two lines to have the mouse position
            // be placed within the map.
            className: 'custom-mouse-position',
            target: document.getElementById('mouse-position'),
            undefinedHTML: '&nbsp;',
        });

        let projectionSelect = document.getElementById('projection');
        projectionSelect.addEventListener('change', function (event) {
            mousePositionControl.setProjection(event.target.value);
        });

        map.addControl(mousePositionControl);

        // when the user moves the mouse, get the name property
        // from each feature under the mouse and display it
        function onMouseMove(browserEvent) {
            let shp = $("#shape-select").val()
            if (shp !== '') {
                var coordinate = browserEvent.coordinate;
                var pixel = map.getPixelFromCoordinate(coordinate);
                var el = document.getElementById('information');
                el.innerHTML = '';
                map.forEachFeatureAtPixel(pixel, function (feature) {
                        let project = 1
                        if (project === 1) {
                            el.innerHTML += '<span>Bloque: </span>' + feature.get('BLOQUE') + '<br>';
                            el.innerHTML += '<span>Campo: </span>' + feature.get('CAMPO') + '<br>';
                        } else {
                            el.innerHTML += feature.get('Uso_de_la_') + '<br>'
                        }
                    }
                )
            }
        }

        map.on('pointermove', onMouseMove);

        function show_feature_info(fea) {
            let shp = $("#shape-select").val()
            if (shp !== '') {
                let project = 2
                if (project === 2) {
                    let ueb = fea.get('UEB');
                    let unidad = fea.get('UNIDAD');
                    let lote = fea.get('LOTE');
                    let bloque = fea.get('BLOQUE');
                    let campo = fea.get('CAMPO');
                    let i = 'UEB :' + ueb + '<br>' +
                        'UNIDAD :' + unidad + '<br>' +
                        'LOTE :' + lote + '<br>' +
                        'BLOQUE :' + bloque + '<br>' +
                        'CAMPO :' + campo + '<br>'
                    info(i)
                } else {
                    const uso = fea.get('Uso_de_la_')
                    let i = 'USO :' + uso + '<br>'
                    info(i)
                }

            }
        }

        function indexInClasses_list(pk) {
            let index = 0
            for (let i = 0; i < window.nclasses; i++) {
                if (window.legend_pk[i] == pk) {
                    index = i;
                    break;
                }
            }
            return index;
        }

        function include(arr, obj) {
            for (let i = 0; i < arr.length; i++) {
                if (arr[i] == obj) return true;
            }
            return false;
        }

        function number_sons(cod, n, aa) {
            let lab_stack_level = new Array(200);
            let cod_stack_level = new Array(200);
            let s = 0
            for (let k = 0; k < aa.categories[n + 1].classes.length; k++) {
                let temp_cod = aa.categories[n + 1].classes[k].cod;
                var pos = temp_cod.search(cod)
                if (pos == 0) {
                    cod_stack_level[s] = aa.categories[n + 1].classes[k].cod;
                    lab_stack_level[s] = aa.categories[n + 1].classes[k].label
                    s = s + 1
                }
            }
            console.log("S dentro: " + s)
            return [cod_stack_level, lab_stack_level, s];
        }

    }
});


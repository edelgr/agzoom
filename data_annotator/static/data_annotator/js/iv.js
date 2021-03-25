$(document).ready(function () {
    $("#btn-image-iv").click(function () {
        window.start_wait()
        var checked_image_list = []
        var checked_imageid_list = []
        $(".checkbox-image").each(function () {
            if ($(this).prop('checked')) {
                var image = $(this).data('image')
                var imageid = $(this).data('imageid')
                checked_image_list.push(image)
                checked_imageid_list.push(imageid)
            }
        })
        var checked_iv_list = []
        $(".checkbox-iv").each(function () {
            if ($(this).prop('checked')) {
                var iv = $(this).data('iv')
                checked_iv_list.push(iv)
            }
        })
        let proj = $("#proj-select").val()
        console.log(checked_iv_list)
        console.log(checked_imageid_list)
        $.post('/prepare_iv',
            {
                'proj_pk': proj,
                'checked_image_list': checked_image_list,
                'checked_imageid_list': checked_imageid_list,
                'checked_iv_list': checked_iv_list
            })
            .done(
                function (data) {
                    window.end_wait()
                    window.location.reload()
                })
            .fail(function (xhr, status, error) {
                    console.log('status' + status)
                    console.log('error' + error)
                }
            )
    });


    function fill_table() {
        let proj = $("#proj-select").val()
        $("#iv-table > tbody:last").children().remove()
        let linea1 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="ndvi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Diferencia Normalizada de Vegetación (NDVI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea1);
         let linea2 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="evi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Vegetación Mejorado (EVI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea2);
        let linea3 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="msi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Estrés Hídrico (MSI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea3);
        let linea4 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="ndmi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Diferencia Normalizada de Humedad (NDMI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea4);
        let linea5 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="ndwi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Diferencial de Agua Normalizado (NDWI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea5);
        let linea6 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="lai" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Area Foliar (LAI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea6);
        let linea7 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="gci" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Clorofila (GCI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea7);
        let linea8 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="sipi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Pigmentación Insensible a la Estructura (SIPI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea8);
        let linea9 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="yvimss" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Amarillez de la Vegetación (YVIMSS)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea9);
        let linea10 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="gndvi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Diferencia Normalizada de Verde (GNDVI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea10);
        let linea11 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="savi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Vegetación Ajustado al Suelo (SAVI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea11);
        let linea12 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="gli" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Hojas Verdes (GLI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea12);
        let linea13 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="tci" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice Triangular de Clorofila (TCI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea13);
        let linea14 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="bsi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Suelo Desnudo (BSI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea14);
        let linea15 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="nbri" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Calcinación Normalizado (NBRI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea15);

        let linea16 = '<tr>   ' +
            '<td class="checked-button"> ' +
            '<div class="form-check"> ' +
            '<label class="form-check-label"> ' +
            '<input class="form-check-input position-static checkbox-iv" data-iv="endvi" type="checkbox"' +
            ' value="option1" aria-label="...">' +
            '</label>' +
            '</div>' +
            '</td> ' +
            '<td>Indice de Vegetación de Diferencia Normalizado Mejorado (ENDVI)</td>' +
            '</tr>'
        $('#iv-table > tbody:last-child').append(linea16);

        if (proj !== "") {
            $.post('/get_all_image/',
                {'proj_pk': proj, 'op': 'iv'},
                function (data) {
                    let pk_list = data['pk_list']
                    let date_list = data['date_list'];
                    let name_list = data['name_list'];
                    let plat_list = data['plat_list'];
                    $("#image-table > tbody:last").children().remove()
                    for (let i = 0; i < pk_list.length; i++) {
                        let p
                        if (plat_list[i] === '1') {
                            p = 'sentinel'
                        }
                        if (plat_list[i] === '2') {
                            p = 'drones'
                        }

                        let linea = '<tr>   ' +
                            '<td class="checked-button"> ' +
                            '<div class="form-check"> ' +
                            '<label class="form-check-label"> ' +
                            '<input class="form-check-input position-static checkbox-image" data-imageid="' + pk_list[i].toString() + '" data-image="' + name_list[i].toString()  + '" type="checkbox"' +
                            ' value="option1" aria-label="...">' +
                            '</label>' +
                            '</div>' +
                            '</td> ' +
                            '<td class="date-image">' + date_list[i] + '</td>' +
                            '<td class="name-image">' + name_list[i] + '</td>' +
                            '<td class="platform">' + p + '</td>' +
                            '</tr>'
                        console.log(linea)
                        $('#image-table > tbody:last-child').append(linea);
                    }
                })
        }
    }

    fill_table()

    $("#proj-select").on('change', (function () {
        fill_table()
    }))
})
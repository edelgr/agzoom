$(document).ready(function () {
    $("#btn-image-tiles").click(function () {
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

        console.log(checked_image_list)

        let proj = $("#proj-select").val()
        $.post('/prepare_tiles',
            {
                'proj_pk': proj,
                'checked_image_list': checked_image_list,
                'checked_imageid_list': checked_imageid_list
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
        if (proj !== "") {
            $.post('/get_all_image/',
               {'proj_pk': proj, 'op': 'create_mbtiles'},
                function (data) {
                    let pk_list = data['pk_list']
                    let date_list = data['date_list'];
                    let name_list = data['name_list'];
                    let plat_list = data['plat_list'];
                    let img_tif_list = data['img_tif_list'];
                    $("#image-table > tbody:last").children().remove()
                    for (let j = 0; j < img_tif_list.length; j++) {
                        let p
                        if (plat_list[j] === '1') {
                            p = 'Sentinel'
                        }
                        if (plat_list[j] === '2') {
                            p = 'Drones'
                        }
                        let linea = '<tr>   ' +
                            '<td> ' + '</td> ' +
                            '<td class="date-image">' + date_list[j] + '</td>' +
                            '<td class="name-image">' + name_list[j] + '</td>' +
                            '<td class="platform">' + p + '</td>' +
                            '</tr>'
                        $('#image-table > tbody:last-child').append(linea);
                        for (let k = 0; k < img_tif_list[j].length; k++) {
                            let linea = '<tr>   ' +
                                '<td class="checked-button"> ' +
                                '<div class="form-check"> ' +
                                '<label class="form-check-label"> ' +
                                '<input class="form-check-input position-static checkbox-image" data-imageid=' + pk_list[j].toString() + ' data-image="' + img_tif_list[j][k].toString() + '" type="checkbox"' +
                                ' value="option1" aria-label="...">' +
                                '</label>' +
                                '</div>' +
                                '</td> ' +
                                '<td class="date-image">' + img_tif_list[j][k] + '</td>' +
                                '<td></td>' +
                                '</tr>'
                            $('#image-table > tbody:last-child').append(linea);
                        }
                    }
                }
            )
        }
    }

    fill_table()

    $("#proj-select").on('change', (function () {
        fill_table()
    }))
})
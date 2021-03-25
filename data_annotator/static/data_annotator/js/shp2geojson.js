$(document).ready(function () {
    $("#btn-shp2geojson").click(function () {
        window.start_wait()
        var checked_shape_id_list = []
        $(".checkbox-shape").each(function () {
            if ($(this).prop('checked')) {
                var shape_id = $(this).data('shapeid')
                checked_shape_id_list.push(shape_id)
            }
        })
        let proj = $("#proj-select").val()
        $.post('/convert_shp2geojson',
            {
                'proj_pk': proj,
                'checked_shape_id_list': checked_shape_id_list
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


    function fill_table_shape() {
        let proj = $("#proj-select").val()
        if (proj !== "") {
            $.post('/get_all_image/',
                {'proj_pk': proj, 'op': 'shp2geojson'},
                function (data) {
                    let pk_list = data['pk_list']
                    let date_list = data['date_list'];
                    let desc_list = data['desc_list'];
                    $("#shape-table > tbody:last").children().remove()
                    for (let i = 0; i < pk_list.length; i++) {
                        let linea = '<tr>   ' +
                            '<td class="checked-button"> ' +
                            '<div class="form-check"> ' +
                            '<label class="form-check-label"> ' +
                            '<input class="form-check-input position-static checkbox-shape" data-shapeid="' + pk_list[i].toString() + '" type="checkbox"' +
                            ' value="option1" aria-label="...">' +
                            '</label>' +
                            '</div>' +
                            '</td> ' + '<td class="date-shape">' + date_list[i] + '</td>' +
                            '<td class="description">' + desc_list[i] + '</td>' +
                            '</tr>'
                        $('#shape-table > tbody:last-child').append(linea);
                    }
                });
        }
    }

    fill_table_shape()

    $("#proj-select").on('change', (function () {
        fill_table_shape()
    }))
})
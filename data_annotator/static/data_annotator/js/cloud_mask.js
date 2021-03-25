$(document).ready(function () {
    $("#btn-image-cloud").click(function () {
        window.start_wait()
        var checked_image_id_list = []
        $(".checkbox-image").each(function () {
            if ($(this).prop('checked')) {
                var image_id = $(this).data('imageid')
                checked_image_id_list.push(image_id)
            }
        })
        let proj = $("#proj-select").val()
        $.post('/prepare_cloud_mask',
            {
                'proj_pk': proj,
                'checked_image_id_list': checked_image_id_list
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
                {'proj_pk': proj, 'op': 'cloud_mask'},
                function (data) {
                    let pk_list = data['pk_list']
                    let date_list = data['date_list'];
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
                            '<input class="form-check-input position-static checkbox-image" data-imageid="' + pk_list[i].toString() + '" type="checkbox"' +
                            ' value="option1" aria-label="...">' +
                            '</label>' +
                            '</div>' +
                            '</td> ' +
                            '<td class="date-image">' + date_list[i] + '</td>' +
                            '<td class="platform">' + p + '</td>' +
                            '</tr>'
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
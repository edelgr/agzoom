$(document).ready(function () {
    function fill_table_image() {
        let proj = $("#proj-select").val()
        if (proj !== "") {
            $.post('/get_all_image/',
                {'proj_pk': proj, 'op': 'data_explorer_img'},
                function (data) {
                    let pk_list = data['pk_list']
                    let date_list = data['date_list'];
                    let name_list = data['name_list'];
                    let plat_list = data['plat_list'];
                    $("#image-table > tbody:last").children().remove()
                    for (let i = 0; i < pk_list.length; i++) {
                        let p = 'Drones'
                        if (plat_list[i] === '1') {
                            p = 'Sentinel'
                        }
                        $('#image-table > tbody:last-child').append(
                            '<tr>   ' +
                            '<div class="form-check"> ' +
                            '<label class="form-check-label"> ' +
                            '<input class="form-check-input position-static checkbox-image" data-imageid="' + pk_list[i].toString() + '" type="checkbox"' +
                            ' value="option1" aria-label="...">' +
                            '</label>' +
                            '</div>' +
                            '</td> ' +
                            '<td class="date-image">' + date_list[i] + '</td>' +
                            '<td class="name-image">' + name_list[i] + '</td>' +
                            '<td class="platform">' + p + '</td>' +
                            '<td class="actions"> B </td>' +
                            '</tr>'
                        );
                    }
                });
        }
    }

    fill_table_image()

    $("#proj-select").on('change', (function () {
        fill_table_image()
    }))
})
$(document).ready(function () {
    function fill_table_shape() {
        let proj = $("#proj-select").val()
        if (proj !== "") {
            $.post('/get_all_image/',
               {'proj_pk': proj, 'op': 'data_explorer_shp'},
                function (data) {
                    let pk_list = data['pk_list']
                    let date_list = data['date_list'];
                    let desc_list = data['desc_list'];
                    $("#shape-table > tbody:last").children().remove()
                    for (let i = 0; i < pk_list.length; i++) {
                        $('#shape-table > tbody:last-child').append(
                            '<tr>   ' +
                            '<div class="form-check"> ' +
                            '<label class="form-check-label"> ' +
                            '<input class="form-check-input position-static checkbox-shape" data-shapeid="' + pk_list[i].toString() + '" type="checkbox"' +
                            ' value="option1" aria-label="...">' +
                            '</label>' +
                            '</div>' +
                            '</td> ' +
                            '<td class="date-shape">' + date_list[i] + '</td>' +
                            '<td class="description">' + desc_list[i] + '</td>' +
                            '<td class="actions"> B </td>' +
                            '</tr>'
                        );
                    }
                });
        }
    }

    fill_table_shape()

    $("#proj-select").on('change', (function () {
        fill_table_shape()
    }))
})
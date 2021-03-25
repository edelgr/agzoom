$(document).ready(function () {
    $("#btn-import").on('change', function (e) {
        window.start_wait()
        var filename = this.files[0];
        if (!filename) {
            return;
        }
        var reader = new FileReader();

        reader.onload = function (e) {
            var contents = e.target.result;
            var input = $.csv.toArrays(contents);

            var row_list = []

            input.forEach(function (l) {
                    let row = {
                        'cpa': l[0],
                        'fecha': l[1],
                        'bloque': l[2],
                        'campo': l[3],
                        'variedad': l[4],
                        'cepa': l[5],
                        'edad': l[6],
                        'pol_cana': l[7],
                        'pol_jugo': l[8],
                        'pureza': l[9],
                        'index': l[10],
                        'brix': l[11],
                        'brix_inf': l[12],
                        'brix_sup': l[13],
                        'im': l[14],
                        'fibra': l[15],
                        'rendimiento': l[16],
                        'ha': l[17],
                        't_ha': l[18],
                        't': l[19]
                    }
                    console.log(row)
                    row_list.push(row)
                }
            )
            let proj = $("#proj-select").val()
            console.log(row_list)
            let rows_json = JSON.stringify(row_list)
            console.log(rows_json)
            $.post('/prepare_prog_corte/',
                {
                    'proj_pk': proj,
                    'rows_list': rows_json
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
        }
        reader.readAsText(filename);
    })
})
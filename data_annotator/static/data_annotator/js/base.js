function init(lon, lat, ap) {
    if (ap === 0) {
        $("#proj-select").val("")
    }
    else {
        $("#proj-select").val(ap)
    }

    $("#proj-select").on('change', (function () {
        let proj = $("#proj-select").val()
        if (proj !== "") {
            $.post('/active_project/',
                {'proj_pk': proj},
                function (data) {

                })
        } else {
            console.log("No esta seleccionado el proyecto")
        }
    }))

    window.start_wait = function () {
        $('#loading-block').show()
        $('#loading-block-div').show()

    }

    window.end_wait = function () {
        $('#loading-block').hide()
        $('#loading-block-div').hide()

    }
}
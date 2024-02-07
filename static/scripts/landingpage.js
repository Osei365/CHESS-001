

$('document').ready(() => {
    $('#blitz1').on('change', () => {
        console.log('changed');
        if ($('#blitz1').is(':checked')) {
            $('#classical1').prop('checked', false);
        }
    });
    $('#classical1').change(() => {
        console.log('changed');
        if ($('#classical1').is(':checked')) {
            console.log('changed');
            $('#blitz1').prop('checked', false);
        }
    });

    $('#blitz2').on('change', () => {
        console.log('changed');
        if ($('#blitz2').is(':checked')) {
            $('#classical2').prop('checked', false);
        }
    });
    $('#classical2').change(() => {
        console.log('changed');
        if ($('#classical2').is(':checked')) {
            console.log('changed');
            $('#blitz2').prop('checked', false);
        }
    });
})




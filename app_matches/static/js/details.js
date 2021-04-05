$(document).ready(function () {
    $('.mid').on('click', function () {

        if ($(this).find('.switch-input').prop('checked') == true) {
            $(this).find('.switch-input').prop('checked', false);
            var $text = $(this).find('.switch-label').data('off');
            $(this).find("input[name='team-name']").val($text);
        } else {
            $(this).find('.switch-input').prop('checked', true);
            var $text = $(this).find('.switch-label').data('on');
            $(this).find("input[name='team-name']").val($text);
        }
    });

    $('.switch-input').each(function () {
        $(this).closest('.mid').find('div').text('Select Team');
        if ($(this).prop('checked') == true) {
            var $text = $(this).parent().find('.switch-label').data('on');
            $(this).find("input[name='team-name']").val($text);
        } else {
            var $text = $(this).parent().find('.switch-label').data('off');
            $(this).find("input[name='team-name']").val($text);
        }
    });


});
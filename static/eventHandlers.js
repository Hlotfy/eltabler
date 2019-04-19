// JavaScript File to add event handlers


$("#btn-submit").on("click", function (event) {
    if(progressive_enhancement_on) {
        event.preventDefault();  // don't do the normal form submission
        var num = $("#form-num").val();
        sendNum(num);
    }
});

$("#collatzNumbers").on("click","[data-num]",function(event) {
        var num = $(this).attr("data-num");
        sendNum(num);
        });
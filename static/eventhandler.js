
/* global $ */

$("#clearCart").on("click", function(event) {
    $.post(URL,{'cart':0},function() { 
        
    });       
    })
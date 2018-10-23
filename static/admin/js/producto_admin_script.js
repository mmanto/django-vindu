if (!$) {
    $ = django.jQuery;
};

function json_to_select(url) {
/*
 Fill a select input field with data from a getJSON call
 Esta funcion sirve para cambiar las opciones en Combinacion de Productos
*/
    $.getJSON(url, function(data) {
            var opt=$('[id^="id_rel_producto_original"]'); 
            var old_val=opt.val();

            /*console.log('opt: ', opt );
            console.log('opt closest select: ', opt.closest('select').first().val());*/
            valor_combina_con = opt.closest('select').first().val(); 

            if (!valor_combina_con) {
                opt.html('');
                opt.append($('<option/>').val("").attr('selected','').text('---------'));
                $.each(data, function () {
                    opt.append($('<option/>').val(this.id).text(this.nombre_producto));
                });
                opt.change();
            };




            /*
            alert(' opt value selected: ', opt.closest('select').text());

            opt.html('');
            opt.append($('<option/>').val("").attr('selected','').text('---------'));
            $.each(data, function () {
                opt.append($('<option/>').val(this.id).text(this.nombre_producto));
            });
            opt.change();
            */
            /* opt.val(old_val); */

    })
};

function json_to_select_categorias(url) {
    /*
     Fill a select input field with data from a getJSON call
     Esta funcion sirve para cambiar las opciones en Otros Colores de Productos
    */
        $.getJSON(url, function(data) {
                var opt=$('[id^="id_color_producto_original"]'); 
                var old_val=opt.val();
                opt.html('');
                opt.append($('<option/>').val("").attr('selected','').text('---------'));
                $.each(data, function () {
                    opt.append($('<option/>').val(this.id).text(this.nombre_producto));
                });
                /*opt.val(old_val);*/
                opt.change();
    
        })
    };

    $(document).ready(function () {
        /*
        $(function(){
            $('#id_marca').change(function(){
            json_to_select('/get-admin-productos-by-marca_id/' + $(this).val() + '/');
            }).change()
        });*/

        $(function(){
            $('#id_categoria').change(function(){
            var id_marca = $('#id_marca').val();
            json_to_select_categorias('/get-admin-productos-by-marca-categoria_id/' + id_marca + '/' + $('#id_categoria').val() + '/');
            json_to_select('/get-admin-comb-productos-by-marca-categoria_id/' + id_marca + '/' + $('#id_categoria').val() + '/');
            })
        });

        /* Manejo de opciones de Combinación de Productos e imágenes asociada */   
        $(function(){
            $('[id^="id_rel_producto_original"]').change(function(){
                /* acá se cambia la imagen del producto combinado mostrada */
                var this_element = $(this);
                var id_producto = $(this).find(":selected").val();

                if (id_producto) {
                    var environ = window.location.host;
                    var protocol = window.location.protocol;
                    var url = protocol + '//' + environ + '/get-imagen-ppal-byProductoId/' + id_producto ;
                    $.ajax({
                        type: "GET",
                        url: url,
                        dataType: "json"
                    }).done(function (res) {
                        var img = '<img src="' + res.foto_principal + '" width="100px"/>';
                        var p = this_element.closest('td').next().find("p").first().html(img);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        console.log("AJAX call failed: " + textStatus + ", " + errorThrown);
                    });
                };
            }); 
        });


        /* Manejo de opciones de Otros Colores de Productos e imágenes asociada */   
        $(function(){
            $('[id^="id_color_producto_original"]').change(function(){
                /* acá se cambia la imagen mostrada del producto en otro color  */
                var this_element = $(this);
                var id_producto = $(this).find(":selected").val();

                if (id_producto) {
                    var environ = window.location.host;
                    var protocol = window.location.protocol;
                    var url = protocol + '//' + environ + '/get-imagen-ppal-byProductoId/' + id_producto;
                    $.ajax({
                        type: "GET",
                        url: url,
                        dataType: "json"
                    }).done(function (res) {
                        img = '<img src="' + res.foto_principal + '" width="100px"/>';
                        p = this_element.closest('td').next().find("p").first().html(img);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        console.log("AJAX call failed: " + textStatus + ", " + errorThrown);
                    });
                }; 
            }); 
        });

    });

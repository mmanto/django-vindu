function talle_stock() {
  talle_id = localStorage.getItem('id')
  shop_sku = localStorage.getItem('shop_sku')
  stock = localStorage.getItem('stock')
  if (shop_sku != '0') {
    $('#shop_sku').val(shop_sku);
  }
  else {
    $('#shop_sku').val(' ');
  }
  $('#stock').val(stock);
}

$("#submit").click(function(){
  shop_sku = $('#shop_sku').val();
  stock = $('#stock').val();
  token = document.getElementsByName("csrfmiddlewaretoken")[0].value
  $.ajax({
  type: 'POST',
  url: '/modificar-talle-producto/'+talle_id+'/',
  data: {
    csrfmiddlewaretoken: token,
    talle_id: talle_id,
    stock: stock,
    shop_sku: shop_sku,
  },
  success: function(data){
    if (data.message == 'ok'){
      $('#modificar-stock-'+talle_id+'').text(stock)
      $('#talle_modal').modal('toggle');
      $('.modificar_stock_'+talle_id+'').attr('onclick','modalTalle("'+talle_id+'", "'+shop_sku+'", "'+stock+'")');
    }
    else {
        alert(data.message)
    }
  },
  error: {}
  });
});

function modalTalle(id, shop_sku, stock){
  event.preventDefault();
  $('#talle_modal').modal('toggle');
  localStorage.setItem('id', id);
  localStorage.setItem('stock', stock);
  localStorage.setItem('shop_sku', shop_sku);
  talle_stock();
};

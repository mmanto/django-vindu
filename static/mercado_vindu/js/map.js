map = new GMaps({
  div: '#local_map',
});

$(function() {
  if ($("input[name=direccion]").val()) {
    GMaps.geocode({
      address: $("input[name=direccion]").val(),
      callback: function(results, status) {
        if (status == 'OK') {
          var latlng = results[0].geometry.location;
          map.setCenter(latlng.lat(), latlng.lng());
          map.removeMarkers()
          map.addMarker({
            lat: latlng.lat(),
            lng: latlng.lng()
          });
        }
      }
    });
  }
  $("input[name=direccion]").focusout(function(){
    GMaps.geocode({
      address: $("input[name=direccion]").val(),
      callback: function(results, status) {
        if (status == 'OK') {
          var latlng = results[0].geometry.location;
          map.setCenter(latlng.lat(), latlng.lng());
          map.removeMarkers()
          map.addMarker({
            lat: latlng.lat(),
            lng: latlng.lng()
          });
        }
      }
    });
  });
});

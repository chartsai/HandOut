function updateLatLng(lat, lng) {
  // updateLatLng
  document.getElementById('lat').value=lat;
  document.getElementById('lng').value=lng;

  console.debug(lat + "," + lng);
}

var map;
function initMap() {

  var current_location;
  getLocation(function(position) {
    var lat = position.coords.latitude;
    var lng = position.coords.longitude;
    current_location = new google.maps.LatLng(lat, lng);
    updateLatLng(lat, lng);

    map = new google.maps.Map(document.getElementById('map'), {
      center: current_location,
      zoom: 16
    });

    var marker = new google.maps.Marker({
      position: current_location,
      map: map,
      draggable: true,
    });
    marker.addListener('dragend', toggleDragEnd);
    google.maps.event.addListener(map, 'click', clickMap);

    function clickMap(event) {
      var latlng = event.latLng;
      marker.setPosition(latlng);
      var lat = latlng.lat();
      var lng = latlng.lng();

      bounceMarker(marker);

      updateLatLng(lat, lng);
    }

    function toggleDragEnd() {
      var latlng = marker.getPosition();
      var lat = latlng.lat();
      var lng = latlng.lng();

      bounceMarker(marker);

      updateLatLng(lat, lng);
    }

    function bounceMarker(marker) {
      marker.setAnimation(google.maps.Animation.BOUNCE);
      setTimeout(function(){ marker.setAnimation(null); }, 500);
    }
  });
}

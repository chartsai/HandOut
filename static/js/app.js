// MAP_KEY='AIzaSyAAJWANy1vD0TcPFB0X5bX3Vi4Qyi4bYPw';

// callback should be:
// callback(position) {
//   position.coords.latitude
//   position.coords.longitude
// }
function getLocation(callback) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(callback);
  } else {
    alert("Cannot get location.");
  }
}

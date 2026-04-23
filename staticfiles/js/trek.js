// --- Map Initialization ---
const map = new maplibregl.Map({
  container:'map',
  style:'https://tiles.openfreemap.org/styles/liberty',
  center:[84.124,28.3949],
  zoom:6.5,
  pitch:45,
  bearing:-17.6
});
map.addControl(new maplibregl.NavigationControl(), 'top-right');

let routeLayerAdded=false, chartInstance=null, currentRoute=null, qrCanvas=null;

// --- FAB ---
function toggleFab(){
  const fabActions = document.getElementById("fabActions");
  fabActions.style.display = fabActions.style.display==="flex"?"none":"flex";
}

// --- Waypoints ---
function addWaypoint(value=""){
  const div = document.createElement("div");
  div.innerHTML = `<input type="text" class="waypoint" placeholder="Waypoint (e.g. Ghandruk)" value="${value}" />`;
  document.getElementById("waypoints").appendChild(div);
}

// --- Geocoding ---
async function geocode(place){
  const url=`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(place)}+Nepal`;
  const res = await fetch(url,{headers:{'Accept-Language':'en'}});
  const data = await res.json();
  if(data && data.length>0) return [parseFloat(data[0].lon),parseFloat(data[0].lat)];
  return null;
}

// --- Route Calculation ---
async function getRoute(){
  const inputs = Array.from(document.querySelectorAll(".waypoint"));
  const places = inputs.map(i=>i.value).filter(v=>v.trim()!=="");
  if(places.length<2){ alert("Enter Start & Destination."); return; }

  const coords=[];
  for(const place of places){
    const c = await geocode(place);
    if(!c){ alert(`Could not find: ${place}`); return; }
    coords.push(c);
    new maplibregl.Marker({color:"blue"}).setLngLat(c).setPopup(new maplibregl.Popup().setHTML(`<b>${place}</b>`)).addTo(map);
  }

  const coordStr=coords.map(c=>c.join(",")).join(";");
  const routeUrl=`https://router.project-osrm.org/route/v1/foot/${coordStr}?overview=full&geometries=geojson`;
  const routeRes=await fetch(routeUrl);
  const routeData=await routeRes.json();

  if(routeData.routes && routeData.routes.length>0){
    const route=routeData.routes[0].geometry;
    const distance=routeData.routes[0].distance;
    currentRoute=route;

    if(routeLayerAdded){ map.removeLayer('route-line'); map.removeSource('route'); }
    map.addSource('route',{type:'geojson', data:{type:'Feature',geometry:route}});
    map.addLayer({id:'route-line', type:'line', source:'route', paint:{'line-color':'#ff6600','line-width':4}});
    routeLayerAdded=true;

    const bounds = new maplibregl.LngLatBounds();
    route.coordinates.forEach(c=>bounds.extend(c));
    map.fitBounds(bounds,{padding:50});

    getElevationProfile(route.coordinates, distance);
  } else alert("No walking route found.");
}

// --- Elevation Profile ---
async function getElevationProfile(coords,distance){
  try{
    const step = Math.ceil(coords.length/200);
    const sampled = coords.filter((_,i)=>i%step===0);
    const locations = sampled.map(c => `${c[1]},${c[0]}`).join("|");
    const url = `https://api.open-elevation.com/api/v1/lookup?locations=${locations}`;
    const res = await fetch(url);
    const data = await res.json();

    if(data.results){
      const elevations = data.results.map(r=>typeof r.elevation==='number'?r.elevation:0);
      const labels = elevations.map((_,i)=>i);

      let ascent=0, descent=0;
      for(let i=1;i<elevations.length;i++){ const diff=elevations[i]-elevations[i-1]; if(diff>0) ascent+=diff; else descent+=Math.abs(diff); }

      const distKm = distance/1000;
      const flatHours = distKm/5, climbHours = ascent/600, estHours = flatHours+climbHours;

      document.getElementById('ascent').innerText = `Ascent: ${Math.round(ascent)} m`;
      document.getElementById('descent').innerText = `Descent: ${Math.round(descent)} m`;
      document.getElementById('distance').innerText = `Distance: ${distKm.toFixed(1)} km`;
      document.getElementById('time').innerText = `Time: ${estHours.toFixed(1)} h`;

      drawElevationChart(labels, elevations);
    }
  } catch(err){ console.error("Elevation fetch error:", err); }
}

function drawElevationChart(labels,elevations){
  const ctx=document.getElementById('elevationChart').getContext('2d');
  if(chartInstance) chartInstance.destroy();
  chartInstance=new Chart(ctx,{type:'line',data:{labels, datasets:[{label:'Elevation (m)', data:elevations, borderColor:'#ff6600', backgroundColor:'rgba(255,102,0,0.3)', fill:true, pointRadius:0}]}, options:{responsive:true, plugins:{legend:{display:false}}, scales:{x:{display:false}, y:{title:{display:true,text:'Meters'}}}}});
}

// --- GPX/KML ---
function downloadGPX(){ 
  if(!currentRoute){ alert("No route!"); return; } 
  const coords=currentRoute.coordinates; 
  let gpx=`<?xml version="1.0" encoding="UTF-8"?><gpx version="1.1" creator="TrekNepal"><trk><name>Trek Route</name><trkseg>`; 
  coords.forEach(c=>gpx+=`<trkpt lon="${c[0]}" lat="${c[1]}"></trkpt>\n`); 
  gpx+=`</trkseg></trk></gpx>`; 
  const blob=new Blob([gpx],{type:"application/gpx+xml"}); 
  const link=document.createElement("a"); 
  link.href=URL.createObjectURL(blob); 
  link.download="trek-route.gpx"; 
  link.click(); 
}

function downloadKML(){ 
  if(!currentRoute){ alert("No route!"); return; } 
  const coords=currentRoute.coordinates; 
  let kml=`<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Trek Route</name><Placemark><LineString><coordinates>`; 
  coords.forEach(c=>kml+=`${c[0]},${c[1]},0 `); 
  kml+=`</coordinates></LineString></Placemark></Document></kml>`; 
  const blob=new Blob([kml],{type:"application/vnd.google-earth.kml+xml"}); 
  const link=document.createElement("a"); 
  link.href=URL.createObjectURL(blob); 
  link.download="trek-route.kml"; 
  link.click(); 
}

// --- QR Sharing ---
function shareTrek(){
  const inputs = Array.from(document.querySelectorAll(".waypoint"));
  const places = inputs.map(i=>i.value).filter(v=>v.trim()!=="");
  if(places.length < 2) { alert("Add start & destination"); return; }

  const id = 'trek_' + Date.now();
  localStorage.setItem(id, JSON.stringify(places));

  const shareUrl = `${window.location.origin}${window.location.pathname}?id=${id}`;
  navigator.clipboard.writeText(shareUrl).then(()=>alert("Short trek link copied!"));

  document.getElementById("qrModal").style.display="flex";
  document.getElementById("qrcode").innerHTML="";
  QRCode.toCanvas(shareUrl, { width: 220 }, (err, canvas) => {
    if(!err){ qrCanvas = canvas; document.getElementById("qrcode").appendChild(canvas); }
  });
}

function downloadQR(){ if(!qrCanvas) return; const link=document.createElement("a"); link.download="trek-qr.png"; link.href=qrCanvas.toDataURL("image/png"); link.click(); }
function closeQR(){ document.getElementById("qrModal").style.display="none"; }

// --- Load route from localStorage ---
window.onload = ()=>{
  const params = new URLSearchParams(window.location.search);
  if(params.has("id")){
    const id = params.get("id");
    const stored = localStorage.getItem(id);
    if(stored){
      const places = JSON.parse(stored);
      const inputs = document.querySelectorAll(".waypoint");
      inputs[0].value = places[0];
      inputs[inputs.length-1].value = places[places.length-1];
      for(let i=1;i<places.length-1;i++) addWaypoint(places[i]);
      getRoute();
    }
  }
};

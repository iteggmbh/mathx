import * as THREE from 'three';

import { TrackballControls } from 'three/addons/controls/TrackballControls.js';
import { parseQuery } from './lib/helpers.mjs';
import * as widgets from './lib/widgets.mjs';
import * as geomlib from './lib/geomlib.mjs';
import * as ecc from './lib/ecc.mjs';

console.log("ECC visualization is starting up...");

var helpButton = new widgets.Button({domNode:"helpButton"});
var helpCloseButton = new widgets.Button({domNode:"helpCloseButton"});
var subTitle = document.getElementById("subTitle");
var helpOver = document.getElementById("helpOver");
var helpOverInner = document.getElementById("helpOverInner");

var helpLoaded = false;

widgets.addAriaClickHandler(helpButton,function(){
  helpOver.classList.remove("mathInvisible");
  helpButton.disabled = true;
  if (!helpLoaded) {
	var url = "templates/ecc-help.html";
	fetch(url).
      then(resp => resp.text()).
	  then(res => helpOverInner.innerHTML = res).
      catch(
        function(err) {
          console.log(err);
          helpOverInner.innerHTML = "Loading of ["+url+"] failed.";
        }
      );
  }
});

widgets.addAriaClickHandler(helpCloseButton,function(){
  helpOver.classList.add("mathInvisible");
  helpButton.disabled = false;
});

var clock = new THREE.Clock();
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 50 );
camera.position.z = 5;

var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setPixelRatio( window.devicePixelRatio );
document.body.appendChild( renderer.domElement );

var material = new THREE.MeshLambertMaterial( { color: 0x00ffff, emissive: 0x00fffff,
                                                side: THREE.FrontSide, depthTest: true, depthWrite: true, wireframe: false,
                                                transparent: true, opacity: 0.7} );
material.color.convertSRGBToLinear();

var material2 = new THREE.MeshLambertMaterial( { color: 0x00ffff, emissive: 0x00fffff,
                                                 side: THREE.BackSide, depthTest: true, depthWrite: true, wireframe: false,
                                                 transparent: true, opacity: 0.7} );
material2.color.convertSRGBToLinear();

// line material.
var material3 = new THREE.LineBasicMaterial({
  color: 0xff0000, linewidth:3
});

// marker material.
var material4 = new THREE.PointsMaterial({
  color: 0x00ff00, size:5, sizeAttenuation: false
});

// greater circle material.
var material5 = new THREE.LineBasicMaterial({
  color: 0x00cc00, linewidth:2
});

// half-plane material
var material6 = new THREE.MeshLambertMaterial( { color: 0x00ff00, emissive: 0x00ff00,
			                                     side: THREE.DoubleSide, depthTest: true, depthWrite: true, wireframe: false,
			                                     transparent: true, opacity: 0.7} );

var geom2 = new geomlib.buildSemiSphere(1.0);
var mesh = new THREE.Mesh( geom2, material );


scene.add( mesh );

var circleGeometry = new THREE.CircleGeometry( 1, 160);
var circle = new THREE.Mesh( circleGeometry, material2 );
scene.add( circle );

var planeBdry = 5;
var planeGeometry = new THREE.PlaneGeometry(planeBdry*2,planeBdry*2);
var planeMaterial = new THREE.MeshLambertMaterial( { color: 0xffffff, emissive: 0xffffff,
			                                         side: THREE.DoubleSide, depthTest: true, depthWrite: true, wireframe: false,
			                                         transparent: true, opacity: 0.4} );

var plane = new THREE.Mesh( planeGeometry, planeMaterial );
plane.translateZ(1.0);

scene.add(geomlib.buildAxes(1.5));

var pointLight = new THREE.PointLight(0xffffff);
pointLight.position.set( 50, 50, 100 );
camera.add( pointLight );

var ambientLight = new THREE.AmbientLight(0x444444);
camera.add( ambientLight );

//var directionalLight = new THREE.DirectionalLight( 0xffffff, 1.0 );
//directionalLight.position.set( 10, 10, 0 );

//camera.add( directionalLight );
scene.add(camera);

var cameraControls = new TrackballControls(camera, renderer.domElement);
cameraControls.target.set(0, 0, 0);

function animate() {

  var delta = clock.getDelta();

  requestAnimationFrame(animate);

  cameraControls.update(delta);

  renderer.render(scene, camera);
}

function onWindowResize(){

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize( window.innerWidth, window.innerHeight );
  renderer.setPixelRatio( window.devicePixelRatio );
}

window.addEventListener( 'resize', onWindowResize, false );

var lines = null;
var markers = null;
var firstPoint = null;
var ec = null;
var planeShown = false;

function drawCurve() {
  var a = -1;
  var b = 1;
  var d = null;
  var p = false;

  if (location.hash) {

    var qo = parseQuery(location.hash.substring(1));

    qo.a != null && !isNaN(qo.a = parseFloat(qo.a)) && (a=qo.a);
    qo.b != null && !isNaN(qo.b = parseFloat(qo.b)) && (b=qo.b);
    qo.d != null && !isNaN(qo.d = parseFloat(qo.d)) && (d=qo.d);
    qo.p != null && ("true" == qo.p || "1" == qo.p) && (p = true);
  }

  if (p != planeShown) {
    if (p) {
      scene.add(plane);
    }
    else {
      scene.remove(plane);
    }
    planeShown = p;
  }

  if (lines) {
    THREE.Scene.prototype.remove.apply(scene,lines);
  }
  lines = [];

  if (markers) {
    THREE.Scene.prototype.remove.apply(scene,markers);
    markers = null;
    firstPoint = null;
  }


  if (d == null) {
    console.log("Drawing Weierstrass curve with a=",a,",b=",b);
    ec = new ecc.WeierstrassCurve(a,b);
  }
  else {
    console.log("Drawing Edwards curve with d=",d);
    ec = new ecc.EdwardsCurve(d);
  }
  subTitle.innerHTML = ec.toHtml();

  var lgeoms = ec.makeGeometries(null);

  for (var i=0;i<lgeoms.length;++i) {
    var line = new THREE.Line(lgeoms[i], material3 );
    scene.add(line);
    lines.push(line);
  }

  if (planeShown) {
    lgeoms = ec.makeGeometries(planeBdry);

    for (var i=0;i<lgeoms.length;++i) {
      var line = new THREE.Line(lgeoms[i], material3 );
      scene.add(line);
      lines.push(line);
    }
  }
}
window.addEventListener("hashchange",drawCurve, false);
drawCurve();

animate();

var modifier = navigator.userAgent.indexOf('Mac OS X') >= 0 ? "metaKey" : "ctrlKey";
var raycaster = new THREE.Raycaster();

function selectPoint(e) {

  var mouse = new THREE.Vector2(
    ( e.x / renderer.domElement.clientWidth ) * 2 - 1,
    1 - ( e.y / renderer.domElement.clientHeight ) * 2 );

  raycaster.setFromCamera( mouse, camera );

  console.log("raycaster=",raycaster.ray.origin,raycaster.ray.direction);

  var d = raycaster.ray.origin.dot(raycaster.ray.direction);
  var np = raycaster.ray.origin.clone();
  np.addScaledVector(raycaster.ray.direction,-d);

  var dist = np.length();

  console.log("d=",d,"np=",np,"dist=",dist);

  if (dist < 1.01) {
    var p;
    if (dist >= 1.0) {
      p=np;
    }
    else {
      var dd = Math.sqrt(1.0-dist*dist);
      var p1 = np.clone();
      p1.addScaledVector(raycaster.ray.direction,dd);
      var p2 = np.clone();
      p2.addScaledVector(raycaster.ray.direction,-dd);

      p = p2.z >= 0 ? p2:p1;
    }

    console.log("p=",p);

    if (ec != null) {

      var tol = 1.0e-14;
      var pp = [p.x,p.y,p.z];
      ec.project(pp,tol);
      var dec = ec.distance(pp);

      if (pp[2] >= -0.01 && Math.abs(dec) < tol) {

        if (pp[2] <= 0) {
          // select neutral element
          p.x = 0;
          p.y = Math.sign(pp[1]);
          p.z = 0;
        }
        else {
          p.x = pp[0];
          p.y = pp[1];
          p.z = pp[2];
        }

        var mg = [];
        mg.push(p);
        var mm = new THREE.Points(new THREE.BufferGeometry().setFromPoints(mg),material4);

        if (markers && markers.length > 1) {
          THREE.Scene.prototype.remove.apply(scene,markers);
          markers = null;
          firstPoint = null;
        }

        if (markers == null) {
          markers = [];
          firstPoint = p;
        }

        scene.add(mm);
        markers.push(mm);

        // second point added or Ctrl-Shift clicked
        if (markers.length == 2 || e.doubleSelect) {
          var gg = geomlib.buildGreaterCircle(p,firstPoint,0.01);

          if (gg != null) {
            var gl = new THREE.Line(gg, material5);
            scene.add(gl);
            markers.push(gl);
          }

          var p0 = firstPoint;
          var pq = ec.add([p0.x,p0.y,p0.z],pp);

          var pqg = [];
          pqg.push(new THREE.Vector3(pq.p[0],pq.p[1],pq.p[2]));
          if (pq.n) {
            // second point on curve for the weierstrass case.
            pqg.push(new THREE.Vector3(pq.p[0],-pq.p[1],pq.p[2]));
          }
          var pqm = new THREE.Points(new THREE.BufferGeometry().setFromPoints(pqg),material4);

          scene.add(pqm);
          markers.push(pqm);

          if (pq.n) {
            // plane for the weierstrass case.
            var gg2 = geomlib.buildGreaterCircle(pqg[0],pqg[1],0.01);

            if (gg2 != null) {
              var gl2 = new THREE.Line(gg2, material5);
              scene.add(gl2);
              markers.push(gl2);
            }


            var cg = geomlib.buildCenterPlane(new THREE.Vector3(pq.n[0],pq.n[1],pq.n[2]),planeShown ? planeBdry : 1.2);
            var cmesh = new THREE.Mesh(cg, material6);
            scene.add(cmesh);
            markers.push(cmesh);
          }
        }
      }
    }
  }
};


renderer.domElement.addEventListener("click",function(e) {
  if (e[modifier]) {
    console.log("Ctrl-Click at ",e.x,e.y);
    selectPoint({x:e.clientX,y:e.clientY,doubleSelect:e.shiftKey});

    e.preventDefault();
    e.stopPropagation();
  }
},false);

if (widgets.isTouchDevice()) {

  widgets.addTouchClickHandler(renderer.domElement,function(event) {
    if (event.duration > 500) {
      var p = {x: event.clientX,
               y: event.clientY,
               doubleSelect: event.duration > 1000};

      selectPoint(p);
    }
  });
}


/*
var clock = new THREE.Clock();

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 50 );
camera.position.z = 5;

var pointLight = new THREE.PointLight(0xffffff);
pointLight.position.set( 50, 50, 100 );
camera.add( pointLight );

var ambientLight = new THREE.AmbientLight(0x444444);
camera.add( ambientLight );

const renderer = new THREE.WebGLRenderer();
const controls = new TrackballControls( camera, renderer.domElement );

const geometry = new THREE.BoxGeometry( 1, 1, 1 );
const material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
const cube = new THREE.Mesh( geometry, material );

scene.add( camera );
scene.add( cube );


renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setPixelRatio( window.devicePixelRatio );

document.body.appendChild( renderer.domElement );

var cameraControls = new TrackballControls(camera, renderer.domElement);
cameraControls.target.set(0, 0, 0);

function animate() {
  var delta = clock.getDelta();
  requestAnimationFrame( animate );
  cameraControls.update(delta);
  renderer.render( scene, camera );
}

function onWindowResize(){

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize( window.innerWidth, window.innerHeight );
  renderer.setPixelRatio( window.devicePixelRatio );
}

window.addEventListener( 'resize', onWindowResize, false );

animate();
*/

console.log("ECC visualization successfully started up.");

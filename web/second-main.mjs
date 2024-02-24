import * as THREE from 'three';

import { TrackballControls } from 'three/addons/controls/TrackballControls.js';
import { parseQuery } from './lib/helpers.mjs';
import * as mathx from './lib/mathx.mjs';
import * as geomlib from './lib/geomlib.mjs';

var clock = new THREE.Clock();
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 50 );
camera.position.z = 5;

var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setPixelRatio( window.devicePixelRatio );
document.body.appendChild( renderer.domElement );

var material = new THREE.MeshPhongMaterial( {  side: THREE.DoubleSide,
                                               depthTest: true,
                                               depthWrite: true,
                                               wireframe: false,
                                               vertexColors: true } );

scene.add(geomlib.buildAxes(1.5));

/*
  var ambientLight = new THREE.AmbientLight( 0xffffff );
  camera.add( ambientLight );

  var lights = [];
  lights[0] = new THREE.PointLight( 0xffffff, 1, 0 );
  lights[1] = new THREE.PointLight( 0xffffff, 1, 0 );
  lights[2] = new THREE.PointLight( 0xffffff, 1, 0 );

  lights[0].position.set( 0, 200, 0 );
  lights[1].position.set( 100, 200, 100 );
  lights[2].position.set( -100, -200, -100 );

  camera.add( lights[0] );
  camera.add( lights[1] );
  camera.add( lights[2] );
*/

//var pointLight = new THREE.PointLight( 0xffffff );
//scene.add( pointLight );

var ambientLight = new THREE.AmbientLight( 0xffffff );
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

animate();

var currentMesh = null;
var currentDeferred = null;

var loadData = function() {

  var state = {
    xmin: -1,
    xmax: 1,
    ymin: -1,
    ymax: 1,
    n: 101,
    f: "x*y+0.5*x"
  };

  if (location.hash) {

    var qo = parseQuery(location.hash.substring(1));

    console.log(qo);

    for (var k in state) {

      if (k in qo) {

        if (typeof state[k] == "number") {
          try {
            state[k] = Number(qo[k]);
          } catch (e) {
            console.log("Option", k,
                        " as a non-numeric value.");
          }
        } else {
          state[k] = qo[k];
        }
      }
    }
  }

  if (currentDeferred) {
    console.log("Canceling previous query to /mathx/evaluate...");
    currentDeferred.cancel();
    currentDeferred = null;
  }

  console.log("Querying /mathx/evaluate with state", state);

  currentDeferred = fetch("/mathx/evaluate",{
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body : JSON.stringify(state)
  });

  currentDeferred.then(resp => resp.json()).then(function(res) {
    currentDeferred = null;
    if (res) {

      console.log("/mathx/evaluate returned", {
        f : res.f,
        xmin: res.xmin,
        xmax: res.xmax,
        ymin: res.ymin,
        ymax: res.ymax,
        n : res.n,
        vl : res.values.length
      });
      var geom2 = mathx.genSurfaceGeometry(res);

      var mesh = new THREE.Mesh(geom2, material);

      if (currentMesh) {
        scene.remove(currentMesh);
      }

      scene.add(mesh);
      currentMesh = mesh;
    }
    else if (currentMesh) {
      console.log("/mathx/evaluate returned null");
      scene.remove(currentMesh);
      currentMesh = null;
    }

  }).catch(function(err) {
    currentDeferred = null;
    console.log("/mathx/evaluate failed:", err);
    if (currentMesh) {
      scene.remove(currentMesh);
      currentMesh = null;
    }
  });
};

window.addEventListener("hashchange",loadData, false);
loadData();

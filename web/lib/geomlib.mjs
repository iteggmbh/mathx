import * as THREE from 'three';

export function buildSemiSphere(radius) {

  var vertices = [0,0,radius];
  var indices = [];

  var z = Math.sqrt(0.5);
  var r = Math.sqrt(0.5)*radius;

  for (var i=0;i<5;++i) {
	var alpha = Math.PI * 0.4 * i;

	vertices.push(Math.cos(alpha)*r);
	vertices.push(Math.sin(alpha)*r);
	vertices.push(z);
	indices.push(0);
	indices.push(1+i);
	indices.push(1+(i+1)%5);
  }

  for (var i=0;i<10;++i) {
	var alpha = Math.PI * 0.2 * i;

	vertices.push(Math.cos(alpha)*radius);
	vertices.push(Math.sin(alpha)*radius);
	vertices.push(0.0);
	if (i & 1) {
	  indices.push(6+i);
	  indices.push(1+((i+1)%10)/2);
	  indices.push(1+(i-1)/2);
	}
	else {
	  indices.push(1+i/2);
	  indices.push(6+i);
	  indices.push(6+(i+1)%10);
	  indices.push(1+i/2);
	  indices.push(6+(i+9)%10);
	  indices.push(6+i%10);
	}
  }

  return new THREE.PolyhedronGeometry( vertices, indices, radius, 4);
};

export function buildAxis(src, dst, colorHex, dashed ) {
  var mat;

  if(dashed) {
    mat = new THREE.LineDashedMaterial({ linewidth: 1, color: colorHex, dashSize: 0.04, gapSize: 0.01 });
  } else {
    mat = new THREE.LineBasicMaterial({ linewidth: 1, color: colorHex });
  }

  var vertices = [];
  vertices.push( src.clone() );
  vertices.push( dst.clone() );

  var geom = new THREE.BufferGeometry().setFromPoints(vertices);
  var axis = new THREE.Line( geom, mat, THREE.LinePieces );

  return axis;
};

export function buildAxes(length) {

  var axes = new THREE.Object3D();

  axes.add(buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( length, 0, 0 ), 0xFF0000, false ) ); // +X
  axes.add(buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( -length, 0, 0 ), 0xFF0000, true) ); // -X
  axes.add(buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 0, length, 0 ), 0x00FF00, false ) ); // +Y
  axes.add(buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 0, -length, 0 ), 0x00FF00, true ) ); // -Y
  axes.add(buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 0, 0, length ), 0x0000FF, false ) ); // +Z
  axes.add(buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 0, 0, -length ), 0x0000FF, true ) ); // -Z

  return axes;
};

export function buildGreaterCircle(p,q,step) {

  var norm = new THREE.Vector3();
  norm.crossVectors(p,q);

  if (Math.abs(norm.length()) < 1.0e-8) {
	return null;
  }

  var angle = Math.atan2(norm.length(),p.dot(q));

  norm.normalize();
  var p2 = new THREE.Vector3();
  p2.crossVectors(norm,p);

  var n = Math.ceil((angle * p.length())/step);
  var vertices = [];

  for (var i=0;i<=n;++i) {
	var a = angle * i / n;
    var v = p.clone();
    v.multiplyScalar(Math.cos(a));
    v.addScaledVector(p2,Math.sin(a));
    vertices.push(v);
  }

  return new THREE.BufferGeometry().setFromPoints(vertices);
};

export function buildCenterPlane(norm,len) {

  norm.normalize();

  var norm1 = new THREE.Vector3(-norm.y,norm.x,0.0);
  var norm2 = new THREE.Vector3();

  norm2.crossVectors(norm,norm1);

  norm1.normalize();
  norm2.normalize();

  var geom = new THREE.BufferGeometry();

  var indices = new Uint32Array([0,1,2,2,0,3]);

  var positions = new Float32Array([
    -len * norm1.x, -len*norm1.y, -len*norm1.z,
    len * norm1.x, len*norm1.y, len*norm1.z,
    len * (norm2.x+norm1.x), len*(norm2.y+norm1.y), len*(norm2.z+norm1.z),
    len * (norm2.x-norm1.x), len*(norm2.y-norm1.y), len*(norm2.z-norm1.z),
  ]);

  geom.setIndex( new THREE.BufferAttribute( indices, 1 ) );
  geom.setAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );

  return geom;
};

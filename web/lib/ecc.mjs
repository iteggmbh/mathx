/*
   Elliptic Curve Projective Space Calculation Engine in javascript.

   Author: Wolfgang Glas

   Copyright 2016 ITEG IT-Engineers GmbH

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

*/

import * as THREE from 'three';

export const M_THIRD = 1.0/3.0;

export function sqr(x) { return x*x; };

export function cube(x) { return x*x*x; };

export function length3(p) {
  return Math.hypot.apply(this,p);
};

export function normalize(p) {
  var fac = 1.0/length3(p);
  for (var i=0;i<p.length;++i) {
    p[i] *= fac;
  }
  return p;
};

// p += fac*d
export function multadd(p,fac,d) {
  for (var i=0;i<p.length&&i<d.length;++i) {
    p[i] += fac*d[i];
  }
  return p;
};

export function cross(p,q) {
  return [ p[1]*q[2] - p[2]*q[1],
           p[2]*q[0] - p[0]*q[2],
           p[0]*q[1] - p[1]*q[0] ];
};

// solve x^3 + p x + q = 0
export function cardano(p,q) {

  var delta = sqr(0.5*q)+cube(M_THIRD*p);

  if (delta == 0) {

    if (q == 0) {
      return [0];
    }
    else {
      var x1 = Math.cbrt(-4*q);
      return [x1,-0.5*x1].sort();
    }
  }
  else if (delta > 0) {

    var sqrtd = Math.sqrt(delta);
    var u = Math.cbrt(-0.5*q+sqrtd);
    var v = Math.cbrt(-0.5*q-sqrtd);
    return [u+v];
  }
  else {

    var f = Math.sqrt(-4*M_THIRD*p);
    var alpha = M_THIRD * Math.acos(-0.5*q * Math.sqrt(cube(-3/p)));

    return [f*Math.cos(alpha),
            -f*Math.cos(alpha+M_THIRD*Math.PI),
            -f*Math.cos(alpha-M_THIRD*Math.PI)
           ].sort();
  }
};

export function addTermToHtml(s,fac,term) {

  if (fac == 0) {
    return s;
  }
  else if (fac == -1) {
    return s + " - " + term;
  }
  else if (fac == 1) {
    return s + " + " + term;
  }
  else if (fac < 0) {
    return s + " - " + (-fac) + "&middot;" + term;
  }
  else {
    return s + " + " + fac + "&middot;" + term;
  }
};


export function addVertice(vertices,p,affineBdry) {

  if (affineBdry) {

    if (p[2] < 0.001) {
      return false;
    }

    var x = p[0] / p[2];
    var y = p[1] / p[2];

    vertices.push(
      new THREE.Vector3(x,y,1)
    );

    return Math.abs(x) < affineBdry && Math.abs(y) < affineBdry;
  }
  else {
    vertices.push(
      new THREE.Vector3(p[0],p[1],p[2])
    );
  }
  return true;
}


// base class
export class EllipticCurve {

  // project point p onto curve with precision
  project(p,precision) {

    for (var i=0;i<20;++i) {

      var d = this.distance(p);

      if (Math.abs(d) < precision) {
        return normalize(p);
      }

      var dd = this.gradient(p);

      // console.log("i=",i,"p=",p,"d=",d,"dd=",dd);

      multadd(p,-d/(dd[0]*dd[0]+dd[1]*dd[1]+dd[2]*dd[2]),dd);
    }
    console.log("Warning cannot project point",p,"to elliptic curve in 20 iterations.");
    return normalize(p);
  }


  // make a vertices array of a branch with the given delta
  // return true, if we ran into infinity or false, if we came back over y=0
  _makeBranchVertices(vertices,p0,delta,affineBdry) {

    // fast clone
    var p=p0.slice();

    var ylast = null;

    for (var i=0;i<1000;++i) {

      // normal vector to curve X^3 + a X Z^2 + b Z^3 - Z*Y^2 = 0
      var grad = this.gradient(p);

      // cross product
      var dd = cross(p,grad);

      var fac = delta / length3(dd);
      multadd(p,fac,dd);

      if (p[2] < 0) {

        // singularity reached
        if (affineBdry == null) {
          if (Math.abs(p[0]) > Math.abs(p[1])) {
            vertices.push(
              new THREE.Vector3(Math.sign(p[0]),0,0)
            );
          }
          else {
            vertices.push(
              new THREE.Vector3(0,Math.sign(p[1]),0)
            );
          }
        }
        return true;
      }

      if (p[2] < 0 || (ylast != null && ylast*p[1] <= 0)) {
        return false;
      }

      this.project(p,1.0e-8);

      if (!addVertice(vertices,p,affineBdry)) {
        return true;
      }

      ylast = p[1];
    }
    return true;
  }

  // return an array of THREE.js geometry instances comprising the curve branches
  makeGeometries(affineBdry) {

    var pp=this.initialPoints();
    var ret = [];
    var step = 0.01;

    var mergeCandidate = null;

    for (var i=0;i<pp.length;++i) {

      var vertices = [];

      var p = pp[i];

      normalize(p);

      console.log("pp[",i,"]=",pp[i],",d=",this.distance(p),",dd=",this.gradient(p));

      if (!addVertice(vertices,p,affineBdry)) {
        continue;
      }

      if (this._makeBranchVertices(vertices,p,step,affineBdry)) {

        vertices.reverse();
        this._makeBranchVertices(vertices,p,-step,affineBdry);

        ret.push(new THREE.BufferGeometry().setFromPoints(vertices));
      }
      else if (mergeCandidate) {

        Array.prototype.push.apply(mergeCandidate,vertices);
        // visually close the loop
        mergeCandidate.push(mergeCandidate[0]);

        ret.push(new THREE.BufferGeometry().setFromPoints(mergeCandidate));
        mergeCandidate = null;
      }
      else {
        mergeCandidate = vertices;
      }
    }

    if (mergeCandidate) {
      console.log("Found a half-loop merge candidate with no counterpart");
      ret.push(new THREE.BufferGeometry().setFromPoints(mergeCandidate));
    }

    return ret;
  }
};

//
// elliptic weierstrass curve X^3 + a X Z^2 + b Z^3 - Z*Y^2 = 0
//
export class WeierstrassCurve extends EllipticCurve {

  constructor(a,b) {
    super();
    this.a = a;
    this.b = b;
  }

  toHtml() {
    var ret = "Weierstrass Curve Z&middot;Y<sup>2</sup> = X<sup>3</sup>";

    ret = addTermToHtml(ret,this.a,"X&middot;Z<sup>2</sup>");
    ret = addTermToHtml(ret,this.b,"Z<sup>3</sup>");
    return ret;
  }

  // The curve equation, aka the distance
  distance(p) {

    return cube(p[0]) + this.a*p[0]*sqr(p[2]) + this.b*cube(p[2]) - p[2]*sqr(p[1]);
  }

  // derivation of distance, gradient.
  gradient(p) {

    return [3*sqr(p[0]) + this.a*sqr(p[2]),
            -2*p[1]*p[2],
            2*this.a*p[0]*p[2]+3*this.b*sqr(p[2])-sqr(p[1])];
  }

  // add p and q
  add(p,q) {

    var uvw;

    if (p[0] == q[0] && p[1] == q[1] && p[2] == q[2]) {
      // square operation -> normal vector is gradient.
      uvw = this.gradient(p);
    }
    else {
      // normal vector from two points.
      uvw = cross(p,q);
    }

    console.log("uvw=",uvw);

    // method 1, calculate with (x,y,1)
    if (Math.abs(uvw[1])>0.1) {
      var s = uvw[0]/uvw[1];
      var v1 = uvw[2]/uvw[1];

      var x1 = p[0]/p[2];
      var x2 = q[0]/q[2];

      var x3 = sqr(s) - x1 - x2;

      var ret1 = [x3,(uvw[2]+uvw[0]*x3)/uvw[1],1];

      var self = this;

      var check = function(x) {
        return cube(x) - sqr(s)*sqr(x)+(self.a-2*s*v1)*x+self.b-sqr(v1);
      };

      console.log("check(x1)=",check(x1),"check(x2)=",check(x2),"check(x3)=",check(x3));
      console.log("norm(ret1)=",normalize(ret1));
      return {p:ret1,n:uvw};
    }

	// method2, calculate with (x,1,z)
	else {
	  var s = uvw[2]/uvw[0];
	  var u1 = uvw[1]/uvw[0];

	  var z1 = p[2]/p[1];
	  var z2 = q[2]/q[1];

	  var z3 = (3 * sqr(s) + this.a)*u1/(this.b-cube(s)-this.a*s) - z1 - z2;

	  var ret2 = z3 < 0 ? [(uvw[1]+uvw[2]*z3)/uvw[0],1,-z3] : [-(uvw[1]+uvw[2]*z3)/uvw[0],-1,z3];

	  var self = this;

	  var check = function(z) {
		return (cube(s)+self.a*s-self.b)*cube(z) + (3*sqr(s)+self.a)*u1*sqr(z)+(1+3*sqr(u1)*s)*z+cube(u1);
	  };
	  console.log("check(z1)=",check(z1),"check(z2)=",check(z2),"check(z3)=",check(z3));

	  console.log("norm(ret2)=",normalize(ret2));
	  return {p:ret2,n:uvw};
	}

	// method3, calculate with (1,y,z)
	/*
	  This method is not used, because no gain was observed, even in extreme corner cases.
	  {
	  var s = uvw[2]/uvw[1];
	  var v1 = uvw[0]/uvw[1];

	  var z1 = p[2]/p[0];
	  var z2 = q[2]/q[0];

	  var z3 = (2*s*v1-this.a)/(this.b-sqr(s)) - z1 - z2;

	  var self = this;

	  var check = function(z) {
	  return (sqr(s)-self.b)*cube(z) + (2*s*v1-self.a)*sqr(z)+z*sqr(v1)-1;
	  };

	  console.log("check(z1)=",check(z1),"check(z2)=",check(z2),"check(z3)=",check(z3));

	  var ret3 = z3<0 ? [-1,-(uvw[0]+uvw[2]*z3)/uvw[1],-z3] : [1,(uvw[0]+uvw[2]*z3)/uvw[1],z3];
	  console.log("norm(ret3)=",normalize(ret3));

	  return {p:ret3,n:uvw};
	  }
	*/

  }

  initialPoints () {
	var xx = cardano(this.a,this.b);
	var ret = [];

	for (var i=0;i<xx.length;++i) {
	  ret.push([xx[i],0,1]);
	}
	return ret;
  }
};

//
// Edwards curve (X^2+Y^2)Z^2=Z^4+d X^2 Y^2
//
export class EdwardsCurve extends EllipticCurve {

  constructor(d) {
    super();
	this.d = d;
  }

  toHtml() {
	var ret = "Edwards Curve (X<sup>2</sup> + Y<sup>2</sup>)&middot;Z<sup>2</sup> = Z<sup>4</sup>";

	ret = addTermToHtml(ret,this.d,"X<sup>2</sup>&middot;Y<sup>2</sup>");
	return ret;
  }

  // The curve equation, aka the distance
  distance(p) {

	return (sqr(p[0])+sqr(p[1]))*sqr(p[2]) - sqr(sqr(p[2]))-this.d*sqr(p[0])*sqr(p[1]);
  }

  // derivation of distance, gradient.
  gradient(p) {

	return [
	  2*p[0]*sqr(p[2]) - this.d*2*p[0]*sqr(p[1]),
	  2*p[1]*sqr(p[2]) - this.d*sqr(p[0])*2*p[1],
	  2*(sqr(p[0])+sqr(p[1]))*p[2] - 4 * cube(p[2])
	];
  }


  // add p and q
  add(p,q) {

	var ret;

	if (p[0] == q[0] && p[1] == q[1] && p[2] == q[2]) {
	  // square operation
	  var B =  sqr(p[0]+p[1]);
	  var C = sqr(p[0]);
	  var D =  sqr(p[1]);
	  var E = C+D;
	  var H = sqr(p[2]);
	  var J = E-2*H;
	  ret = [(B-E)*J,E*(C-D),E*J];
	}
	else {
	  var A = p[0]*q[2];
	  var B = p[1]*q[2];
	  var C = p[2]*q[0];
	  var D = p[2]*q[1];
	  var E = A*B;
	  var F = C*D;
	  var G = E+F;
	  var H = E-F;
	  var J = (A-C)*(B+D)-H;
	  var K = (A+D)*(B+C)-G;
	  ret = [G*J,H*K,J*K];
	}

	normalize(ret);
	if (ret[2]<0) {
	  ret[0] = -ret[0];
	  ret[1] = -ret[1];
	  ret[2] = -ret[2];
	}

	return {p:ret};
  }

  initialPoints() {
	var ret = [[-1,0,1],[1,0,1]];

	if (this.d >= 1) {
	  ret.push([0,-1,1]);
	  ret.push([0,1,1]);
	}

	return ret;
  }
};

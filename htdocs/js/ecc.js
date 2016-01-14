var ecc = {

	M_THIRD: 1.0/3.0,
	
	sqr: function(x) { return x*x; },

	cube: function(x) { return x*x*x; },

	cbrt: Math.cbrt || function(x) { return x < 0 ? -Math.pow(-x,M_THIRD) : Math.pow(x,M_THIRD); },

	hypot: Math.hypot ||
		function() { var l=0.0; for (var i=0;i<arguments.length;++i) l+=ecc.sqr(arguments[i]); return Math.sqrt(l);  },

	length3: function(p) {
		return ecc.hypot.apply(ecc,p);
	},
	
	normalize: function(p) {
		var fac = 1.0/ecc.length3(p);
		for (var i=0;i<p.length;++i) {
			p[i] *= fac;
		}
		return p;
	},

	// p += fac*d
	multadd: function(p,fac,d) {
		for (var i=0;i<p.length&&i<d.length;++i) {
			p[i] += fac*d[i];
		}
		return p;
	},

    cross: function(p,q) {
		return [ p[1]*q[2] - p[2]*q[1],
				 p[2]*q[0] - p[0]*q[2],
				 p[0]*q[1] - p[1]*q[0] ];
	},
	
	// solve x^3 + p x + q = 0
	cardano: function(p,q) {

		var delta = ecc.sqr(0.5*q)+ecc.cube(ecc.M_THIRD*p);

		if (delta == 0) {

			if (q == 0) {
				return [0];
			}
			else {
				var x1 = ecc.cbrt(-4*q);
				return [x1,-0.5*x1].sort();
			}
		}
		else if (delta > 0) {

			var sqrtd = Math.sqrt(delta);
			var u = ecc.cbrt(-0.5*q+sqrtd);					   
			var v = ecc.cbrt(-0.5*q-sqrtd);					   
		    return [u+v];
		}
		else {

			var f = Math.sqrt(-4*ecc.M_THIRD*p);
			var alpha = ecc.M_THIRD * Math.acos(-0.5*q * Math.sqrt(ecc.cube(-3/p)));

			return [f*Math.cos(alpha),
					-f*Math.cos(alpha+ecc.M_THIRD*Math.PI),
					-f*Math.cos(alpha-ecc.M_THIRD*Math.PI)
				   ].sort();
		}
	}
};

// elliptic curve X^3 + a X Z^2 + b Z^3 - Z*Y^2 = 0
ecc.EllipticCurve = function(a,b) {
	this.a = a;
	this.b = b;
};

ecc.EllipticCurve.prototype.distance = function(p) {
	
	return ecc.cube(p[0]) + this.a*p[0]*ecc.sqr(p[2]) + this.b*ecc.cube(p[2]) - p[2]*ecc.sqr(p[1]);
};

// derivation of distance, gradient.
ecc.EllipticCurve.prototype.gradient = function(p) {
	
	return [3*ecc.sqr(p[0]) + this.a*ecc.sqr(p[2]),
			-2*p[1]*p[2],
			2*this.a*p[0]*p[2]+3*this.b*ecc.sqr(p[2])-ecc.sqr(p[1])];
};

// project point p onto curve with precision
ecc.EllipticCurve.prototype.project = function(p,precision) {

	for (var i=0;i<20;++i) {

		var d = this.distance(p);

		if (Math.abs(d) < precision) {
			return ecc.normalize(p);
		}

		var dd = this.gradient(p);

		// console.log("i=",i,"p=",p,"d=",d,"dd=",dd);

		ecc.multadd(p,-d/(dd[0]*dd[0]+dd[1]*dd[1]+dd[2]*dd[2]),dd);
	}
	console.log("Warning cannot project point",p,"to elliptic curve in 20 iterations.");
	return ecc.normalize(p);
};

// add p and q
ecc.EllipticCurve.prototype.add = function(p,q) {

	var uvw;

	if (p[0] == q[0] && p[1] == q[1] && p[2] == q[2]) {
		// square operation -> normal vector is gradient.
		uvw = this.gradient(p);
	}
	else {
		// normal vector from two points.
		uvw = ecc.cross(p,q);
	}

	console.log("uvw=",uvw);

	// method 1, calculate with (x,y,1)
	if (Math.abs(uvw[1])>0.1) {
		var s = uvw[0]/uvw[1];
		var v1 = uvw[2]/uvw[1];
		
		var x1 = p[0]/p[2];
		var x2 = q[0]/q[2];
		
		var x3 = ecc.sqr(s) - x1 - x2;
		
		var ret1 = [x3,(uvw[2]+uvw[0]*x3)/uvw[1],1];
		
		var self = this;
		
		var check = function(x) {
			return ecc.cube(x) - ecc.sqr(s)*ecc.sqr(x)+(self.a-2*s*v1)*x+self.b-(ecc.sqr(v1));
		};
		
		console.log("check(x1)=",check(x1),"check(x2)=",check(x2),"check(x3)=",check(x3));
		console.log("norm(ret1)=",ecc.normalize(ret1));
		return {p:ret1,n:uvw};
	}
	
	// method2, calculate with (x,1,z)
	else {
		var s = uvw[2]/uvw[0];
		var u1 = uvw[1]/uvw[0];
		
		var z1 = p[2]/p[1];
		var z2 = q[2]/q[1];
		
		var z3 = (3 * ecc.sqr(s) + this.a)*u1/(this.b-ecc.cube(s)-this.a*s) - z1 - z2;

		var ret2 = z3 < 0 ? [(uvw[1]+uvw[2]*z3)/uvw[0],1,-z3] : [-(uvw[1]+uvw[2]*z3)/uvw[0],-1,z3];
		
		var self = this;

		var check = function(z) {
			return (ecc.cube(s)+self.a*s-self.b)*ecc.cube(z) + (3*ecc.sqr(s)+self.a)*u1*ecc.sqr(z)+(1+3*ecc.sqr(u1)*s)*z+ecc.cube(u1);
		};
		console.log("check(z1)=",check(z1),"check(z2)=",check(z2),"check(z3)=",check(z3));
		
		console.log("norm(ret2)=",ecc.normalize(ret2));
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
		
		var z3 = (2*s*v1-this.a)/(this.b-ecc.sqr(s)) - z1 - z2;
		
		var self = this;

		var check = function(z) {
			return (ecc.sqr(s)-self.b)*ecc.cube(z) + (2*s*v1-self.a)*ecc.sqr(z)+z*ecc.sqr(v1)-1;
		};
		
		console.log("check(z1)=",check(z1),"check(z2)=",check(z2),"check(z3)=",check(z3));

		var ret3 = z3<0 ? [-1,-(uvw[0]+uvw[2]*z3)/uvw[1],-z3] : [1,(uvw[0]+uvw[2]*z3)/uvw[1],z3];
		console.log("norm(ret3)=",ecc.normalize(ret3));

		return {p:ret3,n:uvw};
	}
	*/
	
}

// make a vertices array of a branch with the given delta
// return true, if we ran into infinity or false, if we came back over y=0
ecc.EllipticCurve.prototype._makeBranchVertices = function(vertices,p0,delta) {

	// fast clone
	var p=p0.slice();
	
	var ylast = null;
		
	for (var i=0;i<1000;++i) {
        
		// normal vector to curve X^3 + a X Z^2 + b Z^3 - Z*Y^2 = 0
		var grad = this.gradient(p); 
		
		// cross product
		var dd = ecc.cross(p,grad);
		
 		fac = delta / ecc.length3(dd);
		ecc.multadd(p,fac,dd);
		
		if (p[2] < 0) {
			vertices.push(
				new THREE.Vector3(0,Math.sign(p[1]),0)
			);
			
			return true;
		}
		
		if (p[2] < 0 || (ylast != null && ylast*p[1] <= 0)) {
			return false;
		}

		this.project(p,1.0e-8);
		
		vertices.push(
            new THREE.Vector3(p[0],p[1],p[2])
		);
		
		ylast = p[1];
	}
	return true;
}

ecc.EllipticCurve.prototype.makeGeometries = function() {

	var xx=ecc.cardano(this.a,this.b);
	var ret = [];
	var step = 0.01;

	var mergeCandidate = null;

	
	for (var i=0;i<xx.length;++i) {
		
        var geom = new THREE.Geometry();

		var p = [xx[i],0,1];
		
		ecc.normalize(p);

		console.log("xx[",i,"]=",xx[i],",d=",this.distance(p),",dd=",this.gradient(p));

		geom.vertices.push(
            new THREE.Vector3(p[0],p[1],p[2])
		);

		if (this._makeBranchVertices(geom.vertices,p,step)) {

			geom.vertices.reverse();
			this._makeBranchVertices(geom.vertices,p,-step);
			ret.push(geom);
		}
		else if (mergeCandidate) {

			Array.prototype.push.apply(mergeCandidate.vertices,geom.vertices);
			// visually close the loop
			mergeCandidate.vertices.push(mergeCandidate.vertices[0]);
			
			ret.push(mergeCandidate);
			mergeCandidate = null;
		}
		else {
			mergeCandidate = geom;
		}
	}

	if (mergeCandidate) {
		console.log("Found a half-loop merge candidate with no counterpart");
		ret.push(mergeCandidate);
	}
	
	return ret;
};

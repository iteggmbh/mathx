var ecc = {

	M_THIRD: 1.0/3.0,
	
	sqr: function(x) { return x*x; },

	cube: function(x) { return x*x*x; },

	cbrt: Math.cbrt || function(x) { return x < 0 ? -Math.pow(x,M_THIRD) : Math.pow(x,M_THIRD); },

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

		var delta = ecc.sqr(0.5*q)+ecc.cube(ecc.M_THIRD*a);

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
	
	return [2*ecc.sqr(p[0]) + this.a*ecc.sqr(p[2]),
			-2*p[1]*p[2],
			2*this.a*p[0]*p[2]+3*this.b*ecc.sqr(p[2])-ecc.sqr(p[1])];
};

// project point p onto curve with precision
ecc.EllipticCurve.prototype.project = function(p,precision) {

	for (var i=0;i<10;++i) {

		ecc.normalize(p);

		var d = this.distance(p);

		if (Math.abs(d) < precision) {
			return p;
		}

		var dd = this.gradient(p);

		// console.log("i=",i,"p=",p,"d=",d,"dd=",dd);

		ecc.multadd(p,-d/(dd[0]*dd[0]+dd[1]*dd[1]+dd[2]*dd[2]),dd);
	}
	console.log("Warning cannot project point",p,"to elliptic curve in 10 iterations.");
	return p;
};

ecc.EllipticCurve.prototype.makeGeometries = function() {

	var xx=ecc.cardano(this.a,this.b);
	var ret = [];
	
	for (var i=0;i<xx.length;++i) {
		
        var geom = new THREE.Geometry();

		var p = [xx[i],0,1];
		ecc.normalize(p);
		var ylast = null;
		
		for (var i=0;i<1000;++i) {
                
			// normal vector to curve X^3 + a X Z^2 + b Z^3 - Z*Y^2 = 0
			var grad = this.gradient(p); 
			
			// cross product
			var dd = ecc.cross(p,grad);
			
 			fac = 0.01 / ecc.length3(dd);
			ecc.multadd(p,fac,dd);

			if (p[2] < 0 || (ylast != null && ylast*p[1] <= 0)) {
				break;
			}

			this.project(p,1.0e-8);
			
     		geom.vertices.push(
                new THREE.Vector3(p[0],p[1],p[2])
			);

			ylast = p[1];
			ret.push(geom);
		}
	}

	return ret;
};

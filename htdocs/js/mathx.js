var mathx = {
		
genSurfaceGeometry: function(state) {
	
	var geom = new THREE.BufferGeometry();

	//var indices = new Uint32Array([0,1,3, 3,1,4, 1,2,4, 4,2,5, 3,4,6, 6,4,7, 4,5,7, 7,5,8 ]);
	var indices = new Uint32Array((state.n-1)*(state.n-1)*6);

	var positions = new Float32Array(state.n*state.n*3);
	var colors = new Float32Array(state.n*state.n*3);

	var palette = [[0,0,1],[0,1,1],[0,1,0],[1,1,0],[1,0,0],[1,0,1]];
	
	var colv = function(v) {
        
		vi = (palette.length-1) * v;
   	    var n = Math.floor(vi);
	    			
        if (n < 0) {
			n=0;
			return palette[0];
		}
		else if (n >= palette.length-1) {
	        return palette[palette.length-1];
	    }
	    else {
	       var d1 = n+1 - vi;
           var d2 = vi - n;
           var c1 = palette[n];
           var c2 = palette[n+1];
	       return [ c1[0]*d1+c2[0]*d2,c1[1]*d1+c2[1]*d2,c1[2]*d1+c2[2]*d2 ];
	    }
	}

	var idx = 0;
	var iidx = 0;
	var vmin = Number.MAX_VALUE;
	var vmax = Number.MIN_VALUE;
	
	// calculate vmin, vmax
	for (var i=0;i<state.n;++i) {

		for (var j=0;j<state.n;++j) {
			
			var v = state.values[idx++];
			
			vmin = Math.min(vmin,v);
			vmax = Math.max(vmax,v);
		}
	}
	
	var n1 = state.n-1;
	var xscale = 1.0/(Math.max(Math.abs(state.xmin),Math.abs(state.xmax))*n1);
	var yscale = 1.0/(Math.max(Math.abs(state.ymin),Math.abs(state.ymax))*n1);
	var zscale = 1.0/Math.max(Math.abs(vmin),Math.abs(vmax));
	var vscale = 1.0/(vmax-vmin);
	
	idx = 0;
	var posIndices = [];
	
	for (var i=0;i<state.n;++i) {

		var x =  (state.xmax * i + state.xmin *(n1-i))*xscale;
						  
		for (var j=0;j<state.n;++j) {
			
			var y = (state.ymax * j + state.ymin *(n1-j))*yscale;
			var v = state.values[idx];
			
			if (v == null) {
				posIndices.push(null);
			}
			else {
				posIndices.push(iidx/3);
				
				var z = v*zscale;
				var c = colv((v-vmin)*vscale);
			
				//var v = x+y;
				positions[iidx] = x;
				colors[iidx] = c[0];
				++iidx;
				positions[iidx] = y;  
				colors[iidx] = c[1];
				++iidx;
				positions[iidx] = z;
				colors[iidx] = c[2];
				++iidx;
			}
			++idx;
        }
	}
	idx = 0;				  
	iidx = 0;
	for (var i=0;i<state.n-1;++i) {

		for (var j=0;j<state.n-1;++j) {
			
			//
			// n1---n2
			// |   / |
			// |  /  |
			// | /   |
			// n3---n4
			//
			var n1 = posIndices[idx];
			var n2 = posIndices[idx+1];
			var n3 = posIndices[idx+state.n];
			var n4 = posIndices[idx+state.n+1];
			
			if (n1 != null && n2 !=null && n3!=null && n4!= null) {
				indices[iidx++] = n1;
				indices[iidx++] = n2;
				indices[iidx++] = n3;
			
				indices[iidx++] = n2;
				indices[iidx++] = n4;
				indices[iidx++] = n3;
			}
			
			++idx;
		}
		++idx;						
    }
						  
	geom.setIndex( new THREE.BufferAttribute( indices, 1 ) );
	geom.addAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
	geom.addAttribute( 'color', new THREE.BufferAttribute( colors, 3 ) );
	return geom;
}
		
		
};

export function parseQuery(s) {

  var opts = s.split('&');

  var ret = {};

  for (var i=0;i<opts.length;++i) {

    var kv = opts[i].split('=',2);

	var key = kv[0];

	if (key) {

	  var value = kv.length>1 ? decodeURIComponent(kv[1]) : null;

	  ret[key] = value;
	}

  }

  return ret;
}

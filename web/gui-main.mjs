import { parseQuery } from './lib/helpers.mjs';

function onContentLoad() {
  var xmin = document.getElementById("inputXmin");
  var xmax = document.getElementById("inputXmax");
  var ymin = document.getElementById("inputYmin");
  var ymax = document.getElementById("inputYmax");
  var f = document.getElementById("inputF");
  var n = document.getElementById("inputN");
  var outputUrl = document.getElementById("outputUrl");
  var iframeHolder = document.getElementById("iframeHolder");

  function onWindowResize(){

    iframeHolder.firstElementChild.setAttribute('width',iframeHolder.offsetWidth);
    iframeHolder.firstElementChild.setAttribute('height',iframeHolder.offsetHeight);
  }

  window.addEventListener('resize',onWindowResize,false);

  function propagateState(state) {

    var url = "second.html";
    var hash = "";
    var sep = "#";
    for (var k in state) {
      hash += sep;
      hash += k;
      hash += "=";
      hash += state[k];
      sep="&";
    }
    url += hash;
    outputUrl.value = location.href.replace(/\/[^/]*$/,"/")+url;
    if (iframeHolder.firstElementChild.src != url) {
      iframeHolder.firstElementChild.setAttribute('src',url);
    }
    location.hash = hash;
  }

  function onHashChange() {
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
    xmin.value = state.xmin;
    xmax.value = state.xmax;
    ymin.value = state.ymin;
    ymax.value = state.ymax;
    n.value = state.n;
    f.value = state.f;
    propagateState(state);
  }

  function changeURL() {

    var state = {};
    xmin.className = isNaN(state.xmin = parseFloat(xmin.value)) ? 'invalid':'';
    xmax.className = isNaN(state.xmax = parseFloat(xmax.value)) ? 'invalid':'';
    ymin.className = isNaN(state.ymin = parseFloat(ymin.value)) ? 'invalid':'';
    ymax.className = isNaN(state.ymax = parseFloat(ymax.value)) ? 'invalid':'';
    state.n = parseInt(n.value);
    n.className = (isNaN(state.n) || state.n <= 1 || state.n > 201) ? 'invalid':'';
    state.f = encodeURIComponent(f.value).replace('%5E','^').replace('%2F','/');
    f.className = state.f.length <= 0 ? 'invalid':'';

    var valid = !isNaN(state.xmin) && !isNaN(state.xmax) &&
        !isNaN(state.ymin) && !isNaN(state.ymax) &&
      !isNaN(state.n) && state.n > 1 && state.n <= 201 &&
      state.f.length > 0;

    console.log("state=",state);

    if (valid) {
      propagateState(state);
    }
    else {
      outputUrl.value = '';
    }
  }

  xmin.addEventListener('input',changeURL);
  xmax.addEventListener('input',changeURL);
  ymin.addEventListener('input',changeURL);
  ymax.addEventListener('input',changeURL);
  n.addEventListener('input',changeURL);
  f.addEventListener('input',changeURL);
  onWindowResize();
  window.addEventListener("hashchange",onHashChange, false);
  onHashChange();
}

document.addEventListener("DOMContentLoaded",onContentLoad,false);

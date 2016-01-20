var widgets = {

	buildDomNode: function(kwargs,elementType) {

		var domNode;
		var nodeOrId = kwargs.domNode;
		
		if (nodeOrId) {
			if (typeof nodeOrId == "string") {
				domNode = document.getElementById(nodeOrId);
			}
			else {
				domNode = nodeOrId;
			}
		}
		else {
		    domNode = document.createElement("div");
		}

		var cls = kwargs["class"];
		if (cls) {
			domNode.classList.add.apply(this.domNode.classList,cls.split(/\s+/));
		}
		return domNode;
	},

	// touch detection according to
	// https://ctrlq.org/code/19616-detect-touch-screen-javascript
	isTouchDevice: function() {
		return ('ontouchstart' in window) ||
			navigator.MaxTouchPoints > 0 ||
			navigator.msMaxTouchPoints > 0;
	},
	
	Button: function(kwargs) {

		this.domNode = widgets.buildDomNode(kwargs,"div");
		
		this.domNode.setAttribute("role","button");

		var tabIndex = null;
		
		Object.defineProperty(this, 'disabled', {
			get: function() {
				return this.domNode.getAttribute("aria-disabled") != null;
			},
			set: function(newValue) {
				if (newValue) {
					this.domNode.setAttribute("aria-disabled","true");
					this.domNode.classList.add("ariaDisabled");
					this.domNode.removeAttribute("tabIndex");
				}
				else {
					this.domNode.removeAttribute("aria-disabled");
					this.domNode.classList.remove("ariaDisabled");
					this.domNode.setAttribute("tabIndex",tabIndex);
				}
			},
			enumerable: true,
			configurable: true
		});

		Object.defineProperty(this, 'tabIndex', {
			get: function() {
				return tabIndex;
			},
			set: function(newValue) {

				tabIndex = newValue;
				if (!this.disabled) {
					this.domNode.setAttribute("tabIndex",newValue);
				}
			},
			enumerable: true,
			configurable: true
		});

		kwargs.disabled != null && (this.disabled = kwargs.disabled);
		this.tabIndex = kwargs.tabIndex == null ? 0 : kwargs.tabIndex;
	},

	addAriaClickHandler: function(w,handler,useCapture) {

		if (widgets.isTouchDevice()) {
			return widgets.addTouchClickHandler(w,handler,useCapture);
		}
		
		var domNode = w.domNode || w;

		var keyEvent = null;
		var mouseEvent = null;
		var cancelClick = null;

		var onMouseMove = function(event){
			if (mouseEvent && mouseEvent.target == event.target) {

				if (Math.abs(mouseEvent.clientX-event.clientX) > 10 ||
					Math.abs(mouseEvent.clientY-event.clientY) > 10   ) {
					cancelClick();
				}
			}
			else {
				cancelClick();
			}
		};
		
		cancelClick = function() {

			if (keyEvent || mouseEvent) {
				domNode.classList.remove("ariaActive");
			}
			
			keyEvent = null;
			if (mouseEvent) {
				domNode.removeEventListener("mousemove",onMouseMove);
				mouseEvent = null;
			}
		};
		
        var onKeyDown = function(event){

			if (!event.target || event.target.getAttribute("aria-disabled")) {
				return;
			}

			if (event.keyCode == 32 || event.keyCode == 10 || event.keyCode == 13) {

				keyEvent = { type: "keyclick",
							 t: new Date(),
							 target: event.target,
							 keyCode: event.keyCode
						   };
				
				domNode.classList.add("ariaActive");
				//console.log("Key down at ",keyEvent);
			}
		};
		
		var onKeyUp = function(event){

			if (keyEvent) {

				if (keyEvent.target==event.target) {
					var d = new Date();
					keyEvent.duration = d.getTime() - keyEvent.t.getTime();
					//console.log("Key up at ",keyEvent);
					var e = keyEvent;
					cancelClick();
					handler(e);
				}
				else {
					cancelClick();
				}
			}
		};		

        var onMouseDown = function(event){

			if (!event.target || event.target.getAttribute("aria-disabled")) {
				return;
			}

			mouseEvent = { type: "mouseclick",
						 t: new Date(),
						 target: event.target,
						 clientX: event.clientX,
						 clientY: event.clientY
					   };
			
			domNode.classList.add("ariaActive");
			domNode.addEventListener("mousemove",onMouseMove);
			//console.log("Mouse down at ",mouseEvent);
		};
		
		var onMouseUp = function(event){

			if (mouseEvent) {

				if (mouseEvent.target==event.target) {
					var d = new Date();
					mouseEvent.duration = d.getTime() - mouseEvent.t.getTime();
					//console.log("Mouse up at ",mouseEvent);
					var e = mouseEvent;
					cancelClick();
					handler(e);
				}
				else {
					cancelClick();
				}
			}
		};		

		domNode.addEventListener("mousedown",onMouseDown,useCapture);
		domNode.addEventListener("mouseup",onMouseUp,useCapture);
		domNode.addEventListener("keydown",onKeyDown,useCapture);
		domNode.addEventListener("keyup",onKeyUp,useCapture);
		domNode.addEventListener("blur",cancelClick,useCapture);
		domNode.addEventListener("mouseleave",cancelClick,useCapture);

		return {
			remove: function() {
				domNode.removeEventListener("mousedown",onMouseDown,useCapture);
				domNode.removeEventListener("mouseup",onMouseUp,useCapture);
				domNode.removeEventListener("keydown",onKeyDown,useCapture);
				domNode.removeEventListener("keyup",onKeyUp,useCapture);
				domNode.removeEventListener("blur",cancelClick,useCapture);
				domNode.removeEventListener("mouseleave",cancelClick,useCapture);
				cancelClick();
			}
		};
	},

	addTouchClickHandler: function(w,handler,useCapture) {

		var domNode = w.domNode || w;

        var touchPos = null;
		var cancelTouch = null;
		
		var onTouchMove = function(event){
			if (event.touches.length == 1 && touchPos && touchPos.target == event.target) {
				var touch = event.touches[0];
				
				if (Math.abs(touchPos.clientX-touch.clientX) > 10 ||
					Math.abs(touchPos.clientY-touch.clientY) > 10   ) {
					cancelTouch();
				}
			}
			else {
				cancelTouch();
			}
		};
		
		cancelTouch = function() {
			if (touchPos) {
				touchPos.target && touchPos.target.classList.remove("ariaActive");
				domNode.removeEventListener("touchmove",onTouchMove,useCapture);
				domNode.classList.remove("ariaActive");
				touchPos = null;
			}
		};
		
        var onTouchStart = function(event){

			if (!event.target || event.target.getAttribute("aria-disabled")) {
				return;
			}

			if (event.touches.length == 1) {
				var touch = event.touches[0];
				touchPos = { type: "touchclick",
							 t: new Date(),
							 target: event.target,
							 clientX:touch.clientX,
							 clientY:touch.clientY };
				domNode.classList.add("ariaActive");
				domNode.addEventListener("touchmove",onTouchMove,useCapture);
				//console.log("Touch start at ",touchPos);
			}
		};
		
		var onTouchEnd = function(event){

			if (touchPos && event.touches.length == 0) {
				
				var d = new Date();
				touchPos.duration = d.getTime() - touchPos.t.getTime();
				//console.log("Touch end at ",touchPos);
				var e = touchPos;
				cancelTouch();
				handler(e);
			}
		};		

		domNode.addEventListener("touchstart",onTouchStart,useCapture);
		domNode.addEventListener("touchend",onTouchEnd,useCapture);

		return {
			remove: function() {
				domNode.removeEventListener("touchstart",onTouchStart,useCapture);
				domNode.removeEventListener("touchend",onTouchEnd,useCapture);
				cacncelTouch();
			}
		};

	}
};

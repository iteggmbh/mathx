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
		var domNode = w.domNode || w;

		var dispatch = function(e) {
			
			if (!domNode.getAttribute("aria-disabled")) {
				if (e.type != "keyup" || e.keyCode == 32 || e.keyCode == 10 || e.keyCode == 13) {
					handler(e);
				}
			}
		};
		
		domNode.addEventListener("click",dispatch,useCapture);
		domNode.addEventListener("keyup",dispatch,useCapture);

		return {
			remove: function() {
				domNode.removeEventListener("click");
				domNode.removeEventListener("keyup");
			}
		};
	}
};

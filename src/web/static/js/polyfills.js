/**
 * Safari浏览器兼容性Polyfills
 * 解决Safari浏览器对ES6+特性支持不完整的问题
 */

// URLSearchParams polyfill for Safari < 10.1
if (!window.URLSearchParams) {
    window.URLSearchParams = function(search) {
        var self = this;
        self.params = {};
        
        if (search) {
            search.replace(/^\?/, '').split('&').forEach(function(param) {
                var parts = param.split('=');
                var key = decodeURIComponent(parts[0]);
                var value = parts[1] ? decodeURIComponent(parts[1]) : '';
                self.params[key] = value;
            });
        }
        
        self.append = function(key, value) {
            self.params[key] = value;
        };
        
        self.toString = function() {
            var pairs = [];
            for (var key in self.params) {
                if (self.params.hasOwnProperty(key)) {
                    pairs.push(encodeURIComponent(key) + '=' + encodeURIComponent(self.params[key]));
                }
            }
            return pairs.join('&');
        };
    };
}

// fetch polyfill for Safari < 10.1
if (!window.fetch) {
    window.fetch = function(url, options) {
        return new Promise(function(resolve, reject) {
            var xhr = new XMLHttpRequest();
            var method = (options && options.method) || 'GET';
            var headers = (options && options.headers) || {};
            var body = options && options.body;
            
            xhr.open(method, url, true);
            
            // 设置请求头
            for (var header in headers) {
                if (headers.hasOwnProperty(header)) {
                    xhr.setRequestHeader(header, headers[header]);
                }
            }
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    var response = {
                        ok: xhr.status >= 200 && xhr.status < 300,
                        status: xhr.status,
                        statusText: xhr.statusText,
                        json: function() {
                            return Promise.resolve(JSON.parse(xhr.responseText));
                        },
                        text: function() {
                            return Promise.resolve(xhr.responseText);
                        }
                    };
                    
                    if (response.ok) {
                        resolve(response);
                    } else {
                        reject(new Error('HTTP ' + xhr.status + ': ' + xhr.statusText));
                    }
                }
            };
            
            xhr.onerror = function() {
                reject(new Error('Network error'));
            };
            
            xhr.send(body);
        });
    };
}

// Promise polyfill for Safari < 7.1
if (!window.Promise) {
    window.Promise = function(executor) {
        var self = this;
        self.state = 'pending';
        self.value = undefined;
        self.handlers = [];
        
        function resolve(result) {
            if (self.state === 'pending') {
                self.state = 'fulfilled';
                self.value = result;
                self.handlers.forEach(handle);
                self.handlers = null;
            }
        }
        
        function reject(error) {
            if (self.state === 'pending') {
                self.state = 'rejected';
                self.value = error;
                self.handlers.forEach(handle);
                self.handlers = null;
            }
        }
        
        function handle(handler) {
            if (self.state === 'pending') {
                self.handlers.push(handler);
            } else {
                if (self.state === 'fulfilled' && typeof handler.onFulfilled === 'function') {
                    handler.onFulfilled(self.value);
                }
                if (self.state === 'rejected' && typeof handler.onRejected === 'function') {
                    handler.onRejected(self.value);
                }
            }
        }
        
        self.then = function(onFulfilled, onRejected) {
            return new Promise(function(resolve, reject) {
                handle({
                    onFulfilled: function(result) {
                        try {
                            if (typeof onFulfilled === 'function') {
                                resolve(onFulfilled(result));
                            } else {
                                resolve(result);
                            }
                        } catch (ex) {
                            reject(ex);
                        }
                    },
                    onRejected: function(error) {
                        try {
                            if (typeof onRejected === 'function') {
                                resolve(onRejected(error));
                            } else {
                                reject(error);
                            }
                        } catch (ex) {
                            reject(ex);
                        }
                    }
                });
            });
        };
        
        self.catch = function(onRejected) {
            return self.then(null, onRejected);
        };
        
        try {
            executor(resolve, reject);
        } catch (ex) {
            reject(ex);
        }
    };
    
    Promise.resolve = function(value) {
        return new Promise(function(resolve) {
            resolve(value);
        });
    };
    
    Promise.reject = function(error) {
        return new Promise(function(resolve, reject) {
            reject(error);
        });
    };
    
    Promise.all = function(promises) {
        return new Promise(function(resolve, reject) {
            var results = [];
            var remaining = promises.length;
            
            if (remaining === 0) {
                resolve(results);
                return;
            }
            
            promises.forEach(function(promise, index) {
                Promise.resolve(promise).then(function(value) {
                    results[index] = value;
                    remaining--;
                    if (remaining === 0) {
                        resolve(results);
                    }
                }, reject);
            });
        });
    };
}

// Object.assign polyfill for Safari < 9
if (!Object.assign) {
    Object.assign = function(target) {
        if (target == null) {
            throw new TypeError('Cannot convert undefined or null to object');
        }
        
        var to = Object(target);
        
        for (var index = 1; index < arguments.length; index++) {
            var nextSource = arguments[index];
            
            if (nextSource != null) {
                for (var nextKey in nextSource) {
                    if (Object.prototype.hasOwnProperty.call(nextSource, nextKey)) {
                        to[nextKey] = nextSource[nextKey];
                    }
                }
            }
        }
        
        return to;
    };
}

// Array.from polyfill for Safari < 9
if (!Array.from) {
    Array.from = function(arrayLike, mapFn, thisArg) {
        var C = this;
        var items = Object(arrayLike);
        var len = parseInt(items.length) || 0;
        var A = typeof C === 'function' ? Object(new C(len)) : new Array(len);
        var k = 0;
        var kValue;
        
        while (k < len) {
            kValue = items[k];
            if (mapFn) {
                A[k] = typeof thisArg === 'undefined' ? mapFn(kValue, k) : mapFn.call(thisArg, kValue, k);
            } else {
                A[k] = kValue;
            }
            k += 1;
        }
        
        A.length = len;
        return A;
    };
}

// String.prototype.includes polyfill for Safari < 9
if (!String.prototype.includes) {
    String.prototype.includes = function(search, start) {
        if (typeof start !== 'number') {
            start = 0;
        }
        
        if (start + search.length > this.length) {
            return false;
        } else {
            return this.indexOf(search, start) !== -1;
        }
    };
}

// Array.prototype.includes polyfill for Safari < 9
if (!Array.prototype.includes) {
    Array.prototype.includes = function(searchElement, fromIndex) {
        return this.indexOf(searchElement, fromIndex) !== -1;
    };
}

// CustomEvent polyfill for Safari < 6
if (!window.CustomEvent) {
    window.CustomEvent = function(event, params) {
        params = params || { bubbles: false, cancelable: false, detail: undefined };
        var evt = document.createEvent('CustomEvent');
        evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
        return evt;
    };
    
    CustomEvent.prototype = window.Event.prototype;
}

// requestAnimationFrame polyfill for Safari < 6.1
if (!window.requestAnimationFrame) {
    window.requestAnimationFrame = function(callback) {
        return setTimeout(callback, 1000 / 60);
    };
    
    window.cancelAnimationFrame = function(id) {
        clearTimeout(id);
    };
}

// classList polyfill for Safari < 5.1
if (!('classList' in document.createElement('_'))) {
    (function(view) {
        if (!('Element' in view)) return;
        
        var classListProp = 'classList',
            protoProp = 'prototype',
            elemCtrProto = view.Element[protoProp],
            objCtr = Object,
            strTrim = String[protoProp].trim || function() {
                return this.replace(/^\s+|\s+$/g, '');
            },
            arrIndexOf = Array[protoProp].indexOf || function(item) {
                var i = 0, len = this.length;
                for (; i < len; i++) {
                    if (i in this && this[i] === item) {
                        return i;
                    }
                }
                return -1;
            };
        
        var DOMTokenList = function(el) {
            this.el = el;
            var classes = el.className.replace(/^\s+|\s+$/g, '').split(/\s+/);
            for (var i = 0, len = classes.length; i < len; i++) {
                this.push(classes[i]);
            }
            this._updateClassName = function() {
                el.className = this.toString();
            };
        };
        
        var tokenListProto = DOMTokenList[protoProp] = [];
        
        tokenListProto.item = function(i) {
            return this[i] || null;
        };
        
        tokenListProto.contains = function(token) {
            token += '';
            return arrIndexOf.call(this, token) !== -1;
        };
        
        tokenListProto.add = function() {
            var tokens = arguments;
            var i = 0;
            var l = tokens.length;
            var token;
            var updated = false;
            do {
                token = tokens[i] + '';
                if (arrIndexOf.call(this, token) === -1) {
                    this.push(token);
                    updated = true;
                }
            } while (++i < l);
            
            if (updated) {
                this._updateClassName();
            }
        };
        
        tokenListProto.remove = function() {
            var tokens = arguments;
            var i = 0;
            var l = tokens.length;
            var token;
            var updated = false;
            var index;
            do {
                token = tokens[i] + '';
                index = arrIndexOf.call(this, token);
                while (index !== -1) {
                    this.splice(index, 1);
                    updated = true;
                    index = arrIndexOf.call(this, token);
                }
            } while (++i < l);
            
            if (updated) {
                this._updateClassName();
            }
        };
        
        tokenListProto.toggle = function(token, force) {
            token += '';
            
            var result = this.contains(token),
                method = result ?
                    force !== true && 'remove' :
                    force !== false && 'add';
            
            if (method) {
                this[method](token);
            }
            
            if (force === true || force === false) {
                return force;
            } else {
                return !result;
            }
        };
        
        tokenListProto.toString = function() {
            return this.join(' ');
        };
        
        if (objCtr.defineProperty) {
            var defineProperty = function(object, property, definition) {
                if (definition.get || definition.set) {
                    objCtr.defineProperty(object, property, definition);
                } else {
                    object[property] = definition.value;
                }
            };
            
            try {
                defineProperty(elemCtrProto, classListProp, {
                    get: function() {
                        return new DOMTokenList(this);
                    },
                    enumerable: true,
                    configurable: true
                });
            } catch (ex) {
                if (ex.number === -0x7FF5EC54) {
                    defineProperty(elemCtrProto, classListProp, {
                        value: function() {
                            return new DOMTokenList(this);
                        },
                        enumerable: true,
                        configurable: true
                    });
                }
            }
        }
    }(window));
}

console.log('✅ Safari兼容性Polyfills加载完成');
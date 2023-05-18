/* <script type="text/javascript" src="http://127.0.0.1:10086/hook.js"></script> */

console.log("当前的函数有")

function isNative(fn) {
	// return (/\{\s*\[native code\]\s*\}/).test('' + fn);
    // return eval(fn + ".toString().indexOf('[native code]') != -1");
    return false;
}

var doNotHookArray = [
    '__core-js_shared__',
    'requestAnimationFrame',
    'clearInterval',
    'setInterval'
]

function hookAllFunction(caijiObj, objStr, flag) {
    // debugger;
    if (window.Object.keys(caijiObj).length){
        window.Object.keys(caijiObj).forEach(
            (elem, index) => {
                // console.log(index, elem, typeof (eval(elem)))
                // console.log(objStr, elem);
                // if (doNotHookArray.indexOf(elem) == -1) {
                if (elem.indexOf('-') == -1 && elem.indexOf('@') == -1 && doNotHookArray.indexOf(elem) == -1) {
                    if (typeof (eval(objStr + elem)) == "function") {
                        if (isNative(objStr + elem)) {
                            // console.log(objStr + elem, "()是原生func，不hook");
                        } else if (objStr + elem == 'window.onload') {
                            if (flag == 1){
                                console.log("函数", elem, "hook该函数，在页面加载完成时再hook一次！");
                                var hookIt = "var _oldFunc = " + objStr + elem + ";" +
                                    objStr + elem + " = function(){" +
                                    "hookAllFunction(window, 'window.', 2);" +
                                    "console.log('开始执行', " + objStr + elem + ");" +
                                    "console.log('参数：', arguments);" +
                                    "let result = _oldFunc.apply(this, arguments);" +
                                    "console.log('执行结束', " + objStr + elem + ");" +
                                    "console.log('结果：', result);" +
                                    "return result;" +
                                    "}";
                                eval(hookIt);
                                console.log(objStr + elem, "已被hook!");
                            }
                        } else {
                            if (flag == 2){
                                console.log("函数", elem);
                                var hookIt = "var _oldFunc = " + objStr + elem + ";" +
                                    objStr + elem + " = function(){" +
                                    "console.log('开始执行', " + objStr + elem + ");" +
                                    "console.log('参数：', arguments);" +
                                    "let result = _oldFunc.apply(this, arguments);" +
                                    "console.log('执行结束', " + objStr + elem + ");" +
                                    "console.log('结果：', result);" +
                                    "return result;" +
                                    "}";
                                eval(hookIt);
                                console.log(objStr + elem, "已被hook!");
                            }
                        }
                    } else if (typeof (eval(objStr + elem)) == "object" && eval(objStr + elem) && !eval(objStr + elem + ' instanceof Array')) {
                        if (eval(objStr + elem) != caijiObj) {
                            // console.log("开始遍历对象", objStr + elem, "的子对象");
                            hookAllFunction(eval(objStr + elem), objStr + elem + ".");
                        }
                    }
                }
            }
        )
    }
}

hookAllFunction(window, "window.", 1)

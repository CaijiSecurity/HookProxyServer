/* <script type="text/javascript" src="http://127.0.0.1:10086/hook.js"></script> */

console.log("当前的函数有")

function hookAllFunction(caijiObj, objStr) {
    // debugger;
    window.Object.keys(caijiObj).forEach(
        (elem, index) => {
            // console.log(index, elem, typeof (eval(elem)))
            if (typeof (eval(objStr + elem)) == "function") {
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
            } else if (typeof (eval(objStr + elem)) == "object" && eval(objStr + elem)) {
                if (eval(objStr + elem) != caijiObj) {
                    console.log("开始遍历对象", objStr + elem, "的子对象");
                    hookAllFunction(eval(objStr + elem), objStr + elem + ".");
                }
            }
        }
    )
}

hookAllFunction(window, "window.")

// (function() {
//     // 保存原始方法
//     window.__cr_fun = window.Function;
//     // 重写 function
//     var myfun = function() {
//         var args = Array.prototype.slice.call(arguments, 0, -1).join(","),
//             src = arguments[arguments.length - 1];
//         console.log(src);
//         console.log("=============== Function end ===============");
//         debugger;
//         return window.__cr_fun.apply(this, arguments);
//     }
//     // 屏蔽js中对原生函数native属性的检测
//     myfun.toString = function() {
//         return window.__cr_fun + ""
//     }
//     Object.defineProperty(window, 'Function', {
//         value: myfun
//     });
// })();
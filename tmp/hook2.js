_Object = Object;

Object = function () {
    console.log("开始");
    let result = _Object.apply(this, arguments);
    console.log("新对象：", result);
    console.log("结束");
    return result;
}

_Object.getOwnPropertyNames(_Object).forEach(function (key) {
    console.log(key, typeof (key));
    eval('Object.' + key + ' = ' + '_Object.' + key);
    console.log('已赋值！');
});

// var a = {}
// _Object2 = a.constructor

// a.constructor = function () {
//     console.log("开始");
//     let result = _Object2.apply(this, arguments);
//     console.log("新对象：", result);
//     console.log("结束");
//     return result;
// }

// _Object2.getOwnPropertyNames(_Object2).forEach(function (key) {
//     console.log(key, typeof (key));
//     eval('a.constructor.' + key + ' = ' + '_Object2.' + key);
//     console.log('已赋值！');
// });

_Function = Function;

Function = function () {
    console.log("开始");
    let result = _Function.apply(this, arguments);
    console.log("新函数：", result);
    console.log("结束");
    return result;
}

console.log("Object已被hook");
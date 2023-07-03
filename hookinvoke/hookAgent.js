var hookInvokeTask;

function hookAgentPush(url, method, data) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url + "?retData=" + data, true);

    xhr.onload = () => { };
    xhr.send();
}


function hookAgentGet(url, method, callBack) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);

    xhr.onload = () => {
        let tmpData = xhr.responseText;
        callBack(tmpData);
    };
    xhr.send();
}


function loopTask(targetFuncs) {
    let resultDate;
    hookAgentGet(
        "http://127.0.0.1:8992/get",
        "GET",
        (tmpData) => {
            resultDate = tmpData;
            for (const func of targetFuncs) {
                resultDate = func(resultDate);
            }
            console.log(resultDate);
            hookAgentPush("http://127.0.0.1:8992/push", "GET", resultDate);
        }
    );
}

// 开始轮训
function startHookInvoke(targetFuncs) {
    hookInvokeTask = setInterval(loopTask, 500, targetFuncs);
}

function stopHookInvoke() {
    clearInterval(hookInvokeTask);
}

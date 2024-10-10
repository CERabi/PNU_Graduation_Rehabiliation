window.addEventListener("load", begin, false)


let dev_names = []
let dev_addrs = []
let dev_onlines = []

/* ----- Functions ----- */

// 장치 목록 불러오기
function get_device_information(){
    dev_names = []
    dev_addrs = []
    
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
            received = JSON.parse(this.responseText)
            if (received.type=="data"){
                dev_names = received.dev_names;
                dev_addrs = received.dev_addrs;
                // 장치 목록 element 가져옴
                let dev_list = document.getElementById("dev_list");
                for(let i in dev_names){
                    let div_dev = document.createElement("div");
                    div_dev.setAttribute("class","dev");

                    let span_isonline = document.createElement("span");
                    span_isonline.setAttribute("class","dev_isonline");

                    let span_addr = document.createElement("span");
                    span_addr.setAttribute("class","dev_addr");
                    span_addr.appendChild(document.createTextNode(dev_addrs[i]));

                    let span_name = document.createElement("span");
                    span_name.setAttribute("class","dev_name");
                    span_name.appendChild(document.createTextNode(dev_names[i]));
                    
                    div_dev.appendChild(span_isonline);
                    div_dev.appendChild(span_name);
                    div_dev.appendChild(span_addr);

                    dev_list.appendChild(div_dev);
                }
            }
            else{
                add_alarm(received.type, received.message);
            }
        }
    }
    xhr.open("GET","http://localhost:8000/devices",true);
    xhr.send();
}

// 장치 상태 스캔
function dev_scan(){
    add_alarm("message", "장치 상태를 불러옵니다");

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
            received = JSON.parse(this.responseText)
            if (received.type=="data"){ // 성공적
                add_alarm("complete","장치 상태를 불러왔습니다.")
                dev_onlines = received.dev_online;
                
                // 장치 목록 element 가져옴
                let dev_list = document.getElementsByClassName("dev");
                // 상태 업데이트
                for(let i in dev_onlines){
                    let onoff = dev_list[i].firstChild;
                    if(dev_onlines[i] == true){
                        onoff.setAttribute("class","dev_isonline on")
                    }
                    else{
                        onoff.setAttribute("class", "dev_isonline")
                    }
                }
            }
            else{ //실패
                add_alarm(received.type, received.message);
            }
        }
    }
    let senddata = {
        dev_list : dev_addrs
    }
    xhr.open("POST","http://localhost:8000/scan",true);
    xhr.setRequestHeader('Content-type', 'application/json');
    xhr.send(JSON.stringify(senddata));
}

//자세 추론
function dev_predict(){
    document.getElementById("show_example").style.display = "block";

    
}

//알람 추가하기
function add_alarm(msgtype, msg){
    let alarm_list = document.getElementById("alarm_list");

    let div_alarm = document.createElement("div");
    if (msgtype=="exception"){
        div_alarm.setAttribute("class","alarm exception");
    }
    else if (msgtype=="complete"){
        div_alarm.setAttribute("class","alarm complete");
    }
    else{
        div_alarm.setAttribute("class","alarm");
    }
    let btn_removealarm = document.createElement('button');
    btn_removealarm.setAttribute("class","btn_removealarm");
    btn_removealarm.setAttribute("onclick","remove_alarm(this)");
    btn_removealarm.appendChild(document.createTextNode("X"));

    let span_msg = document.createElement("span");
    span_msg.appendChild(document.createTextNode(msg));

    div_alarm.appendChild(btn_removealarm);
    div_alarm.appendChild(span_msg);

    alarm_list.appendChild(div_alarm);
}

/* ----- Event ----- */

// 버튼 이벤트
function remove_alarm(e){
    //e는 버튼 오브젝트
    e.parentNode.remove()
}
function btn_scan(){
    dev_scan()
}
function btn_predict(){
    dev_predict()
}




function begin(){

    get_device_information();
}




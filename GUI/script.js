window.addEventListener("load", begin, false);


let dev_names = [];      // 전체 센서
let dev_addrs = [];      // 전체 센서 주소
let dev_names_to_addrs = {}; // 센서 이름:센서 주소 매칭
let dev_onlines = [];    // 전체 센서 상태
let dev_now_online = [];// 현재 online 센서 이름

/* ----- Functions ----- */

// 장치 목록 불러오기
function get_device_information() {
    dev_names = [];
    dev_addrs = [];
    dev_names_to_addrs = {};

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            received = JSON.parse(this.responseText);
            if (received.type == "data") {
                dev_names = received.dev_names;
                dev_addrs = received.dev_addrs;
                
                // 장치 목록 element 가져옴
                let dev_list = document.getElementById("dev_list");
                for (let i in dev_names) {
                    dev_names_to_addrs[dev_names[i]] = dev_addrs[i]; 

                    let div_dev = document.createElement("div");
                    div_dev.setAttribute("class", "dev");

                    let span_isonline = document.createElement("span");
                    span_isonline.setAttribute("class", "dev_isonline");

                    let span_addr = document.createElement("span");
                    span_addr.setAttribute("class", "dev_addr");
                    span_addr.appendChild(document.createTextNode(dev_addrs[i]));

                    let span_name = document.createElement("span");
                    span_name.setAttribute("class", "dev_name");
                    span_name.appendChild(document.createTextNode(dev_names[i]));

                    div_dev.appendChild(span_isonline);
                    div_dev.appendChild(span_name);
                    div_dev.appendChild(span_addr);

                    dev_list.appendChild(div_dev);
                }
            }
            else {
                add_alarm(received.type, received.message);
            }
        }
    }
    xhr.open("GET", "http://localhost:8000/devices", true);
    xhr.send();
}

// 장치 상태 스캔
function dev_scan() {
    add_alarm("message", "장치 상태를 불러옵니다");
    dev_now_online = [] // 기존 목록 초기화(필요한 변수)

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            received = JSON.parse(this.responseText)
            if (received.type == "data") { // 성공적
                add_alarm("complete", "장치 상태를 불러왔습니다.")
                dev_onlines = received.dev_online;

                // 장치 목록 element 가져옴
                let dev_list = document.getElementsByClassName("dev");
                // 상태 업데이트
                for (let i in dev_onlines) {
                    let onoff = dev_list[i].firstChild;
                    if (dev_onlines[i] == true) {
                        onoff.setAttribute("class", "dev_isonline on")
                        dev_now_online.push(dev_names[i])
                    }
                    else {
                        onoff.setAttribute("class", "dev_isonline")
                    }
                }
            }
            else { //실패
                add_alarm(received.type, received.message);
            }
        }
    }
    let senddata = {
        dev_list: dev_addrs,
        pos: "none"
    }
    xhr.open("POST", "http://localhost:8000/scan", true);
    xhr.setRequestHeader('Content-type', 'application/json');
    xhr.send(JSON.stringify(senddata));
}

//자세 추론
function dev_predict() {
    // 선택한 자세 읽음
    let position = document.getElementById("sel_rehab").value;
    // 설명창 변경
    document.getElementById("show_example").style.display = "block";
    document.getElementById("pos_title").textContent = position_title[position];
    document.getElementById("pos_description").innerHTML = position_description[position];

    // 선택한 자세에 맞는 센서가 있는지 확인
    let not_online = []
    for(let s of position_essential_sensor[position]){
        if (!dev_now_online.includes(s)){
            not_online.push(s)
        }
    }
    if (not_online.length != 0){
        document.getElementById("status_str").textContent = "필요한 센서를 모두 연결해주세요. 없음:" + not_online.toString();
        return;
    }
    document.getElementById("status_str").textContent = "센서 연결 중...";

    // 필요한 센서들 주소 가져오기
    let connect_addrs = position_essential_sensor[position].map(function(e){
        return dev_names_to_addrs[e];
    })
     
    // predict_start 호출
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let received = JSON.parse(this.responseText);
            add_alarm(received.type, received.message)
        }
    }
    let senddata = {
        dev_list: connect_addrs,
        pos: position
    }
    xhr.open("POST", "http://localhost:8000/predict_start", true);
    xhr.setRequestHeader('Content-type', 'application/json');
    xhr.send(JSON.stringify(senddata));

    // predict_get 호출
    let xhr2 = new XMLHttpRequest()
    xhr2.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let received = JSON.parse(this.responseText);
            // 추론이 끝나 응답을 받는 경우
            if(received.type == "complete" && received.message == "wait_end"){
                add_alarm(received.type, "자세 추론을 시작합니다.");
                show_predict();
            }
            else{
                add_alarm(received.type, received.message);
            }
        }
    }
    xhr2.open("GET", "http://localhost:8000/predict_get", true);
    setTimeout(xhr2.send(),1000);
}

// 자세추론 중에 결과 확인하기
function show_predict(){
    //시간 경과
    let ellapsed = 0;
    let result_time = document.getElementById("result_time");

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let received = JSON.parse(this.responseText);
            if(received.type == "data"){
                //add_alarm(received.type, received.predict_result)
                result_time.textContent = ellapsed.toString();
            }
            else{
                // 정지
                add_alarm(received.type, received.message)
                window.clearInterval(timer)
            }
        }
    }
    
    var timer = window.setInterval(function(){
        xhr.open("GET", "http://localhost:8000/predict_get", true);
        xhr.send();
        ellapsed += 1;
    }, 1000)
}



//알람 추가하기
function add_alarm(msgtype, msg) {
    let alarm_list = document.getElementById("alarm_list");

    let div_alarm = document.createElement("div");
    if (msgtype == "exception") {
        div_alarm.setAttribute("class", "alarm exception");
    }
    else if (msgtype == "complete") {
        div_alarm.setAttribute("class", "alarm complete");
    }
    else {
        div_alarm.setAttribute("class", "alarm");
    }
    let btn_removealarm = document.createElement('button');
    btn_removealarm.setAttribute("class", "btn_removealarm");
    btn_removealarm.setAttribute("onclick", "remove_alarm(this)");
    btn_removealarm.appendChild(document.createTextNode("X"));

    let span_msg = document.createElement("span");
    span_msg.appendChild(document.createTextNode(msg));

    div_alarm.appendChild(btn_removealarm);
    div_alarm.appendChild(span_msg);

    alarm_list.appendChild(div_alarm);
}

/* ----- Event ----- */

// 버튼 이벤트
function remove_alarm(e) {
    //e는 버튼 오브젝트
    e.parentNode.remove()
}
function btn_scan() {
    dev_scan()
}
function btn_predict() {
    dev_predict()
}

function begin() {
    get_device_information();
}


//..
const position_title = {
    "shoulder": "Assisted shoulder flexion",
    "hamstring": "Hamstring stretch",
    "neck": "Neck side extension",
    "bridge": "Bridge stretch"
};
const position_description = {
    "shoulder":
    "0. 필요한 센서: B(왼손목) C(오른손목) F(배꼽) <br>\
    1. 양 손을 깍지끼고 양팔을 아래로 뻗습니다.<br>\
    2. 5초 동안 양 팔을 편 채 위로 올립니다.<br>\
    3. 다음 5초 동안 아래로 내립니다.<br>\
    4. 총 10회 반복합니다.<br>",

    "hamstring": 
    "0. 필요한 센서: F(배꼽) G(무릎 위) H(발목 위) \
    1. 의자에 앉아 허리를 곧게 폅니다. <br>\
    2. 5초간 (왼쪽) 종아리를 서서히 폅니다. <br>\
    3. 다음 5초간 (왼쪽) 종아리를 서서히 내립니다.<br>\
    4. 총 10회 반복합니다.<br>",

    "neck":
    "0. 필요한 센서: A, B \
    1. 바른 자세를 유지합니다.<br>\
    2. 목에 힘을 풀고, 한 손을 들어 반대편 머리를 잡고 당깁니다. <br>\
    3. 목을 꺾어버리진 마세요.<br>",

    "bridge":
    "0. 필요한 센서: A, B \
    1. 바른 자세를 유지합니다.<br>\
    2. 목에 힘을 풀고, 한 손을 들어 반대편 머리를 잡고 당깁니다. <br>\
    3. 목을 꺾어버리진 마세요.<br>"
}
const position_essential_sensor =
{
    "shoulder": ["B","C","F"],
    "hamstring": ["F","G","H"],
    "neck": ["A","B"],
    "bridge": ["A","B","C","D","E"]
};
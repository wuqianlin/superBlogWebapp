/**
 * Created by Administrator on 2016-04-19.
 */
//ApiUrl = 'http://www.h5api.com/';

 var ishttps = 'https:' == document.location.protocol ? true: false;
 if(ishttps){
        ApiUrl = 'https://h5api.api.guxiansheng.cn/';
        ApiLogin = 'https://login.api.guxiansheng.cn/';
        ApiContent = 'https://content.api.guxiansheng.cn/';
        ApiGuJi = 'https://clb.api.guxiansheng.cn/';
        ApiMember = 'https://u.api.guxiansheng.cn/';
        ApiSeller = 'https://seller.api.guxiansheng.cn/';
        ApiGeGu = 'https://mk.api.guxiansheng.cn/';
        PdfUrl  = 'https://pdf.guxiansheng.cn/';
        ApiTps = 'https://tps.api.guxiansheng.cn/';
        H5Url = 'https://h5.api.guxiansheng.cn/';
 }else{
        ApiUrl = 'http://h5api.api.guxiansheng.cn/';
        ApiLogin = 'http://login.api.guxiansheng.cn/';
        ApiContent = 'http://content.api.guxiansheng.cn/';
        ApiGuJi = 'http://clb.api.guxiansheng.cn/';
        ApiMember = 'http://u.api.guxiansheng.cn/';
        ApiSeller = 'http://seller.api.guxiansheng.cn/';
        ApiGeGu = 'http://mk.api.guxiansheng.cn/';
        PdfUrl  = 'http://pdf.guxiansheng.cn/';
        ApiTps = 'http://tps.api.guxiansheng.cn/';
        H5Url = 'http://h5.api.guxiansheng.cn/';
 }


/*member_id = 169;
key = '9d9e023afc25351777c1f67f2b87b6a3';*/

member_id = GetQueryString("member_id");
key = GetQueryString("key");

function jsonp(url,callback,type,data){

    $.ajax({
        url:url,    //请求的url地址
        dataType:"jsonp",   //返回格式为json
        data:data,    //参数值{a:2,b:c}
        type:type,   //请求方式post get
        jsonp:'callback',
        jsonpCallback:callback
    });
}


function GetQueryString(name){
    var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r!=null) return unescape(r[2]); return null;
}


/**
 * 格式化数字,四舍五入
 * str 需要格式的数字
 * n 保留几位小数
 * f 是否要进行单位转化 大于0则转化
 * */
function formatNumber(str,n,f){
    var currnum = Number(str);
    if(currnum>=0){
        var symbol = '';
    }else{
        var symbol = '-';
        currnum = Math.abs(currnum);
    }
    var unit = '';
    if(currnum){
        if (f > 0) {
            if (currnum > 100000000) {
                currnum = currnum / 100000000;
                unit = '亿';
            } else if (currnum > 10000) {
                currnum = currnum / 10000;
                unit = '万';
            }
        }
        var renum = currnum.toFixed(n);
    }else{
        var renum = '0.';
        for(var i=0;i<n;i++){
            renum+='0';
        }
    }
    return symbol+renum+unit;
}



function check_is_login(){
    var member_id = GetQueryString('member_id');
    var key = GetQueryString('key');
//    if(member_id != 'null' && member_id != undefined && member_id != 0 && member_id != '' && key != 'null' && key != undefined && key != 0 && key != ''){
    if(member_id != 'null' && member_id != undefined && member_id != 0 && member_id != ''){
        return true;
    }else{
        return false;
    }



}


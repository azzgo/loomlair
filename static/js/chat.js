// 查询消息
var message_find = function(){
  var msg;
  $.get('/chat/get/', function(data){
    msg = data.msg;
    flash_msg(msg);
  },'json');
};

// 添加消息到box
var flash_msg = function(msg){
  for(var i=0; i<msg.length; i++){
    if(msg[i].nickname===$("#nickname").text()){
      $('#chat-content').append(nano("<div class='other-msg'><p class='other-content'>{content}</p><p class='puber'>{pub_time} by {nickname}</p></div>", msg[i]));
    }else{
      $('#chat-content').append(nano("<div class='mine-msg'><p class='mine-content'>{content}</p><p class='puber'>{pub_time} by {nickname}</p></div>", msg[i]));
    }
  }
};

// # 在线用户查询
var userlist_find = function(){
  var user_list;
  $.get('/chat/userlist/get/', function(data){
    user_list = data.userlist;
    flash_user(user_list);
  });
};

// # 添加用户到box
var flash_user = function(user_list){
  $('#user-list-content').html('');
  for (var i=0; i< user_list.length;i++){
    $('#user-list-content').append(nano("<p class='user-item'>{nickname}</p>", user_list[i]));
  }
};

// 定时查询新消息
$(document).ready(function(){
  message_find();
  userlist_find();
  setInterval('message_find()', 15000);
  setInterval('userlist_find()', 1200000);
});

$('#message-sending').click(function(){
  var message = $('#message-text').val();
  if (message === ''){
    return false;
  }

  $.post('/chat/add/', {'message': message}, function(){
    console.log('成功');
    $("#message-text").val('');
    message_find();
  });
});

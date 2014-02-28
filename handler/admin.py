#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated
from tornado.escape import json_encode, json_decode
from base import BaseHandler, authenticated, catch_exception
from lib import util


class AdminHandler(BaseHandler):
    pass
    """
    --- 1 ---
    <li class="myMessagePartList">
        <!-- 管理员提交全站公告之后触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">站内公告</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief">梧桐已推出了 <a href="#">梧桐阅读(ver3.141)</a> Android客户端，您可以点击 <a href="#">这里</a> 获取更多信息 </div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- 加入小组之后触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">加入小组</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief">您已加入小组 <a href="/g/1">PANTERA</a> ，点击 <a href="#">这里</a> 了解更多关于梧桐小组的信息</div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- 当组长任命“我”时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">组长任命</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief">您已被 <a href="/g/1">思存工作室养老院</a> 小组组长提议担任该小组新一任组长，<a href="#"> 同意 </a> | <a href="#"> 拒绝 </a></div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- 当组长任命“我”时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">小组管理员任命</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief">您已被 <a href="/g/1">思存工作室养老院</a> 小组组长提议担任该小组管理员，<a href="#"> 同意 </a> | <a href="#"> 拒绝 </a></div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- 当“我”被组长移除时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">退出小组</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief">您已被 <a href="/g/1">Eagles</a> 小组管理员移除该小组</div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- “我”主动退出小组时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">退出小组</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief">您已退出 <a href="/g/1">Rammstein</a> 小组</div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- 他人接受了“我”的会话邀请时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">会话邀请</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief"><a href="/user/flyMonster">flyMonster</a> 已接受了您的会话邀请，现在您可以点击<a href="#"> 这里 </a>与Ta开始聊天</div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- 他人拒绝了“我”的会话邀请时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">会话邀请</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief"><a href="/user/flyMonster">flyMonster</a> 已拒绝了您的会话邀请</div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- 他人向"我"发出会话邀请时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">会话邀请</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief"><a href="/user/flyDog">flyDog</a> 向您发起了会话邀请， <a href="#"> 同意</a> | <a href="#">拒绝</a> </div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- 被他人关注时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">关注</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief"><a href="/user/flyDog">flyCat</a> 关注了您，您的推送作品将会第一时间推送至Ta</div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- 关注了某人时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">关注</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief">您关注了 <a href="/user/flyDog">flyFox</a>，现在您可以第一时间在 消息-推送 中得到Ta的推送作品</div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- ”我“的作品被管理员删除时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">作品删除</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief">很遗憾，由于您的作品 <a href="#">像少年啦，飞驰</a> 涉嫌版权问题，梧桐已移除该作品，您也受到一次警告。在使用梧桐的过程中请务必遵守<a href="#">梧桐指南</a></div>
        </div>
    </li>
    <li class="myMessagePartList">
        <!-- ”我“的作品被梧桐管理员判定为优秀作品时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">头衔授予</div>
            <div class="myMessageUserName"><a href="#">Wutong</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief">由于您在作品 <a href="#">麦田里的守望者</a> 中的精彩表现，梧桐授予您 <a href="#">梧桐特殊贡献者 </a>的头衔，并将该作品摘录在 <a href="#">梧桐年鉴</a> 中，在此我们向您表示祝贺</div>
        </div>
    </li>

    --- 2 ---
    <li class="myMessagePartList">
        <!-- 他人在底评中@”我“并提交底评时触发 -->
        <div href="#" class="myMessagePartInline">
            <img class='myMessageUserImage' src="" />
            <div class="myMessageAddress">在 <a href="#">关于莉莉周的一切</a> 里提到我</div>
            <div class="myMessageUserName"><a href="#">flyCat</a></div>
            <div class="myMessageTime">10-23 20:56</div>
            <div class="myMessagBrief"><a href="#">@loggerhead 跟你说过是这篇啦...</a></div>
        </div>
    </li>
    """

# coding:utf-8
import sys
import os

user = {"name": "", "is_login": False, "is_admin": False}


def login_confirm(func):
    def wrap(*args, **kwrgs):
        if user["is_login"]:
            func(*args, **kwrgs)
        else:
            print("未登录")
        return func

    return wrap


def admin_confirm(func):
    def wrap(*args, **kwrgs):
        if user["is_admin"]:
            func(*args, **kwrgs)
        else:
            print("没有权限")
        return func

    return wrap


def index():
    print("This page is for everyone")


@login_confirm
def usr():
    print("This is user page!")


@login_confirm
@admin_confirm
def admin():
    print("This is admin page!")


if __name__ == "__main__":
    while True:
        print("(1) 访问首页　(2) 登录 (3) 用户界面 (4)管理员 (q)退出\n")
        num = input("请输入对应数字：")
        if num == "q":
            sys.exit(0)
        if num == "1":
            index()
        elif num == "2":
            name = input("请输入你的名字：")
            if name == "admin":
                user["name"] = name
                user["is_login"] = True
                user["is_admin"] = True
            else:
                user["name"] = name
                user["is_login"] = True
        elif num == "3":
            usr()
        elif num == "4":
            admin()
        else:
            print("错误的选项")
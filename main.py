#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import random
import sys

from PyQt5.QtCore import Qt, QTimer, QVariant
from PyQt5.QtGui import QImage, QPixmap, QCursor, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDesktopWidget, QMenu, qApp, QAction, QSystemTrayIcon

from config import PETS_PATH

pets = []


class MyMikuPet(QWidget):
    def __init__(self, pet_name):
        super().__init__()
        quit = QAction("退出", self, triggered=os._exit)
        quit.setIcon(QIcon("sys_img/icon.png"))
        self.pet = DeskPet(pet_name)
        pets.append(self.pet)
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(quit)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon("sys_img/icon.png"))
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.show()


class DeskPet(QWidget):

    def __init__(self, pet_name):
        super().__init__()
        # self.drag = False
        # self.position = 0
        self.timer = QTimer()
        self.context_menu = QMenu(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.repaint()
        self.pet_name = pet_name
        # 当前循环的图片的索引
        self.index = 0
        # 设置初始宠物的图片
        self.conf = self.get_pet_config_info()
        self.img = QLabel(self)
        self.resize(300, 300)
        self.appear()

        # 当前动作的保持时间
        self.action_duration_time = 0

        # 当前循环图片切换的时间
        self.frame_refresh = 0
        self.default_action()
        self.init_menu()

        self.show()

    def default_action(self):
        # 设置默认动作
        # 设置定时器

        img = QImage()
        action_name = 'default'

        # 设置第一张图
        act_pic_name = self.conf.get(action_name).get("images")
        action_pic_path = self.get_action_pic_path(act_pic_name)
        print(action_pic_path)
        img.load(action_pic_path)
        self.img.setPixmap(QPixmap.fromImage(img))
        self.set_action_timer(action_name)

    def set_action_timer(self, action_name):
        print("设置新动作")
        frame_refresh = self.conf.get(action_name).get("frame_refresh")
        self.frame_refresh = frame_refresh
        self.action_duration_time = 0
        # 设置定时器
        self.timer.timeout.connect(lambda: self.set_action(action_name))
        self.timer.start(int(self.frame_refresh * 1000))

    def cancel_timer(self):
        if self.timer is not None and self.timer.isActive():
            self.timer.stop()
            self.timer.timeout.disconnect()
            print("定时器已取消")

    def get_pet_path(self):
        return os.path.join(r"pet", self.pet_name)

    def get_pet_config_info(self):
        pic_path = self.get_pet_path()
        act_conf = os.path.join(pic_path, "act_conf.json")
        with open(act_conf, mode='r', encoding='utf-8') as f:
            return json.load(f)

    def get_action_pic_path(self, act_pic_name):
        action_pic = f"{act_pic_name}_{self.index}"
        img_path = os.path.join(self.get_pet_path(), "action", action_pic) + ".png"
        img_path = img_path.replace('\\', '\\\\')
        return img_path

    def set_action(self, action_name):
        self.action_duration_time += self.frame_refresh
        act_num = self.conf.get(action_name).get("act_num")
        act_pic_name = self.conf.get(action_name).get("images")
        img = QImage()
        img_path = self.get_action_pic_path(act_pic_name)

        if not os.path.exists(img_path):
            self.index = 0

        img.load(img_path)
        self.img.setPixmap(QPixmap.fromImage(img))
        if self.index < act_num:
            self.index += 1
        else:
            self.index = 0
        # # 获取屏幕坐标

        # # 获取窗口坐标和尺寸
        window = self.geometry()

        frame_move = self.conf.get(action_name).get("frame_move")

        if action_name == "left_walk":
            self.move(window.x() - frame_move, window.y())
            if self.action_duration_time > 5:
                self.cancel_timer()
                self.set_action_timer("right_walk")
        if action_name == "right_walk":
            self.move(window.x() + frame_move, window.y())
            if self.action_duration_time > 5:
                self.cancel_timer()
                self.set_action_timer("left_walk")

    def init_menu(self):
        # 鼠标右键后的菜单栏
        switch_action_menu = QMenu('选择动作', self)
        switch_role_menu = QMenu('切换角色', self)
        add_role_menu = QMenu('新增角色', self)

        for pet in os.listdir(PETS_PATH):
            data = {
                "event": "switch_role",
                "key": pet
            }
            switch_role_menu.addAction(pet).setData(data)

            data = {
                "event": "add_role",
                "key": pet
            }
            add_role_menu.addAction(pet).setData(data)

        for k, c in self.conf.items():
            if c.get("desc"):
                action = switch_action_menu.addAction(c.get("desc"))
                data = {
                    "event": "action",
                    "key": k
                }
                action.setData(QVariant(data))

        self.context_menu.addMenu(switch_action_menu)
        self.context_menu.addMenu(switch_role_menu)
        self.context_menu.addMenu(add_role_menu)

    def appear(self):
        self.setWindowTitle('Move to Bottom Left')

        # 获取屏幕和窗口的几何尺寸
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        random_number_x = random.randint(size.width(), int((screen.width() - size.width()) / 2))
        random_number_y = random.randint(size.height(), int((screen.height() - size.height()) / 2))
        # 计算窗口应该移动到的左下角位置
        x = screen.width() - random_number_x  # 右边对齐
        y = screen.height() - random_number_y  # 垂直居中

        # 移动窗口到计算的位置
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos() - self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def contextMenuEvent(self, event):
        # 鼠标右击事件触发
        action = self.context_menu.exec_(self.mapToGlobal(event.pos()))
        if not action:
            return

        self.analysis(action)

    def analysis(self, action):
        global pets
        event = action.data().get("event")
        key = action.data().get("key")
        print(f"用户选择动作解析:{event}")
        # 切换动作
        if event == "action":
            self.cancel_timer()
            self.set_action_timer(key)
        elif event == "add_role":
            pets.append(DeskPet(key))
        elif event == "switch_role":
            self.cancel_timer()
            index = pets.index(self)
            pets.append(DeskPet(key))
            pets.pop(index)
            self.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = MyMikuPet("miku")
    sys.exit(app.exec_())

from PIL import Image,ImageFilter,ImageEnhance
import numpy as np
import pygame,easygui
import sys

first = easygui.buttonbox(msg='欢迎使用轻修图', title='轻修图', choices=('开始修图', '退出'),image="qxt.ico")
if first == "退出":
    sys.exit()

class ImageColorAdjuster:
    # 轻修图 - 专业调色功能类
    def __init__(self, image_path=None, pil_image=None):
        # 初始化调色器
        if pil_image is not None:
            self.im = pil_image.copy()  # 使用传入的PIL图像
        elif image_path is not None:
            self.im = Image.open(image_path).convert('RGB')  # 统一转为RGB
        else:
            raise ValueError("必须提供image_path或pil_image参数之一")
        # 保存原始图像副本，用于重置
        self.original = self.im.copy()
    def reset(self):
        # 重置为原始图像
        self.im = self.original.copy()
        return self.im
    
    def save(self, path):
        # 保存当前图像
        self.im.save(path)
        print(f"图像已保存至: {path}")
    
    def show(self):
        # 显示当前图像
        self.im.show()
    
    # 基础调整功能
    def adjust_brightness(self, factor):
        # 调整亮度
        enhancer = ImageEnhance.Brightness(self.im)
        self.im = enhancer.enhance(factor)
        return self.im
    
    def adjust_contrast(self, factor):
        # 调整对比度
        enhancer = ImageEnhance.Contrast(self.im)
        self.im = enhancer.enhance(factor)
        return self.im
    
    def adjust_saturation(self, factor):
        # 调整饱和度
        enhancer = ImageEnhance.Color(self.im)
        self.im = enhancer.enhance(factor)
        return self.im
    
    def adjust_sharpness(self, factor):
        # 调整锐度
        enhancer = ImageEnhance.Sharpness(self.im)
        self.im = enhancer.enhance(factor)
        return self.im
    
    def adjust_hue(self, delta): # 调整色调（基于HSV色彩空间），色调偏移量 (-180到180)
        # 转为HSV色彩空间
        hsv_im = self.im.convert('HSV')
        h, s, v = hsv_im.split()
        # 调整色调
        h_array = np.array(h, dtype=np.uint16)
        h_array = (h_array + delta * 255 // 360) % 255
        h_new = Image.fromarray(h_array.astype(np.uint8))
        # 合并回图像
        self.im = Image.merge('HSV', (h_new, s, v)).convert('RGB')
        return self.im
    
    def adjust_temperature(self, warmth): # 调整色温，色温值 (-100到100)
        # 将图像转为数组处理
        img_array = np.array(self.im, dtype=np.float32)
        if warmth > 0:
            # 增加暖色（红、黄通道增强）
            img_array[:, :, 0] *= 1.0 + warmth/200  # 红通道
            img_array[:, :, 1] *= 1.0 + warmth/300  # 绿通道（黄）
        else:
            # 增加冷色（蓝通道增强）
            img_array[:, :, 2] *= 1.0 - warmth/200  # 蓝通道
        # 限制像素值范围
        img_array = np.clip(img_array, 0, 255)
        self.im = Image.fromarray(img_array.astype(np.uint8))
        return self.im
    
    def apply_vignette(self, intensity=0.7): # 应用暗角效果，暗角强度 (0.0-1.0)
        width, height = self.im.size
        img_array = np.array(self.im, dtype=np.float32)
        # 创建渐变遮罩
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        X, Y = np.meshgrid(x, y)
        # 计算径向距离（中心为0，边缘为1）
        R = np.sqrt(X**2 + Y**2)
        mask = 1 - np.clip(R * intensity, 0, 1)
        mask = np.expand_dims(mask, axis=2)  # 扩展维度用于RGB
        # 应用暗角效果
        img_array *= mask
        img_array = np.clip(img_array, 0, 255)
        
        self.im = Image.fromarray(img_array.astype(np.uint8))
        return self.im

# 输入图片路径
path = easygui.fileopenbox(title = "导入")
# 记录修改次数
num = 0

try:
    path2 = path.split("\\")
    length = len(path2)
    # 打开图片
    im = Image.open(path)
    photo_class = im.format # 检测图片类型
except:
    print("输入错误")
    sys.exit()

# 初始化 Pygame
pygame.init()

# 设置窗口尺寸
window_size = (1600,800)
screen = pygame.display.set_mode(window_size)
icon = pygame.image.load('qxt.ico')
pygame.display.set_icon(icon)
screen.fill((50,50,50))

# 设置窗口标题
pygame.display.set_caption("轻修图")
# 渲染字体
font = pygame.font.Font('simsun.ttc',20)
text = font.render('效果 | 调色 | 降噪 | 撤回 | 完成修图', True, (255,255,255))
text_rect = text.get_rect(center=(200,20)) # text_rect = text.get_rect(center=(250,20))

# 主循环标志
running = True

# 主循环
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN: # 按下按键
            x,y = event.pos[0],event.pos[1]
            print(x,y)
            if x >= 20 and x <= 60 and y >= 10 and y <= 40: # 效果
                choicex = easygui.buttonbox(msg='选择效果', title='轻修图', choices=('轮廓图', '浮雕'))
                if choicex == "轮廓图": 
                    im2=im.filter(ImageFilter.CONTOUR)
                elif choicex == "浮雕":
                    im2=im.filter(ImageFilter.EMBOSS)
                else:
                    continue
                num += 1
                save_path = ""
                for i in range(length - 1):
                    save_path = save_path + path2[i] + "\\"
                save_path = save_path + str(num) + "." + photo_class # 计算保存路径
                im2.save(save_path)
                im = im2 # 更新图片以便下一步处理
                path = save_path
            elif x >= 90 and x <= 135 and y >= 10 and y <= 40: # 调色
                mod = easygui.buttonbox(msg='选择调色模式', title='轻修图', choices=('自定义调色','使用预设'))
                if mod == '自定义调色':
                    fix = easygui.multenterbox('调整色彩参数','轻修图',
                                            ["曝光度（标准值为1.0）",
                                            "对比度（标准值为1.0）",
                                            "饱和度（标准值为1.0）",
                                            "锐化（标准值为1.0）",
                                            "色调（-180到180）",
                                            "色温（-100到100）"])
                    try:
                        color_adjuster = ImageColorAdjuster(image_path=path)
                        color_adjuster.adjust_brightness(float(fix[0])) # 曝光度
                        color_adjuster.adjust_contrast(float(fix[1])) # 对比度
                        color_adjuster.adjust_saturation(float(fix[2])) # 饱和度
                        color_adjuster.adjust_sharpness(float(fix[3])) # 锐化
                        color_adjuster.adjust_hue(float(fix[4])) # 色调
                        color_adjuster.adjust_temperature(float(fix[5])) # 色温
                        num += 1
                        #print(num)
                        save_path = ""
                        for i in range(length - 1):
                            save_path = save_path + path2[i] + "\\"
                        save_path = save_path + str(num) + "." + photo_class # 计算保存路径
                        color_adjuster.save(save_path)
                        im = color_adjuster # 更新图片以便下一步处理
                        path = save_path
                        color_adjuster.save(save_path)
                    except:
                        easygui.msgbox("输入错误")
                        continue
                elif mod == '使用预设':
                    fix = easygui.buttonbox(msg='选择预设', title='轻修图', choices=('复古风','电影风','黑白风'))
                    color_adjuster = ImageColorAdjuster(image_path=path)
                    if fix != None:
                        if fix == '复古风':
                            color_adjuster.adjust_brightness(0.9)
                            color_adjuster.adjust_contrast(1.1)
                            color_adjuster.adjust_saturation(0.8)
                            color_adjuster.adjust_temperature(30)
                            color_adjuster.apply_vignette(0.5)
                        elif fix == '电影风':
                            color_adjuster.adjust_brightness(0.95)
                            color_adjuster.adjust_contrast(1.4)
                            color_adjuster.adjust_saturation(1.1)
                            color_adjuster.adjust_sharpness(1.2)
                        elif fix == '黑白风':
                            color_adjuster.adjust_saturation(0.0)  # 完全去色
                            color_adjuster.adjust_contrast(1.3)    # 增强对比度
                        num += 1
                        #print(num)
                        save_path = ""
                        for i in range(length - 1):
                            save_path = save_path + path2[i] + "\\"
                        save_path = save_path + str(num) + "." + photo_class # 计算保存路径
                        color_adjuster.save(save_path)
                        im = color_adjuster # 更新图片以便下一步处理
                        path = save_path
                        color_adjuster.save(save_path)
                    else:
                        continue
                else:
                    continue
            elif x >= 160 and x <= 200 and y >= 10 and y <= 40: # 降噪
                im2=im.filter(ImageFilter.SMOOTH)
                num += 1
                #print(num)
                save_path = ""
                for i in range(length - 1):
                    save_path = save_path + path2[i] + "\\"
                save_path = save_path + str(num) + "." + photo_class # 计算保存路径
                im2.save(save_path)
                im = im2 # 更新图片以便下一步处理
                path = save_path
                easygui.msgbox("已完成一次降噪")
            elif x >= 230 and x <= 270 and y >= 10 and y <= 40: # 撤回
                print("撤回")
                print(num)
                if num > 1:
                    num -= 1
                    save_path = ""
                    for i in range(length - 1):
                        save_path = save_path + path2[i] + "\\"
                    save_path = save_path + str(num) + "." + photo_class # 计算路径
                    im = Image.open(save_path) # 更新图片以便下一步处理
                    path = save_path
            elif x >= 300 and x <= 380 and y >= 10 and y <= 40:
                running = False

    image = pygame.image.load(path)
    w,h = image.get_size()
    image = pygame.transform.scale(image,(w / 4,h / 4))
    screen.blit(image,(20,50))
    screen.blit(text, text_rect)
    pygame.display.update()
# 退出 Pygame
pygame.quit()
easygui.msgbox("已保存  " + path)
import sys
from PIL import Image
import os


#  图片置灰
#  https://blog.csdn.net/wzk4869/article/details/126082728
def imageChange():
    if len(sys.argv) != 3:
        print('error')
        exit(1)
    image_path = sys.argv[1]
    out_path = sys.argv[2]
    # image_path = 'C:\Users\banban\Desktop\image'
    # out_path = 'C:/Users/banban\Desktop/new_image'
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    file_list = os.listdir(image_path)
    input_data = len(file_list)
    print(input_data)
    for file in file_list:
        if file.endswith('.png') or file.endswith('.jpg'):
            image_i = Image.open(os.path.join(image_path, file))
            image_gray = image_i.convert('L')
            print('{} -- success'.format(file))
            image_gray.save(os.path.join(out_path, file), quality=95)  # subsampling=0

    out_data = len(os.listdir(out_path))
    print(out_data)
    if int(input_data) == int(out_data):
        print('gray all success')


if __name__ == '__main__':
    imageChange()

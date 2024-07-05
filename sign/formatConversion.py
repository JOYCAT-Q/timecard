import base64
import numpy as np
import cv2
import requests


# 图片文件content转cv2，并缩放到指定尺寸
def content_to_cv2(contents: list, size: tuple):
    """
    content -> np -> cv2 -> cv2<target_size>
    """
    imgs_np = [np.asarray(bytearray(content), dtype=np.uint8) for content in contents]
    imgs_cv2 = [cv2.imdecode(img_np, cv2.IMREAD_COLOR) for img_np in imgs_np]
    imgs_cv2 = [cv2.resize(img_cv2, size, interpolation=cv2.INTER_LINEAR) for img_cv2 in imgs_cv2]
    return imgs_cv2


def base64_to_content(base64_img: str):
    img_content = base64.b64decode(base64_img)
    return img_content


def base64_to_cv2(img: str):
    # 注：仅适合图像，不适合其它numpy数组，例如bboxs(人脸标注框)的数据
    # base64 -> 二进制 -> ndarray -> cv2
    # 解码为二进制数据
    img_codes = base64.b64decode(img)
    img_np = np.frombuffer(img_codes, np.uint8)
    img_cv2 = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    return img_cv2


def cv2_to_base64(image):
    data = cv2.imencode('.png', image)[1]
    return base64.b64encode(data.tostring()).decode('utf8')


def np_to_base64(array):
    return base64.b64encode(array.tostring()).decode('utf8')


def base64_to_np(arr_b64):
    return np.frombuffer(base64.b64decode(arr_b64), np.float32)


# 显示cv2格式的图像
def cv2_show(img_cv2):
    cv2.imshow('img', img_cv2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 画人脸标注框
def cv2_with_rectangle(img_cv2, bboxs: list):
    """return --> 画好矩形标注框的图像"""
    bboxs = [bbox.astype('int32') for bbox in bboxs]
    for bbox in bboxs:
        cv2.rectangle(
            img_cv2,
            (bbox[0], bbox[1]),
            (bbox[2], bbox[3]),
            (255, 0, 0),  # 蓝色
            thickness=2)
    return img_cv2


# 计算特征向量的余弦相似度
def compare_face(emb1: np.ndarray, emb2: np.ndarray, threshold=0.6):
    """
    @return -> (<numpy.bool>, <numpy.float32>)
    - bool: 是否为同一张人脸
    - float: 余弦相似度[-1, 1]，值越大越相似 \\n
    @params
    - threshold: 判断两张人脸为同一张的余弦相似度阈值
    """
    # return --> 余弦相似度[-1, 1]，值越大，越相似
    sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return sim > threshold, sim


# 百度逆地理编码
# 将经纬度转换为具体城市街道数据
def reverse_geocoding(lng, lat, currentkey):
    """
    lat and lng convert address
    :param lng: longitude
    :param lat: latitude
    :param currentkey: AK
    :return: places_ll
    """
    url = 'http://api.map.baidu.com/reverse_geocoding/v3/?'
    params = {
        "location": str(lat) + ',' + str(lng),
        "output": 'json',
        "ak": currentkey,
        "coordtype": "wgs84ll",
    }
    response = requests.get(url, params=params)
    answer = response.json()
    if answer['status'] == 0:
        tmpList = answer['result']
        return tmpList['formatted_address']
    else:
        return "Error in latitude and longitude resolution, unknown location."

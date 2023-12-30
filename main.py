# 這個程式的用法：
# 1. 首先，確保你已經安裝了必要的 Python 庫，你可以使用以下指令進行安裝：
#    pip install Pillow numpy
# 2. 接著，在終端機中執行此程式，並使用以下指令：
#    python 腳本檔.py --input_file <輸入檔案路徑> --output_path <輸出資料夾路徑>
#    - --input_file：指定輸入的網頁截圖檔案路徑，預設為 'sample.png'。
#    - --output_path：指定輸出裁剪後圖片的資料夾路徑，預設為 'save' 資料夾。
# 3. 程式將讀入網頁截圖，處理後將空白區域裁剪成多張圖片，並保存到指定的輸出資料夾。
# 4. 裁剪完成後，你會在輸出資料夾中看到多張裁剪後的圖片。

from PIL import Image
import numpy as np
import argparse
import os


def find_blank_columns(original_image):
    """
    找到圖像中每一列是否都是空白的區域。

    Parameters:
    - original_image: PIL.Image.Image
        要處理的原始圖像。

    Returns:
    - blank_columns: numpy.ndarray
        布林陣列，表示每一列是否都是空白的區域。
    """
    # 將圖像轉換為NumPy數組
    image_array = np.array(original_image)

    # 將彩色圖像轉換為灰度圖像
    gray_image = np.mean(image_array, axis=-1)

    # 設定空白區域的閾值（這裡假設白色為255）
    blank_threshold = 255

    # 找到整列都是空白的區域
    blank_columns = np.all(gray_image == blank_threshold, axis=1)
    return blank_columns


def find_continuous_false_ranges(boolean_array):
    """
    找到布林陣列中連續的False區域。

    Parameters:
    - boolean_array: list
        布林陣列。

    Returns:
    - false_ranges: list of tuples
        連續的False區域，每個區域用一個元組表示（起始索引，結束索引）。
    """
    false_ranges = []
    current_range = None

    for i, value in enumerate(boolean_array):
        if not value:  # 當遇到 False 時
            if current_range is None:
                current_range = [i, i]
            else:
                current_range[1] = i
        elif current_range is not None:
            # 添加長度檢查
            false_ranges.append(tuple(current_range))
            current_range = None

    # 處理最後一個範圍
    if current_range is not None:
        false_ranges.append(tuple(current_range))
    return false_ranges


def crop_image_by_regions(image, blank_regions, path='save'):
    """
    根據空白區域裁切圖像，並保存裁切後的圖像。

    Parameters:
    - image: PIL.Image.Image
        要裁切的原始圖像。
    - blank_regions: list of tuples
        連續的False區域，每個區域用一個元組表示（起始索引，結束索引）。
    - path: str
        裁切後的圖像保存的路徑。

    Returns:
    - None
    """
    i = 0
    for start, end in blank_regions:
        # 裁切圖像
        cropped_image = image.crop((0, start-1, image.width, end+1))
        cropped_image.save(f'{path}/cropped_image_{i}.png')
        i = i+1
    print("裁切完成，共 "+str(i)+" 張圖片")


def process_short_true_ranges(bool_array, min_true_count=30):
    """
    處理布林陣列中連續的True區域，如果長度小於指定值，則改為False。

    Parameters:
    - bool_array: list
        布林陣列。
    - min_true_count: int
        指定的最小True區域長度。

    Returns:
    - processed_array: list
        處理後的布林陣列。
    """
    processed_array = []
    current_true_count = 0

    for value in bool_array:
        if value:
            current_true_count += 1
        else:
            # 處理連續的 True 區域
            if current_true_count != 0:
                if current_true_count < min_true_count:
                    processed_array.extend([False] * current_true_count)
                else:
                    processed_array.extend([True] * current_true_count)
                current_true_count = 0

            # 添加當前值
            processed_array.append(value)

    # 處理最後一段連續的 True 區域
    if current_true_count != 0:
        if current_true_count < min_true_count:
            processed_array.extend([False] * current_true_count)
        else:
            processed_array.extend([True] * current_true_count)
        current_true_count = 0
    return processed_array


def check_folder(path):
    """
    檢查指定路徑是否存在資料夾，若不存在則創建之。

    參數:
    - path (str): 要檢查和創建的資料夾路徑。
    """
    if not os.path.exists(path):
        print('mkdir ' + path)
        os.mkdir(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Cutting an image into multiple pictures.')
    parser.add_argument('--input_file', type=str,
                        default='sample.png', help='input image file path')
    parser.add_argument('--output_path', type=str,
                        default='save', help='output folder path')
    parser.add_argument('--minimum_white', type=int,
                        default=30, help='Specified minimum white space length')
    args = parser.parse_args()
    # 讀入網頁截圖
    original_image = Image.open(args.input_file)
    # 找到空白區域
    blank_regions = find_continuous_false_ranges(
        process_short_true_ranges(
            find_blank_columns(original_image),args.minimum_white))
    # 建立
    check_folder(args.output_path)
    # 根據空白區域裁切圖像
    cropped_images = crop_image_by_regions(
        original_image, blank_regions, args.output_path)
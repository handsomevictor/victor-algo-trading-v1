import os
import pandas as pd

if __name__ == '__main__':
    # print(os.environ.get('INFLUXDB_TOKEN'))
    #
    # a = {'current_time': ['2023-03-17T01:18:55'], 'index_code': ['KK_RR_BTCUSD'], 'price': [25010.0]}
    # print(pd.DataFrame(a))

    from PIL import Image
    import numpy as np

    image = Image.open("python-logo-master-v3-TM.png")

    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Convert the image to grayscale
    image_gray = np.dot(image_array[...,:3], [0.299, 0.587, 0.114])
    print(image_gray)

    # save to txt
    np.savetxt("python-logo-master-v3-TM.txt", image_gray, fmt="%d", delimiter=",")

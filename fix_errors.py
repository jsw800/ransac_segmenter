import os
import segmenter
import json
import cv2


dirs = [os.path.join('outs', f) for f in os.listdir('outs') if os.path.isdir(os.path.join('outs', f))]


seg = segmenter.RANSAC_segmenter('data/template.jpg', 'data/template.json')

for dir in dirs:
    files = [os.path.join(dir, flnm) for flnm in os.listdir(dir)]
    for flnm in files:
        with open(flnm) as f:
            corners = json.load(f)
        if corners == {}:
            sample_img_name = flnm.split('/')[-1].split('.')[0] + '.jpg'
            sample_img_dir = sample_img_name.split('_')[0]
            sample_img_name = os.path.join('full_1930_set', sample_img_dir, sample_img_name)
            sample_img = cv2.imread(sample_img_name)
            points = seg.segment(sample_img)
            if points is None:
                print('could not segment ' + sample_img_name)
                with open(flnm, 'w+') as f:
                    f.write('{}')
            else:
                out = [[int(points[:, i][0]), int(points[:, i][1])] for i in range(points.shape[1])]
                out = {'corners':out}
                with open(flnm, 'w+') as f:
                    print('segmented ' + sample_img_name)
                    f.write(json.dumps(out))


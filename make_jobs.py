import os
from os.path import join


with open('jobs/template.sh') as f:
    template = f.read()

dirs = [flnm for flnm in os.listdir('full_1930_set') if os.path.isdir('full_1930_set/' + flnm)]
nums = [flnm for flnm in dirs]
out_dirs = [join('outs', flnm) for flnm in dirs]
dirs = [join('full_1930_set', flnm) for flnm in dirs]


for i in range(len(dirs)):
    command = 'mkdir ' + out_dirs[i] + '\npython segmenter.py data/template.jpg data/template.json ' + \
               dirs[i] + ' ' + out_dirs[i]
    sh = template + command
    with open('jobs/' + nums[i] + '.sh', 'w+') as f:
        f.write(sh)


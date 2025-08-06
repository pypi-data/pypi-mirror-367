from invoke import task
from pathlib import Path

@task(default=True)
def setup_dev(c):
    from fhopecc import env
    import os
    github = env.githubdrive / 'github'
    p = Path(__file__).parent
    pythonpath = ";".join([str(Path(__file__).parent), os.environ['PYTHONPATH']])
    os.system(f'setx PYTHONPATH {pythonpath}')

@task
def hanlp(c):
    from pathlib import Path
    from zhongwen.file import 下載
    import logging
    logging.basicConfig(level=logging.INFO)
    local = Path.home() / 'AppData\Roaming\hanlp'
    url = 'https://ftp.hankcs.com/hanlp/tok/coarse_electra_small_20220616_012050.zip'
    下載(url, 儲存目錄=local / 'tok')
    url = 'https://ftp.hankcs.com/hanlp/utils/char_table_20210602_202632.json.zip'
    下載(url, 儲存目錄=local / 'utils')
    url = 'https://ftp.hankcs.com/hanlp/transformers/electra_zh_small_20210706_125427.zip'
    下載(url, 儲存目錄=local / 'transformers')
    url = 'https://ftp.hankcs.com/hanlp/transformers/electra_zh_small_20210706_125427.zip'

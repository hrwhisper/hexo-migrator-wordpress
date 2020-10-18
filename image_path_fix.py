
import os
import re
import requests

def parse_custon_url(text: str) -> str:
    """Parse
    ---
    title: Gephi 安装后 打不开解决办法
    tags: []
    id: '2220'
    categories:
    - - others
        - 问题解决
    custom_url: can-not-open-gephi-solution
    date: 2015-10-29 19:28:20
    ---

    to can-not-open-gephi-solution
    """
    head = text.split("---")[1]
    target_str = "custom_url:"
    index = head.index("custom_url:")
    head = head[index:]
    end_index = head.index("\n")
    custom_url = head[len(target_str):end_index].lstrip().strip()
    return custom_url

def replace_all_image_path(text: str, image_path: str) -> str:
    """
    # ![decision-tree-example](./decision-tree-example.png)
    """
    pattern = r"\!\[(?P<imgname>.*?)\]\((?P<filepath>.*)\)"
    # print(re.findall(pattern, text))
    text = re.sub(pattern, 
            lambda m: '![{}]({})'.format(m.group('imgname'), 
                        image_path + os.path.basename(m.group('filepath'))), text)
    return text


def request_image_path(filename:str, text: str) -> None:
    pattern = r"\!\[(?P<imgname>.*?)\]\((?P<filepath>.*)\)"
    for _, url in re.findall(pattern, text):
        if url.startswith('../images/'):
            url = url[3:]
            url = f'http://localhost:4000/{url}'
            r = requests.get(url)
            if r.status_code != 200:
                print(f'filename:{filename} url:{url}, result:{r}')
        else:
            print(f'skip filename:{filename} url:{url}')

if __name__ == "__main__":
    base_path = "/mnt/F/blog/blog/source/_posts"
    post_name_list = os.listdir(base_path)

    # step1: replace all image path
    for filename in post_name_list:
        if filename.startswith('leetcode'):
            continue
        with open(os.path.join(base_path, filename)) as f:
            text = f.read()
        # print(text)
        try:
            custom_url = parse_custon_url(text)

            image_path = '../images/' + custom_url +'/'
            text = replace_all_image_path(text, image_path)
            with open(os.path.join(base_path, filename), 'w') as f:
                f.write(text)
        except Exception as e:
            print(filename, e)

    # # step2: request all image path, and judge it is ok
    for filename in post_name_list:
        with open(os.path.join(base_path, filename)) as f:
            text = f.read()
            request_image_path(filename, text)

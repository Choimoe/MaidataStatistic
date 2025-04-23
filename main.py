import os
import re


def remove_comments(text):
    """去除大花括号内的注释内容"""
    return re.sub(r'\{.*?}', '', text, flags=re.DOTALL)


def remove_before_inote_6(text):
    index = text.find("inote_6")

    if index != -1:
        return text[index + len("inote_6"):]
    else:
        return text


def find_matching_lines_in_file(file_path):
    """检查文件内容并返回符合条件的行"""
    matches = []
    is_white = False

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().replace('\n', '').replace('\r', '')

        # 去除注释部分
        # content = remove_comments(content)

        if not re.search(r'inote_6', content):
            return []

        if not re.search(r'14', content):
            return []

        remove_before_inote_6(content)

        rrr = r'\{2\}[^{}]*,[^{}]*,[^{}]*,[^{}]*,\{4\}[^{}]*,[^{}]*,[^{}]*,[^{}]*,\{2\}[^{}]*,[^{}]*,[^{}]*,[^{}]*,'

        # 查找匹配的字符串
        # if re.search(
        #         r'1\s*,2\s*,3\s*,4\s*,5\s*,6\s*,7\s*,8\s*,'
        #         r'1\s*,2\s*,3\s*,4\s*,5\s*,6\s*,7\s*,8\s*,'
        #         r'1\s*,2\s*,3\s*,4\s*,5\s*,6\s*,7\s*,8\s*,'
        #         r'1\s*,2\s*,3\s*,4\s*,5\s*,6\s*,7\s*,8\s*,',
        #         content):
        if re.search(
                rrr,
                # r'1\s*[a-zA-Z]*,8\s*[a-zA-Z]*,1\s*[a-zA-Z]*,8\s*[a-zA-Z]*,1\s*[a-zA-Z]*,8\s*[a-zA-Z]*,1\s*[a-zA-Z]*,8\s*[a-zA-Z]*,'
                # r'1\s*[a-zA-Z]*,2\s*[a-zA-Z]*,3\s*[a-zA-Z]*,4\s*[a-zA-Z]*,5\s*[a-zA-Z]*,6\s*[a-zA-Z]*,7\s*[a-zA-Z]*,8\s*[a-zA-Z]*,'
                # r'1\s*[a-zA-Z]*,2\s*[a-zA-Z]*,3\s*[a-zA-Z]*,4\s*[a-zA-Z]*,5\s*[a-zA-Z]*,6\s*[a-zA-Z]*,7\s*[a-zA-Z]*,8\s*[a-zA-Z]*,'
                # r'1\s*[a-zA-Z]*,8\s*[a-zA-Z]*,1\s*[a-zA-Z]*,8\s*[a-zA-Z]*,1\s*[a-zA-Z]*,8\s*[a-zA-Z]*,1\s*[a-zA-Z]*,8\s*[a-zA-Z]*,',
                content):
            qwq = ','.join(re.findall(rrr, content))
            if not re.search('s', qwq):
                return []
            print(qwq)
            matches.append(file_path)

    return matches


def search_in_folder(root_folder):
    """遍历文件夹及子文件夹查找所有符合条件的文件"""
    matched_files = []

    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename == 'maidata.txt':  # 只处理名为maidata.txt的文件
                file_path = os.path.join(dirpath, filename)
                matches = find_matching_lines_in_file(file_path)
                matched_files.extend(matches)

    return matched_files


# 调用搜索函数并输出结果
root_folder = '.'  # 请替换为实际的文件夹路径
matching_files = search_in_folder(root_folder)

# 打印所有符合条件的文件路径
if matching_files:
    print("匹配的文件:")
    for file in matching_files:
        print(file)
else:
    print("没有找到匹配的文件。")

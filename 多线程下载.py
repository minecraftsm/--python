import threading
import requests
import os
from urllib.parse import urlparse, unquote

# wb,rb等为格式

def get_filename_from_url(url):
    # 从URL中获取文件名
    parsed_url = urlparse(url)
    filename = unquote(os.path.basename(parsed_url.path)) # 这里使用了Python的urllib.parse库中的urlparse函数来解析给定的URL，将其拆分为各个部分，例如协议、主机、路径等。os.path.basename函数用于从路径中提取文件名
    # unquote函数用于解码URL编码的特殊字符。URL编码通常用于在URL中表示特殊字符，例如空格被编码为"%20"。通过调用unquote函数，同学们可以将编码的字符还原为原始字符。这是为了确保文件名不包含编码后的特殊字符。
    return filename

def get_file_extension(filename):
    # 获取文件的后缀名
    _, file_extension = os.path.splitext(filename) # 加入"_,"来确保最后不出现符号，os.path.splitext接受一个文件名 filename，并将其拆分为文件的根部分和扩展名部分。
    return file_extension

def download_file(url, thread_id, num_threads):
    response = requests.get(url, stream=True) # 启动流式下载
    total_size = int(response.headers.get('content-length', 0))
    chunk_size = total_size // num_threads

    start_byte = thread_id * chunk_size # thread_id其实是for i in range生成的，所以是0-num_thread - 1,不要以为是1-num_thread!!!!!!
    end_byte = start_byte + chunk_size

    headers = {'Range': f'bytes={start_byte}-{end_byte}'}

    downloaded_bytes = 0

    # 获取文件名并提取后缀
    filename = get_filename_from_url(url)
    file_extension = get_file_extension(filename)

    with open(f'download_part_{thread_id}{file_extension}', 'wb') as f:
        for chunk in response.iter_content(chunk_size=128):
            if chunk:
                f.write(chunk)
                downloaded_bytes += len(chunk)

                progress = (downloaded_bytes / total_size) * 100
                print(f"Thread {thread_id} - Progress: {progress:.2f}%")

    print(f"Thread {thread_id} finished downloading")

def main():
    file_url = input("请输入要下载的URL: ")
    num_threads = int(input("请输入要使用的线程数量(建议2-8，最佳为4): "))

    thread_list = []

    for i in range(num_threads):
        thread = threading.Thread(target=download_file, args=(file_url, i, num_threads))
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

    # 获取文件名并提取后缀
    filename = get_filename_from_url(file_url)
    file_extension = get_file_extension(filename)

    # 合并下载的部分文件并添加后缀
    with open(f'downloaded_file{file_extension}', 'wb') as output_file:
        for i in range(num_threads):
            with open(f'download_part_{i}{file_extension}', 'rb') as part_file:
                output_file.write(part_file.read())

    # 删除下载的部分文件
    for i in range(num_threads):
        os.remove(f'download_part_{i}{file_extension}')

if __name__ == "__main__":
    main()

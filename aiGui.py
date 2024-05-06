import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
import tkinter.ttk as ttk
import xml.etree.ElementTree as ET
import base64
from openai import OpenAI
import time
import re

def process_chunks(chunks, target_list, excluded_phrase):
    for idx, chunk in enumerate(chunks.split('\n')):
        if chunk != excluded_phrase:
            tmp = chunk.replace(str(idx), "")
            if tmp:
                target_list.append(tmp)
                print(idx, tmp)
security_issue_list = []
Expanded_attack_surface_list = []
Basic_Information = []

client = OpenAI(
  api_key="sk-8hzzdlK9qzptZ",
  base_url="https://api.moonshot.cn/v1",
)

# 用于打开文件对话框，选择XML文件并展示内容的函数
def open_xml_file():
    URL_list = []
    # 清空表格内容
    for i in tree_view.get_children():
        tree_view.delete(i)
    
    # 获取用户选择的文件路径
    file_path = filedialog.askopenfilename(
        title='Open XML File',
        filetypes=[('XML files', '*.xml')]
    )
    
    if file_path:
        try:
            # 解析XML文件
            tree = ET.parse(file_path)  # 注意：这里的 tree 是局部变量，仅用于解析
            root = tree.getroot()
            
            # 遍历所有的item元素，并获取其中的url和mimetype文本
            for item in root.findall('item'):
                #url = item.find('url').text
                #mimetype = item.find('mimetype').text
                url = item.find('url').text
                host = item.find('host').text
                port = item.find('port').text
                protocol = item.find('protocol').text
                method = item.find('method').text
                path = item.find('path').text
                extension = item.find('extension').text
                request = item.find('request').text
                status = item.find('status').text
                responselength = item.find('responselength').text
                mimetype = item.find('mimetype').text
                response = item.find('response').text
                comment = item.find('comment').text
                # 如果需要处理base64编码的数据
                request_base64 = item.find('request').get('base64')
                response_base64 = item.find('response').get('base64')
                checkTypeList = ["JSON" , "HTML", None]
                if mimetype in checkTypeList and url not in URL_list:
                    URL_list.append(url)
                    try:
                        if request_base64:
                            # 解码base64数据
                            request_data = base64.b64decode(request)
                            request_info = request_data.decode('utf-8')
                        else:
                            request_info = request

                        if response_base64:
                            # 解码base64数据
                            response_data = base64.b64decode(response)
                            response_info = response_data.decode('utf-8')
                        else:
                            response_info = response
                    except:
                        pass
                    infomation = '''request:
{}
response:
{}'''.format(request_info, response_info)
                    # 将item的信息添加到表格中
                    tree_view.insert('', 'end', text='Item', values=(url, mimetype, len(infomation),infomation))
        except ET.ParseError:
            messagebox.showerror("Error", "Failed to parse XML file.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# 定义当AI测试按钮被点击时执行的函数
def ai_testing():
    # 这里添加您想要执行的检测逻辑
    selected_items = tree_view.selection()  # 获取所有被选中的行
    for item in selected_items:
        # 获取该行的URL值
        len = int(tree_view.item(item, "values")[2])
        infomation = tree_view.item(item, "values")[3]
        if len < 7900:
            model_name = "moonshot-v1-8k"
        elif len < 31500:
            model_name = "moonshot-v1-32k"
        elif len < 127500:
            model_name = "moonshot-v1-128k"
        else:
            model_name = None
            messagebox.showinfo("AI Testing", f"数据包过大，超出api分析能力")
        # 这里可以添加对URL进行AI测试的代码
        if model_name != None:
            # 构建请求的payload
            system_message = {"role": "system","content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，擅长进行渗透测试，发现潜在问题并给出解决方案。我将发送给你一个完整的数据包，请帮我查看是否有潜在的安全问题，以及可以着重检查哪些方面的安全问题。回答的格式为：发现的安全问题有：\n需要拓展检测的攻击面有：\n系统基本信息是：\n，每一方面总结不要超过5点内容。"}
            user_message = {"role": "user","content": infomation}
            messages = [system_message, user_message]
        
            # 发送请求并获取响应
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.3,
                stream=True,
            )
            collected_messages = []
            for idx, chunk in enumerate(completion):
                # print("Chunk received, value: ", chunk)
                chunk_message = chunk.choices[0].delta
                if not chunk_message.content:
                    continue
                collected_messages.append(chunk_message)
                add_to_text(chunk_message.content)
                #print(chunk_message.content)

                root.update()  # 强制立即更新GUI
            FullConversation = ''.join([m.content for m in collected_messages])
            parts = re.split(r'\n\s*\n', FullConversation)
            # 处理第一部分
            process_chunks(parts[0], security_issue_list, "发现的安全问题有：")
            
            # 处理第二部分
            process_chunks(parts[1], Expanded_attack_surface_list, "需要拓展检测的攻击面有：")
            
            # 处理第三部分
            process_chunks(parts[2], Basic_Information, "系统基本信息是：")
            add_to_text("\n" + "-" * 55 + "\n")
                #collected_messages.append(chunk_message)  # save the message
                #update_data("#{idx}: {''.join([m.content for m in collected_messages])}")
                #messagebox.showinfo("AI Testing", f"#{idx}: {''.join([m.content for m in collected_messages])}")
                #show_custom_dialog(f"#{idx}: {''.join([m.content for m in collected_messages])}")
            # 打印结果
            #print(completion.choices[0].message.content)
            #messagebox.showinfo("AI Testing", completion.choices[0].message.content)

# 定义当AI测试按钮被点击时执行的函数
def result_analysis():
    add_to_text("发现的安全问题有：\n")
    for i in security_issue_list:
        add_to_text(i+'\n')
    add_to_text("\n需要拓展检测的攻击面有：\n")
    for i in Expanded_attack_surface_list:
        add_to_text(i+'\n')
    add_to_text("\n系统基本信息是：\n")
    for i in Basic_Information:
        add_to_text(i+'\n')

# 将数据添加到文本框的函数
def add_to_text(data):
    text_widget.configure(state='normal')  # 允许编辑
    text_widget.insert(tk.END, data)  # 在文本框末尾添加数据
    text_widget.see(tk.END)  # 自动滚动到文本框底部
    text_widget.configure(state='disabled')  # 禁止编辑

# 创建主窗口
root = tk.Tk()
root.title("AI辅助渗透测试")
root.geometry("1250x550")
root.resizable(False, False)

# 创建一个frame用于放置按钮，以保持它们对齐
button_frame = tk.Frame(root)
button_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

# 创建文件选择按钮并加入到frame中
file_button = tk.Button(button_frame, text="选择XML文件", command=open_xml_file)
file_button.pack(side=tk.TOP, fill=tk.X, expand=True)

# 创建AI测试按钮并加入到frame中
ai_test_button = tk.Button(button_frame, text="AI测试", command=ai_testing)
ai_test_button.pack(side=tk.TOP, fill=tk.X, expand=True)

# 创建结果分析按钮并加入到frame中
result_button = tk.Button(button_frame, text="结果分析", command=result_analysis)
result_button.pack(side=tk.TOP, fill=tk.X, expand=True)

# 创建一个frame用于放置表格和滚动条
tree_frame = tk.Frame(root)
tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# 创建用于展示XML内容的表格
tree_view = ttk.Treeview(root, columns=['URL', 'Mimetype', 'Length'], show="headings")
tree_view.column('URL', anchor='w', width=450)
tree_view.column('Mimetype', anchor='w', width=50)
tree_view.column('Length', anchor='w', width=50)  # 修正列标题的拼写
tree_view.heading('URL', text='URL')
tree_view.heading('Mimetype', text='Mimetype')
tree_view.heading('Length', text='Length')  # 修正列标题的拼写
tree_view.column('#0', stretch=tk.YES, minwidth=0)  # 确保第一列可以伸展
tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 创建一个滚动条，并将其与Treeview控件关联
scrollbar1 = tk.Scrollbar(tree_frame, orient="vertical", command=tree_view.yview)
scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)  # 放置在tree_frame的右侧并填满垂直空间

# 将滚动条与Treeview控件关联
tree_view.configure(yscrollcommand=scrollbar1.set)
# 创建一个Frame用于放置文本框和滚动条，放在表格的右边
stream_frame = tk.Frame(root, width=300)
stream_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# 创建一个滚动条
scrollbar = tk.Scrollbar(stream_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 创建一个文本框用于展示流式数据
text_widget = tk.Text(stream_frame, wrap=tk.WORD, height=15, yscrollcommand=scrollbar.set)
text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 将滚动条与文本框关联
scrollbar.config(command=text_widget.yview)

# 运行主循环
root.mainloop()
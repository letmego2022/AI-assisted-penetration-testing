# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request, jsonify, Response
import itertools
import time
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
  api_key="sk-",
  base_url="https://api.moonshot.cn/v1",
)



HTML_INDEX_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI安全基线检查</title>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="static/bootstrap.min.css">
    <!-- Custom styles -->
    <style>
        body {
            padding-top: 2rem;
        }
        .scanner-container {
            max-width: 960px;
            margin: 0 auto;
            padding: 2rem;
            border: 1px solid #e3e3e3;
            border-radius: .25rem;
            background-color: #f9f9f9;
        }
        .input-group {
            margin-bottom: 1rem;
        }
        .result-container {
            display: flex;
        }
        .crawled-links, .ai-analysis {
            padding: 1rem;
            border: 1px solid #e3e3e3;
            border-radius: .25rem;
            margin-right: 1rem;
            background-color: #fff;
            flex: 1;
        }
        .ai-analysis {
            margin-right: 0;
        }
        #url-input {
            flex-grow: 1;
        }
        #scan-button {
            padding: .5rem 1rem;
        }
        .hidden {
            display: none;
        }
        .link-entry {
            margin-bottom: 1rem;
            padding: 1rem;
            border: 1px solid #e3e3e3;
            border-radius: .25rem;
            background-color: #fff;
        }
    </style>
    <!-- Optional Bootstrap JavaScript -->
    <script src="static/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="static/bootstrap.min.js"></script>
</head>
<body>
    <div class="scanner-container">
        <div class="input-group">
            <input type="url" id="url-input" class="form-control" placeholder="http://example.com">
            <div class="input-group-append">
                <button id="scan-button" class="btn btn-primary" type="button" onclick="scanURL()">Scan</button>
            </div>
        </div>

        <div class="result-container">
            <div class="crawled-links box">
                <h3>爬取的链接情况</h3>
                <div id="crawled-links">
                    <!-- 爬取的链接将在这里显示 -->
                </div>
            </div>
            <div class="ai-analysis box">
                <h3>AI 分析过程</h3>
                <div id="ai-analysis">
                    <!-- AI分析的过程将在这里显示 -->
                </div>
            </div>
        </div>
    </div>

    <!-- JavaScript for scanning -->
<script>
    // 添加一个函数来处理从服务器接收到的AI分析步骤
    function handleAIAnalysisStep(step) {
        const analysisBox = document.getElementById('ai-analysis');
        analysisBox.innerHTML += step;
        analysisBox.scrollTop = analysisBox.scrollHeight; // 滚动到最新内容
    }
	// 处理从服务器接收到的AI分析步骤或AI问候
    function handleAIMessage(step) {
        const analysisBox = document.getElementById('ai-analysis');
        analysisBox.innerHTML += step;
        analysisBox.scrollTop = analysisBox.scrollHeight; // 滚动到最新内容
    }

    // 当页面加载完成后，启动AI问候流式传输
    document.addEventListener('DOMContentLoaded', function() {
        // 连接到AI分析流（如果需要的话）
        // ...

        // 连接到AI问候流式传输
        const aiGreetingEventSource = new EventSource('/ai-greeting-stream');
        aiGreetingEventSource.onmessage = function(event) {
            handleAIMessage(event.data);
        };
        aiGreetingEventSource.onerror = function(error) {
            console.error('AI Greeting EventSource failed:', error);
            aiGreetingEventSource.close(); // 如果发生错误，关闭连接
        };
    });

    function scanURL() {
        var urlInput = document.getElementById('url-input');
        var url = urlInput.value;

        // 使用 fetch 发送 AJAX POST 请求到服务器
        fetch('/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'url=' + encodeURIComponent(url)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 在页面上显示爬取的链接
                document.getElementById('crawled-links').innerHTML = data.links.join('<br>');

                // 开始监听AI分析步骤的流式数据
                const eventSource = new EventSource('/ai-analysis-stream');
                eventSource.onmessage = function(event) {
                    handleAIAnalysisStep(event.data);
                };
                eventSource.onerror = function(error) {
                    console.error('EventSource failed:', error);
                    eventSource.close(); // 如果发生错误，关闭连接
                };
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('扫描过程中发生错误。');
        });
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INDEX_PAGE)

@app.route('/scan', methods=['POST'])
def scan():
    # 获取 POST 请求中的 URL 参数
    url = request.form.get('url')
    # 这里应该添加实际的扫描逻辑
    # 模拟返回一些数据
    links = ['http://example.com/link1', 'http://example.com/link2']
    analysis = 'AI分析结果将在这里显示。'
    return jsonify({
        'status': 'success',
        'message': 'URL扫描完成。',
        'links': links,
        'analysis': analysis
    })

@app.route('/ai-analysis-stream')
def ai_analysis_stream():
    def event_stream():
        system_message = {"role": "system","content": "你是 AI安全基线检查助手，由 Moonshot AI 提供的人工智能助手，擅长进行渗透测试，发现潜在问题并给出解决方案。我将发送给你一个完整的数据包，请帮我查看是否有潜在的安全问题，以及可以着重检查哪些方面的安全问题。回答的格式为：发现的安全问题有：\n需要拓展检测的攻击面有：\n系统基本信息是：\n，每一方面总结不要超过5点内容。"}
        infomation = '''request:
GET /service-storage/sys-file/download?id=null&catalog=portrait HTTP/1.1
Host: 172.16.210.22:8260
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36
Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Referer: http://172.16.210.22:8260/index.html
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: accessToken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGwiLCJ1aWQiOiI3MDg2MTAyMjQ0OTEwNjk0NDAiLCJhdWQiOiJCRDY3ODE0IiwiaXNzIjoiZm94bmljLXdlYi5jb20iLCJleHAiOiIyMDI0LTA0LTI5IDE1OjUwOjMxIiwiaWF0IjoiMjAyNC0wNC0yOSAxNToyMDozMSIsImp0aSI6ImRkNTRkOGI1LTg5ZGItNDcxYy04N2I5LWNmZTFiZjQzMTZjYSJ9.GoUxjWO371WPdQwIzRxngZZGW8Kb1RusY0JHVF4v5b7OxvrEAVfD2fkssxDhmBomIJs-owajS9cWCGE4PYNxqCgmcc4rToX4A3AZO8mm5eamB9cP8YE7GmC7BQtXlSJ6HqoZIQfI5Q7Ev4j-j9DrIB6jugXL_6eAOQk3dKTejhonrZM3InKbKlKLzrQharyCCikvjGgttUp7btmNrU7qgwWw7rHy2OFhJSY3TYol0iW5YfqhP4wWHT-1ZpC7j1T-9ybYrHBmpCIp40p5q-hLOWnk27gE6y8WW2sDeVsosW9kDdMqKUwC5cllRzNz7__EyoiT0bmI_SlmUFO7kU01iA; refreshToken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGwiLCJ1aWQiOiI3MDg2MTAyMjQ0OTEwNjk0NDAiLCJhdWQiOiJCRDY3ODE0IiwiaXNzIjoiZm94bmljLXdlYi5jb20iLCJleHAiOiIyMDI0LTA0LTI5IDE2OjIwOjMxIiwiaWF0IjoiMjAyNC0wNC0yOSAxNToyMDozMSIsImp0aSI6ImRkNTRkOGI1LTg5ZGItNDcxYy04N2I5LWNmZTFiZjQzMTZjYSJ9.fnIdYf8oOOLAW9m__EdplkWN5lIKdrIbcUcYGnTFoV76h552kLU5vpzH9fiVjFZZZrrwFFDbLX5UTmErbmrZXGtHF070pY3tMKUt76HYSjhGV9-R0W7RpQJdXeIY-fhL-oyW5P-zJGNvDEJqvAZenmCEJpU0_Qzpd4ppJRsLdu863WCbqapj2wDyl-OabFFx-F_cwaJCVBR3w0fm7r2b0m6NOjxerqorniIoFEghj_rRj_9D2pMSwUGjgfCm2yQeIILIIZxKt-I48Ge8aS6yqBKNwcapze_20jakCHgZobPGzb_BohglV2eUpX_lsyZbuvkxRWXj3wP5nM8NMLu1yw; JSESSIONID=3VEj7hqvUc_0X7516WDUhIuWRwR_KItUv6aqbRhf
Connection: close


response:
HTTP/1.1 200 OK
Expires: 0
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
X-XSS-Protection: 1; mode=block
Pragma: no-cache
Date: Mon, 29 Apr 2024 07:20:40 GMT
Connection: close
Vary: Origin
Vary: Access-Control-Request-Method
Vary: Access-Control-Request-Headers
X-Content-Type-Options: nosniff
Content-Length: 92

{"code":"34","extra":{"messageLevel":"read"},"message":"file is not exists","success":false}'''
        user_message = {"role": "user","content": infomation}
        messages = [system_message, user_message]
        
        # 发送请求并获取响应
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
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
            print(chunk_message)
            yield f"data: {chunk_message.content.replace("\n", "<br>")}\n\n"
            print(chunk_message.content)
        yield "data: <br>***********↑↑↑↓↓↓**************<br>\n\n"
       # while True:
       #     for line in generate():
       #         if not line:
       #             break
       #         yield f"data: {line}\n\n"

    return Response(event_stream(), content_type='text/event-stream')


@app.route('/ai-greeting-stream')
def ai_greeting_stream():
    def generate():
        system_message = {"role": "system","content": "你是 AI安全基线检查助手，由 Moonshot AI 提供的人工智能助手，擅长进行渗透测试，发现潜在问题并给出解决方案。我将发送给你一个完整的数据包，请帮我查看是否有潜在的安全问题，以及可以着重检查哪些方面的安全问题。你只需要用户输入一个网址并点击Scan，就可以。"}
        infomation = "请问你是谁，请简略回答你能帮我在安全方面和渗透测试方面做些什么？最后请说明一下这个工具的用法。"
        user_message = {"role": "user","content": infomation}
        messages = [system_message, user_message]
        
        # 发送请求并获取响应
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
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
            yield f"data: {chunk_message.content.replace("\n", "<br>")}\n\n"
        # 在所有消息发送完毕后，发送一个结束标记
        yield "data: <br>***********↑↑↑↓↓↓**************<br>\n\n"

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082)

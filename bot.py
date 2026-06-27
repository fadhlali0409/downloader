from flask import Flask, render_template_string, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>سوشيال داونلودر</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white p-5 text-center">
    <h1 class="text-2xl font-bold mb-5">أداة تحميل الفيديو</h1>
    <input id="url-input" class="text-black p-2 w-full max-w-md rounded" placeholder="ضع الرابط هنا...">
    <button onclick="analyzeLink()" class="bg-blue-500 p-2 px-5 rounded mt-2">تحليل الرابط</button>
    <div id="result" class="mt-5"></div>
    <script>
        async function analyzeLink() {
            const url = document.getElementById('url-input').value;
            const res = await fetch('/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ url: url })
            });
            const data = await res.json();
            if(data.success) {
                document.getElementById('result').innerHTML = `<a href="${data.url}" class="text-green-400 font-bold">اضغط هنا للتحميل</a>`;
            } else {
                alert('خطأ: ' + data.error);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url')
    ydl_opts = {'format': 'best', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or (info['formats'][-1]['url'] if 'formats' in info else None)
            return jsonify({'success': True, 'url': video_url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run()
    

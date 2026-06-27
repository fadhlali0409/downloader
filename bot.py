from flask import Flask, render_template_string, request, jsonify
import yt_dlp

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html dir="rtl">
<body>
    <input id="u" placeholder="ضع الرابط هنا">
    <button onclick="go()">تحميل</button>
    <div id="r"></div>
    <script>
        async function go() {
            let u = document.getElementById('u').value;
            let res = await fetch('/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({url:u})});
            let d = await res.json();
            if(d.ok) document.getElementById('r').innerHTML = '<a href="'+d.link+'">اضغط للتحميل</a>';
            else alert('فشل');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL({'quiet':True}) as ydl:
            i = ydl.extract_info(url, download=False)
            l = i.get('url') or i.get('formats', [{}])[-1].get('url')
            return jsonify({'ok': True, 'link': l})
    except:
        return jsonify({'ok': False})

if __name__ == '__main__':
    app.run()
    

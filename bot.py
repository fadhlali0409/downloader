from flask import Flask, render_template_string, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# واجهة التصميم الأزرق المحدثة بالكامل
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سوشيال داونلودر - تحميل الوسائط</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background: radial-gradient(circle at 50% 30%, #1e40af 0%, transparent 55%), #070a13;
            font-family: system-ui, -apple-system, sans-serif;
        }
        .glass-panel {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
    </style>
</head>
<body class="min-h-screen text-white flex flex-col justify-between p-4 md:p-6">

    <header class="w-full max-w-6xl mx-auto flex items-center justify-between text-xs text-gray-400 pb-4 border-b border-white/5">
        <div class="flex items-center gap-2 bg-sky-500 text-white font-bold px-4 py-2 rounded-xl shadow-lg shadow-sky-500/20">
            <i class="fa-solid fa-circle-down"></i>
            <span>حمّل الآن</span>
        </div>
        <div class="hidden md:flex items-center gap-6">
            <a href="#" class="text-sky-400 font-medium">الرئيسية</a>
            <a href="#" class="hover:text-white transition-colors">كيف يعمل</a>
        </div>
    </header>

    <main class="w-full max-w-4xl mx-auto text-center my-auto py-6 space-y-8">
        <div class="space-y-2">
            <h1 class="text-3xl md:text-5xl font-black">حمّل الوسائط العامة <span class="text-sky-400">في ثوانٍ.</span></h1>
            <p class="text-gray-400 text-xs md:text-sm max-w-xl mx-auto">ألصق رابطاً عاماً من منصتك المفضلة وحلّل الفيديوهات بأفضل جودة ملائمة.</p>
        </div>

        <div class="w-full max-w-2xl mx-auto">
            <div class="glass-panel p-1.5 rounded-2xl flex items-center gap-2 shadow-2xl">
                <input id="url-input" type="url" placeholder="ضع رابط الفيديو هنا..." 
                       class="w-full bg-transparent border-none py-3 px-4 text-white placeholder-gray-500 focus:outline-none text-xs md:text-sm text-right" dir="rtl" />
                <button onclick="analyzeLink()" class="bg-sky-500 hover:bg-sky-400 text-white font-bold px-6 py-3 rounded-xl text-xs md:text-sm whitespace-nowrap flex items-center gap-2 shadow-lg shadow-sky-500/20 cursor-pointer">
                    <i class="fa-solid fa-wand-magic-sparkles"></i>
                    <span id="btn-text">تحليل الرابط</span>
                </button>
            </div>
        </div>

        <div id="results-section" class="w-full max-w-2xl mx-auto bg-blue-600/20 border border-blue-500/30 backdrop-filter blur-xl rounded-2xl p-5 text-right space-y-5 shadow-2xl hidden">
            <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between pb-3 border-b border-white/10">
                <div class="flex items-center gap-3">
                    <img id="video-thumb" src="" class="w-24 h-14 rounded-lg object-cover border border-white/20 shadow-md" />
                    <div>
                        <span id="video-extractor" class="bg-red-500 text-white text-[9px] px-2 py-0.5 rounded font-bold">Video</span>
                        <h3 id="video-title" class="text-xs font-bold text-white mt-1">اسم الفيديو</h3>
                    </div>
                </div>
            </div>

            <div id="download-options" class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
                </div>
        </div>
    </main>

    <script>
        async function analyzeLink() {
            const urlInput = document.getElementById('url-input').value;
            const btnText = document.getElementById('btn-text');
            const resultsSection = document.getElementById('results-section');
            
            if(!urlInput) return alert('الرجاء إدخال رابط أولاً');
            
            btnText.innerText = 'جاري التحليل...';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ url: urlInput })
                });
                const data = await response.json();
                
                if(data.success) {
                    document.getElementById('video-title').innerText = data.title;
                    document.getElementById('video-thumb').src = data.thumbnail;
                    document.getElementById('video-extractor').innerText = data.extractor;
                    
                    const optionsContainer = document.getElementById('download-options');
                    optionsContainer.innerHTML = '';
                    
                    data.formats.forEach(f => {
                        optionsContainer.innerHTML += `
                            <div class="bg-blue-900/40 border border-white/5 p-3 rounded-xl flex items-center justify-between">
                                <a href="${f.url}" target="_blank" class="bg-sky-500 hover:bg-sky-400 text-white font-bold px-3 py-1.5 rounded-lg text-xs flex items-center gap-1"><i class="fa-solid fa-download"></i><span>تحميل</span></a>
                                <div class="text-right">
                                    <div class="text-xs font-bold text-white">${f.quality}</div>
                                </div>
                            </div>
                        `;
                    });
                    resultsSection.classList.remove('hidden');
                } else {
                    alert('فشل في تحليل الرابط: ' + data.error);
                }
            } catch (err) {
                alert('حدث خطأ أثناء الاتصال بالسيرفر');
            } finally {
                btnText.innerText = 'تحليل الرابط';
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
    
    @app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url')
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or (info['formats'][-1]['url'] if 'formats' in info else None)
            
            return jsonify({
                'success': True,
                'title': info.get('title', 'فيديو بدون عنوان'),
                'thumbnail': info.get('thumbnail', ''),
                'extractor': info.get('extractor_key', 'موقع عام'),
                'formats': [{'quality': 'تحميل مباشر', 'url': video_url}]
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
        

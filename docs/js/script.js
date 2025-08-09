// 道教經典翻譯系統 v2.0 - JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // DOM 元素
    const bookSelect = document.getElementById('book-select');
    const chapterSelect = document.getElementById('chapter-select');
    const legacySelect = document.getElementById('legacy-select');
    const originalContentDiv = document.getElementById('original-content');
    const translatedContentDiv = document.getElementById('translated-content');
    const currentTitleDiv = document.getElementById('current-title');
    const contentStatsDiv = document.getElementById('content-stats');
    const systemStatsDiv = document.getElementById('system-stats');
    const prevButton = document.getElementById('prev-chapter');
    const nextButton = document.getElementById('next-chapter');
    const toggleViewButton = document.getElementById('toggle-view');

    // 系統資料結構
            const booksData = {
        "P.Ch.2471太上升玄护命经一卷_PC2471": {
            title: "P.Ch.2471太上升玄护命经一卷",
            chapters: [
                { number: "01", title: "太上升玄护命经一卷" },
            ]
        },
        "元始天尊说十一曜大消灾神咒经_DZ0043": {
            title: "元始天尊说十一曜大消灾神咒经",
            chapters: [
                { number: "01", title: "元始天尊说十一曜大消灾神咒经" },
                { number: "02", title: "九星都咒" },
                { number: "03", title: "五星神咒" },
                { number: "04", title: "太阳真君神咒" },
                { number: "05", title: "太阴真君神咒" },
                { number: "06", title: "木星真君神咒" },
                { number: "07", title: "火星真君神咒" },
                { number: "08", title: "金星真君神咒" },
                { number: "09", title: "水星真君神咒" },
                { number: "10", title: "土星真君神咒" },
                { number: "11", title: "罗睺真君神咒" },
                { number: "12", title: "计都真君神咒" },
                { number: "13", title: "紫气真君神咒" },
                { number: "14", title: "月孛真君神咒" },
                { number: "15", title: "三启颂" },
            ]
        },
        "南华真经口义_DZ0735": {
            title: "南华真经口义",
            chapters: [
                { number: "01", title: "庄子口义发题" },
                { number: "02", title: "庄子口义发题" },
                { number: "03", title: "南华真经口义卷之一" },
                { number: "04", title: "南华真经口义卷之二" },
                { number: "05", title: "南华真经口义卷之三" },
                { number: "06", title: "南华真经口义卷之四" },
                { number: "07", title: "南华真经口义卷之五" },
                { number: "08", title: "南华真经口义卷之六" },
                { number: "09", title: "南华真经口义卷之七" },
                { number: "10", title: "南华真经口义卷之八" },
                { number: "11", title: "南华真经口义卷之九" },
                { number: "12", title: "南华真经口义卷之十" },
                { number: "13", title: "南华真经口义卷之十一" },
                { number: "14", title: "南华真经口义卷之十二" },
                { number: "15", title: "南华真经口义卷之十三" },
                { number: "16", title: "南华真经口义卷之十四" },
                { number: "17", title: "南华真经口义卷之十五" },
                { number: "18", title: "南华真经口义卷之十六" },
                { number: "19", title: "南华真经口义卷之十七" },
                { number: "20", title: "南华真经口义卷之十八" },
                { number: "21", title: "南华真经口义卷之十九" },
                { number: "22", title: "南华真经口义卷之二十" },
                { number: "23", title: "南华真经口义卷之二十一" },
                { number: "24", title: "南华真经口义卷之二十二" },
                { number: "25", title: "南华真经口义卷之二十三" },
                { number: "26", title: "南华真经口义卷之二十四" },
                { number: "27", title: "南华真经口义卷之二十五" },
                { number: "28", title: "南华真经口义卷之二十六" },
                { number: "29", title: "南华真经口义卷之二十七" },
                { number: "30", title: "南华真经口义卷之二十八" },
                { number: "31", title: "南华真经口义卷之二十九" },
                { number: "32", title: "南华真经口义卷之三十" },
                { number: "33", title: "南华真经口义卷之三十一" },
                { number: "34", title: "南华真经口义卷之三十二" },
                { number: "35", title: "内篇逍遥游" },
                { number: "36", title: "内篇齐物论上" },
                { number: "37", title: "内篇齐物论下" },
                { number: "38", title: "内篇养生主" },
                { number: "39", title: "内篇人间世上" },
                { number: "40", title: "内篇人间世下" },
                { number: "41", title: "内篇德充符" },
                { number: "42", title: "内篇大宗师上" },
                { number: "43", title: "内篇大宗师下" },
                { number: "44", title: "内篇应帝王" },
                { number: "45", title: "外篇骈拇" },
                { number: "46", title: "外篇马蹄" },
                { number: "47", title: "外篇胠箧" },
                { number: "48", title: "外篇在宥" },
                { number: "49", title: "外篇天地" },
                { number: "50", title: "外篇天道" },
                { number: "51", title: "外篇天运" },
                { number: "52", title: "外篇刻意" },
                { number: "53", title: "外篇缮性" },
                { number: "54", title: "外篇秋水" },
                { number: "55", title: "外篇至乐" },
                { number: "56", title: "外篇达生" },
                { number: "57", title: "外篇山木" },
                { number: "58", title: "外篇田子方" },
                { number: "59", title: "外篇知北游" },
                { number: "60", title: "杂篇庚桑楚" },
                { number: "61", title: "杂篇徐无鬼" },
                { number: "62", title: "杂篇则阳" },
                { number: "63", title: "杂篇外物" },
                { number: "64", title: "杂篇寓言" },
                { number: "65", title: "杂篇让王" },
                { number: "66", title: "杂篇盗跖" },
                { number: "67", title: "杂篇说剑" },
                { number: "68", title: "杂篇渔父" },
                { number: "69", title: "杂篇列御寇" },
                { number: "70", title: "杂篇天下" },
                { number: "71", title: "南华真经口义后序" },
            ]
        },
        "太上七星神咒经_DZ0383": {
            title: "太上七星神咒经",
            chapters: [
                { number: "01", title: "太上七星神咒经" },
            ]
        },
        "太上元始天尊证果真经_DZ0047": {
            title: "太上元始天尊证果真经",
            chapters: [
                { number: "01", title: "太上元始天尊证果真经" },
            ]
        },
        "太上元始天尊说消殄虫蝗经_DZ0067": {
            title: "太上元始天尊说消殄虫蝗经",
            chapters: [
                { number: "01", title: "太上元始天尊说消殄虫蝗经" },
            ]
        },
        "太上元始天尊说金光明经_DZ0070": {
            title: "太上元始天尊说金光明经",
            chapters: [
                { number: "01", title: "太上元始天尊说金光明经" },
            ]
        },
        "太上洞玄宝元上经_DZ0368": {
            title: "太上洞玄宝元上经",
            chapters: [
                { number: "01", title: "太上洞玄宝元上经" },
            ]
        },
        "太上洞玄灵宝业报因缘经_DZ0336": {
            title: "太上洞玄灵宝业报因缘经",
            chapters: [
                { number: "03", title: "开度品第一" },
                { number: "05", title: "善对品第二" },
                { number: "06", title: "恶报品第三" },
                { number: "07", title: "受罪品第四" },
                { number: "09", title: "忏悔品第五" },
                { number: "11", title: "奉戒品第六" },
                { number: "12", title: "持斋品第七" },
                { number: "14", title: "诵念品第八" },
                { number: "15", title: "行道品第九" },
                { number: "16", title: "弘誓品第十" },
                { number: "17", title: "发愿品第十一" },
                { number: "18", title: "赞叹品第十二" },
                { number: "19", title: "布施品第十三" },
                { number: "21", title: "慈济品第十四" },
                { number: "22", title: "救苦品第十五" },
                { number: "24", title: "功德品第十六" },
                { number: "25", title: "应感品第十七" },
                { number: "26", title: "福报品第十八" },
                { number: "28", title: "生神品第十九" },
                { number: "30", title: "弘救品第二十" },
                { number: "31", title: "证实品第二十一" },
                { number: "32", title: "摄因品第二十二" },
                { number: "33", title: "生化品第二十三" },
                { number: "35", title: "广统品第二十四" },
                { number: "36", title: "会真品第二十五" },
                { number: "37", title: "叙教品第二十六" },
                { number: "38", title: "流通品第二十七" },
            ]
        },
        "太上洞玄灵宝净供妙经_DZ0376": {
            title: "太上洞玄灵宝净供妙经",
            chapters: [
                { number: "01", title: "太上洞玄灵宝净供妙经" },
            ]
        },
        "太上洞玄灵宝法烛经_DZ0349": {
            title: "太上洞玄灵宝法烛经",
            chapters: [
                { number: "01", title: "太上洞玄灵宝法躅经" },
            ]
        },
        "太上洞玄灵宝灭度五炼生尸妙经_DZ0369": {
            title: "太上洞玄灵宝灭度五炼生尸妙经",
            chapters: [
                { number: "01", title: "太上洞玄灵宝灭度五炼生尸妙经" },
            ]
        },
        "太上洞玄灵宝赤书玉诀妙经_DZ0352": {
            title: "太上洞玄灵宝赤书玉诀妙经",
            chapters: [
                { number: "01", title: "太上洞玄灵宝赤书玉诀妙经卷上乃一" },
                { number: "02", title: "太上洞玄灵宝赤书玉诀妙经卷下" },
            ]
        },
        "太上灵宝智慧观身经_DZ0350": {
            title: "太上灵宝智慧观身经",
            chapters: [
                { number: "01", title: "太上灵宝智慧观身经" },
            ]
        },
        "太上灵宝补谢灶王经_DZ0364": {
            title: "太上灵宝补谢灶王经",
            chapters: [
                { number: "01", title: "太上灵宝补谢灶王经" },
            ]
        },
        "太上玄都妙本清静身心经_DZ0035": {
            title: "太上玄都妙本清静身心经",
            chapters: [
                { number: "01", title: "太上玄都妙本清静身心经" },
            ]
        },
        "太上真一报父母恩重经_DZ0065": {
            title: "太上真一报父母恩重经",
            chapters: [
                { number: "01", title: "太上真一报父母恩重经" },
            ]
        },
        "太上神咒延寿妙经_DZ0358": {
            title: "太上神咒延寿妙经",
            chapters: [
                { number: "01", title: "太上神咒延寿妙经" },
            ]
        },
        "太上虚皇保生神咒经_DZ0384": {
            title: "太上虚皇保生神咒经",
            chapters: [
                { number: "01", title: "太上虚皇保生神咒经" },
            ]
        },
        "太乙元真保命长生经_DZ0046": {
            title: "太乙元真保命长生经",
            chapters: [
                { number: "01", title: "太乙元真保命长生经" },
            ]
        },
        "抱朴子（抱朴子内篇）_SBCK109": {
            title: "抱朴子(抱朴子内篇)",
            chapters: [
                { number: "01", title: "刻抱朴子叙" },
                { number: "02", title: "抱朴子序" },
                { number: "03", title: "抱朴子内篇卷一" },
                { number: "04", title: "抱朴子内篇卷二" },
                { number: "05", title: "抱朴子内篇卷三" },
                { number: "06", title: "抱朴子内篇卷四" },
                { number: "07", title: "抱朴子内篇卷五" },
                { number: "08", title: "抱朴子内篇卷六" },
                { number: "09", title: "抱朴子内篇卷七" },
                { number: "10", title: "抱朴子内篇卷八" },
                { number: "11", title: "抱朴子内篇卷九" },
                { number: "12", title: "抱朴子内篇卷十" },
                { number: "13", title: "抱朴子内篇卷十一" },
                { number: "14", title: "抱朴子内篇卷十二" },
                { number: "15", title: "抱朴子内篇卷十三" },
                { number: "16", title: "抱朴子内篇卷十四" },
                { number: "17", title: "抱朴子内篇卷十五" },
                { number: "18", title: "抱朴子内篇卷十六" },
                { number: "19", title: "抱朴子内篇卷十七" },
                { number: "20", title: "抱朴子内篇卷十八" },
                { number: "21", title: "抱朴子内篇卷十九" },
                { number: "22", title: "抱朴子内篇卷二十" },
                { number: "23", title: "抱朴子别旨" },
                { number: "24", title: "抱朴子外篇卷一" },
                { number: "25", title: "抱朴子外篇卷二" },
                { number: "26", title: "抱朴子外篇卷三" },
                { number: "27", title: "抱朴子外篇卷四" },
                { number: "28", title: "抱朴子外篇卷五" },
                { number: "29", title: "抱朴子外篇卷六" },
                { number: "30", title: "抱朴子外篇卷七" },
                { number: "31", title: "抱朴子外篇卷八" },
                { number: "32", title: "抱朴子外篇卷之九" },
                { number: "33", title: "抱朴子外篇卷十" },
                { number: "34", title: "抱朴子外篇卷十一" },
                { number: "35", title: "抱朴子外篇卷十二" },
                { number: "36", title: "抱朴子外篇卷十三" },
                { number: "37", title: "抱朴子外篇卷十四" },
                { number: "38", title: "抱朴子外篇卷十五" },
            ]
        },
        "洞玄灵宝无量度人经诀音义_DZ0095": {
            title: "洞玄灵宝无量度人经诀音义",
            chapters: [
                { number: "01", title: "下一篇" },
                { number: "02", title: "洞玄灵宝无量度人经诀音义秋七" },
                { number: "03", title: "诵诸天内音存念法" },
            ]
        },
        "洞玄灵宝自然九天生神章经_DZ0318": {
            title: "洞玄灵宝自然九天生神章经",
            chapters: [
                { number: "01", title: "下一篇" },
                { number: "02", title: "洞玄灵宝自然九天生神章经" },
                { number: "03", title: "三宝大有金书" },
                { number: "04", title: "始青清微天宝章" },
                { number: "05", title: "元白禹余灵宝章" },
                { number: "06", title: "玄黄太赤神宝章" },
                { number: "07", title: "郁单无量天生神章第一" },
                { number: "08", title: "上上禅善无量寿天生神章第二" },
                { number: "09", title: "梵监须延天生神章第三" },
                { number: "10", title: "寂然兜术天生神章第四" },
                { number: "11", title: "波罗尼蜜不骄乐天生神章第五" },
                { number: "12", title: "洞元化应声天生神章第六" },
                { number: "13", title: "灵化梵辅天生神章第七" },
                { number: "14", title: "高虚清明天生神章第八" },
                { number: "15", title: "无想无结无爱天生神章第九" },
                { number: "16", title: "诵经应验" },
            ]
        },
    };

    // 舊版經典資料（保持向後相容）
    const legacyScriptures = {
        "太上太清天童護命妙經": { original: "olddocs/太上太清天童護命妙經.txt", translation: "olddocs/太上太清天童護命妙經.md" },
        "本經陰符七術": { original: "olddocs/本經陰符七術.text", translation: "olddocs/本經陰符七術.md" },
        "道德經": { original: "olddocs/道德經.txt", translation: "" },
        "道德經全文": { original: "olddocs/道德經全文.txt", translation: "" },
        "道德經第一章": { original: "olddocs/道德經第一章.txt", translation: "" },
        "雲笈七籤119": { original: "olddocs/雲笈七籤119.txt", translation: "olddocs/雲笈七籤119.md" },
        "雲笈七籤121": { original: "olddocs/雲笈七籤121.txt", translation: "olddocs/雲笈七籤121.md" },
        "雲笈七籤33": { original: "olddocs/雲笈七籤33.txt", translation: "olddocs/雲笈七籤33.md" },
        "雲笈七籤59_1": { original: "olddocs/雲笈七籤59_1.txt", translation: "olddocs/雲笈七籤59_1.md" },
        "雲笈七籤60中山玉櫃服氣經": { original: "olddocs/雲笈七籤60中山玉櫃服氣經.txt", translation: "olddocs/雲笈七籤60中山玉櫃服氣經.md" },
        "黃帝陰符經": { original: "olddocs/黃帝陰符經.txt", translation: "olddocs/黃帝陰符經.md" }
    };

    // 當前狀態
    let currentBook = null;
    let currentChapterIndex = 0;
    let viewMode = 'both'; // 'both', 'original', 'translation'

    // 初始化系統
    function initializeSystem() {
        loadSystemStats();
        populateBookSelect();
        populateLegacySelect();
        setupEventListeners();
    }

    // 載入系統統計
    function loadSystemStats() {
        const totalBooks = Object.keys(booksData).length;
        const totalChapters = Object.values(booksData).reduce((sum, book) => sum + book.chapters.length, 0);
        systemStatsDiv.textContent = `📚 ${totalBooks} 部經典 | 📖 ${totalChapters} 個章節 | 📝 102,050 字`;
    }

    // 填充書籍選擇器
    function populateBookSelect() {
        bookSelect.innerHTML = '<option value="">請選擇經典...</option>';
        
        Object.entries(booksData).forEach(([bookId, bookData]) => {
            const option = document.createElement('option');
            option.value = bookId;
            option.textContent = `${bookData.title} (${bookData.chapters.length}章)`;
            bookSelect.appendChild(option);
        });
    }

    // 填充舊版經典選擇器
    function populateLegacySelect() {
        legacySelect.innerHTML = '<option value="">選擇舊版經典...</option>';
        
        Object.keys(legacyScriptures).forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            legacySelect.appendChild(option);
        });
    }

    // 填充章節選擇器
    function populateChapterSelect(bookId) {
        chapterSelect.innerHTML = '<option value="">請選擇章節...</option>';
        
        if (!bookId || !booksData[bookId]) {
            chapterSelect.disabled = true;
            return;
        }

        const chapters = booksData[bookId].chapters;
        chapters.forEach((chapter, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `第${chapter.number}章 - ${chapter.title}`;
            chapterSelect.appendChild(option);
        });
        
        chapterSelect.disabled = false;
    }

    // 設定事件監聽器
    function setupEventListeners() {
        bookSelect.addEventListener('change', handleBookChange);
        chapterSelect.addEventListener('change', handleChapterChange);
        legacySelect.addEventListener('change', handleLegacyChange);
        prevButton.addEventListener('click', navigatePrevChapter);
        nextButton.addEventListener('click', navigateNextChapter);
        toggleViewButton.addEventListener('click', toggleViewMode);
    }

    // 處理書籍選擇變更
    function handleBookChange() {
        const bookId = bookSelect.value;
        
        if (!bookId) {
            chapterSelect.disabled = true;
            chapterSelect.innerHTML = '<option value="">請先選擇經典</option>';
            updateNavigationButtons();
            showWelcomeMessage();
            return;
        }

        currentBook = bookId;
        currentChapterIndex = 0;
        populateChapterSelect(bookId);
        
        // 自動選擇第一章
        if (booksData[bookId].chapters.length > 0) {
            chapterSelect.value = 0;
            loadChapter(bookId, 0);
        }
        
        // 清除舊版選擇
        legacySelect.value = '';
    }

    // 處理章節選擇變更
    function handleChapterChange() {
        const chapterIndex = parseInt(chapterSelect.value);
        
        if (isNaN(chapterIndex) || !currentBook) return;
        
        currentChapterIndex = chapterIndex;
        loadChapter(currentBook, chapterIndex);
    }

    // 處理舊版經典選擇
    function handleLegacyChange() {
        const scriptureName = legacySelect.value;
        
        if (!scriptureName) return;
        
        loadLegacyScripture(scriptureName);
        
        // 清除新版選擇
        bookSelect.value = '';
        chapterSelect.disabled = true;
        chapterSelect.innerHTML = '<option value="">請先選擇經典</option>';
        currentBook = null;
        updateNavigationButtons();
    }

    // 載入章節內容
    async function loadChapter(bookId, chapterIndex) {
        const bookData = booksData[bookId];
        const chapter = bookData.chapters[chapterIndex];
        
        if (!chapter) return;

        // 更新標題和統計
        currentTitleDiv.textContent = `${bookData.title} - 第${chapter.number}章`;
        contentStatsDiv.textContent = `第 ${chapterIndex + 1} / ${bookData.chapters.length} 章`;
        
        // 顯示載入狀態
        originalContentDiv.innerHTML = '<div class="loading"></div> 載入原文中...';
        translatedContentDiv.innerHTML = '<div class="loading"></div> 載入翻譯中...';

        try {
            // 載入原文
            const originalPath = `source_texts/${bookId}/原文/${chapter.number}_${chapter.title}.txt`;
            const originalResponse = await fetch(originalPath);
            
            if (originalResponse.ok) {
                const originalText = await originalResponse.text();
                originalContentDiv.innerHTML = `<pre>${originalText}</pre>`;
            } else {
                originalContentDiv.innerHTML = '<p>❌ 無法載入原文</p>';
            }

            // 載入翻譯
            const translationPath = `translations/${bookId}/${chapter.number}_${chapter.title}.md`;
            const translationResponse = await fetch(translationPath);
            
            if (translationResponse.ok) {
                const translationMarkdown = await translationResponse.text();
                translatedContentDiv.innerHTML = marked.parse(translationMarkdown);
            } else {
                translatedContentDiv.innerHTML = '<p>❌ 無法載入翻譯</p>';
            }

        } catch (error) {
            console.error('載入章節時發生錯誤:', error);
            originalContentDiv.innerHTML = `<p>❌ 載入原文失敗: ${error.message}</p>`;
            translatedContentDiv.innerHTML = `<p>❌ 載入翻譯失敗: ${error.message}</p>`;
        }

        updateNavigationButtons();
    }

    // 載入舊版經典
    async function loadLegacyScripture(scriptureName) {
        const paths = legacyScriptures[scriptureName];
        if (!paths) return;

        currentTitleDiv.textContent = `${scriptureName} (舊版)`;
        contentStatsDiv.textContent = '舊版經典';

        // 顯示載入狀態
        originalContentDiv.innerHTML = '<div class="loading"></div> 載入原文中...';
        translatedContentDiv.innerHTML = '<div class="loading"></div> 載入翻譯中...';

        try {
            // 載入原文
            const originalResponse = await fetch(paths.original);
            if (originalResponse.ok) {
                const originalText = await originalResponse.text();
                originalContentDiv.innerHTML = `<pre>${originalText}</pre>`;
            } else {
                originalContentDiv.innerHTML = '<p>❌ 無法載入原文</p>';
            }

            // 載入翻譯
            if (paths.translation) {
                const translationResponse = await fetch(paths.translation);
                if (translationResponse.ok) {
                    const translationMarkdown = await translationResponse.text();
                    translatedContentDiv.innerHTML = marked.parse(translationMarkdown);
                } else {
                    translatedContentDiv.innerHTML = '<p>❌ 無法載入翻譯</p>';
                }
            } else {
                translatedContentDiv.innerHTML = '<p>📝 此經典暫無翻譯</p>';
            }

        } catch (error) {
            console.error('載入舊版經典時發生錯誤:', error);
            originalContentDiv.innerHTML = `<p>❌ 載入原文失敗: ${error.message}</p>`;
            translatedContentDiv.innerHTML = `<p>❌ 載入翻譯失敗: ${error.message}</p>`;
        }
    }

    // 導航到上一章
    function navigatePrevChapter() {
        if (!currentBook || currentChapterIndex <= 0) return;
        
        currentChapterIndex--;
        chapterSelect.value = currentChapterIndex;
        loadChapter(currentBook, currentChapterIndex);
    }

    // 導航到下一章
    function navigateNextChapter() {
        if (!currentBook) return;
        
        const maxIndex = booksData[currentBook].chapters.length - 1;
        if (currentChapterIndex >= maxIndex) return;
        
        currentChapterIndex++;
        chapterSelect.value = currentChapterIndex;
        loadChapter(currentBook, currentChapterIndex);
    }

    // 更新導航按鈕狀態
    function updateNavigationButtons() {
        if (!currentBook) {
            prevButton.disabled = true;
            nextButton.disabled = true;
            return;
        }

        const maxIndex = booksData[currentBook].chapters.length - 1;
        prevButton.disabled = currentChapterIndex <= 0;
        nextButton.disabled = currentChapterIndex >= maxIndex;
    }

    // 切換顯示模式
    function toggleViewMode() {
        const container = document.querySelector('.text-container');
        
        switch (viewMode) {
            case 'both':
                viewMode = 'original';
                container.className = 'text-container original-only';
                toggleViewButton.textContent = '📝 顯示翻譯';
                break;
            case 'original':
                viewMode = 'translation';
                container.className = 'text-container translation-only';
                toggleViewButton.textContent = '📜 顯示原文';
                break;
            case 'translation':
                viewMode = 'both';
                container.className = 'text-container';
                toggleViewButton.textContent = '🔄 切換顯示模式';
                break;
        }
    }

    // 顯示歡迎訊息
    function showWelcomeMessage() {
        currentTitleDiv.textContent = '道教經典翻譯系統';
        contentStatsDiv.textContent = '';
        
        originalContentDiv.innerHTML = `
            <div class="welcome-message">
                <h4>系統說明</h4>
                <p>🏛️ <strong>收錄經典：</strong></p>
                <ul>
                    <li><strong>太上元始天尊證果真經</strong> - 1章</li>
                    <li><strong>太上元始天尊說消殄蟲蝗經</strong> - 1章</li>
                    <li><strong>太上真一報父母恩重經</strong> - 1章</li>
                    <li><strong>太乙元真保命長生經</strong> - 1章</li>
                    <li><strong>抱朴子（抱朴子內篇）</strong> - 38章</li>
                    <li><strong>洞玄靈寶無量度人經訣音義</strong> - 3章</li>
                </ul>
                <p>📊 <strong>統計資訊：</strong> 總計6部經典，45個章節，102,050字</p>
            </div>
        `;
        
        translatedContentDiv.innerHTML = `
            <div class="welcome-message">
                <h4>歡迎使用道教經典翻譯系統 v2.0</h4>
                <p>🎯 <strong>功能特色：</strong></p>
                <ul>
                    <li>📚 <strong>6部經典</strong> - 包含45個章節，超過10萬字</li>
                    <li>🔍 <strong>智能選擇</strong> - 書籍和章節雙重選擇系統</li>
                    <li>📖 <strong>對照閱讀</strong> - 原文與譯文並排顯示</li>
                    <li>🎛️ <strong>多種模式</strong> - 支援不同的閱讀模式</li>
                    <li>📜 <strong>向後相容</strong> - 保留舊版經典存取</li>
                </ul>
                <p>請從上方選擇經典開始閱讀。</p>
            </div>
        `;
    }

    // 全域函數（供HTML調用）
    window.showSystemInfo = function() {
        alert(`道教經典翻譯系統 v2.0

📊 系統統計：
• 經典總數：6部
• 章節總數：45章
• 總字數：102,050字

🎯 功能特色：
• 智能書籍和章節選擇
• 原文與翻譯對照顯示
• 多種閱讀模式切換
• 向後相容舊版經典

🔗 專案網址：https://github.com/your-repo/taoism-translation`);
    };

    window.showHelp = function() {
        alert(`使用說明

📚 選擇經典：
1. 從「選擇經典」下拉選單選擇書籍
2. 系統會自動載入章節列表
3. 選擇要閱讀的章節

🎛️ 功能按鈕：
• ⬅️➡️ 上一章/下一章：快速導航
• 🔄 切換顯示模式：原文/翻譯/對照

📜 舊版經典：
• 可存取之前版本的經典
• 保持向後相容性

💡 小貼士：
• 支援鍵盤方向鍵導航
• 可使用滑鼠滾輪閱讀長篇內容`);
    };

    // 鍵盤快捷鍵
    document.addEventListener('keydown', (e) => {
        if (!currentBook) return;
        
        switch (e.key) {
            case 'ArrowLeft':
                if (!prevButton.disabled) navigatePrevChapter();
                break;
            case 'ArrowRight':
                if (!nextButton.disabled) navigateNextChapter();
                break;
            case ' ':
                e.preventDefault();
                toggleViewMode();
                break;
        }
    });

    // 初始化系統
    initializeSystem();
    showWelcomeMessage();
});
// 道教經典翻譯系統 v2.0 - JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // 密碼驗證邏輯
    const passwordOverlay = document.getElementById('password-overlay');
    const passwordInput = document.getElementById('password-input');
    const passwordSubmit = document.getElementById('password-submit');
    const passwordError = document.getElementById('password-error');
    const mainContent = document.getElementById('main-content');

    const correctPassword = "福生無量天尊";
    let passwordEntered = false;
    let pendingBookId = null;
    let pendingChapterIndex = 0;

    function isPasswordOverlayVisible() {
        return getComputedStyle(passwordOverlay).display !== 'none';
    }

    function checkPassword() {
        // 輸入框空白時直接按「進入」或 Enter，視同輸入密語
        const value = passwordInput.value.trim() || correctPassword;
        if (value === correctPassword) {
            passwordOverlay.style.display = 'none';
            passwordEntered = true;
            if (pendingBookId) {
                loadBook(pendingBookId, pendingChapterIndex);
                pendingBookId = null;
                pendingChapterIndex = 0;
            }
        } else {
            passwordError.textContent = '密語錯誤，請重試';
            passwordInput.value = '';
        }
    }

    passwordSubmit.addEventListener('click', checkPassword);
    passwordInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            checkPassword();
        }
    });

    // Tab：輸入框是空的時候自動帶入密語（再按一次 Tab 才移到「進入」按鈕）
    passwordInput.addEventListener('keydown', (event) => {
        if (event.key === 'Tab' && !event.shiftKey && !passwordInput.value) {
            event.preventDefault();
            passwordInput.value = correctPassword;
            passwordError.textContent = '';
        }
    });

    // 頁面載入時密語視窗就是開著的，先讓輸入框取得焦點，快捷鍵才能直接用
    if (isPasswordOverlayVisible()) {
        passwordInput.focus();
    }
    
    // 手機端優化：添加輸入事件監聽
    passwordInput.addEventListener('input', () => {
        passwordError.textContent = ''; // 清除錯誤訊息
    });
    
    // 確保密碼輸入框在顯示時獲得焦點
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                if (passwordOverlay.style.display === 'flex') {
                    setTimeout(() => {
                        passwordInput.focus();
                    }, 100);
                }
            }
        });
    });
    observer.observe(passwordOverlay, { attributes: true });

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

    // 書單由 docs/data/books.json 載入（python tools/build_web_data.py 依實際檔案產生）
    const DEFAULT_BOOK_CODE = 'DZ0756';  // 不需密語即可閱讀的書（太上老君說常清靜經注），以書籍編號比對
    let DEFAULT_BOOK_ID = null;
    let booksData = {};
    let webStats = { books: 0, chapters: 0, translated: 0 };

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
    async function initializeSystem() {
        populateLegacySelect();
        setupEventListeners();
        try {
            await loadBooksData();
        } catch (error) {
            console.error('載入書單失敗:', error);
            systemStatsDiv.textContent = '⚠️ 書單載入失敗，請重新整理頁面';
            return;
        }
        loadSystemStats();
        populateBookSelect();
        // 依序使用：網址指定的章節 → 上次讀到的章節 → 預設書籍
        openTarget(targetFromHash() || lastReadTarget() || { bookId: DEFAULT_BOOK_ID, chapterIndex: 0 });
    }

    // 章節網址 #書籍編號/章節編號（例如 #DZ0336/03），可分享或加入書籤
    const LAST_READ_KEY = 'taoism:lastRead';

    function bookCode(bookId) {
        const match = bookId.match(/_([A-Za-z]+\d+)$/);
        return match ? match[1] : bookId;
    }

    function findChapterTarget(code, number) {
        const bookId = Object.keys(booksData).find(id => bookCode(id) === code);
        if (!bookId) return null;
        const index = booksData[bookId].chapters.findIndex(chapter => chapter.number === number);
        return { bookId, chapterIndex: Math.max(index, 0) };
    }

    function targetFromHash() {
        const match = decodeURIComponent(location.hash).match(/^#([^/]+)\/(\d+)$/);
        return match ? findChapterTarget(match[1], match[2]) : null;
    }

    function lastReadTarget() {
        try {
            const saved = JSON.parse(localStorage.getItem(LAST_READ_KEY) || 'null');
            return saved ? findChapterTarget(saved.code, saved.number) : null;
        } catch (error) {
            return null;  // 無痕模式等情況下無法使用 localStorage
        }
    }

    function rememberChapter(bookId, chapter) {
        const code = bookCode(bookId);
        history.replaceState(null, '', `#${code}/${chapter.number}`);
        try {
            localStorage.setItem(LAST_READ_KEY, JSON.stringify({ code, number: chapter.number }));
        } catch (error) {
            // 無法記住閱讀位置時不影響閱讀
        }
    }

    // 開啟指定章節；需要密語的書先記下，通過密語後再開
    function openTarget(target) {
        if (target.bookId !== DEFAULT_BOOK_ID && !passwordEntered) {
            pendingBookId = target.bookId;
            pendingChapterIndex = target.chapterIndex;
            passwordOverlay.style.display = 'flex';
            return;
        }
        loadBook(target.bookId, target.chapterIndex);
    }

    // 手動修改網址或點選章節連結時切換章節
    window.addEventListener('hashchange', () => {
        const target = targetFromHash();
        if (target && !(target.bookId === currentBook && target.chapterIndex === currentChapterIndex)) {
            openTarget(target);
        }
    });

    // 載入書單
    async function loadBooksData() {
        const response = await fetch('data/books.json');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        webStats = data.stats;
        booksData = Object.fromEntries(
            data.books.map(book => [book.id, { title: book.title, chapters: book.chapters }])
        );
        DEFAULT_BOOK_ID = Object.keys(booksData).find(id => id.endsWith(`_${DEFAULT_BOOK_CODE}`))
            || Object.keys(booksData)[0];
    }

    // 載入系統統計
    function loadSystemStats() {
        systemStatsDiv.textContent =
            `📚 ${webStats.books} 部經典 | 📖 ${webStats.chapters} 個章節 | ✅ 已翻譯 ${webStats.translated} 章`;
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
            option.textContent = `第${chapter.number}章 - ${chapter.title}${chapter.translated ? '' : '（未翻譯）'}`;
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

        if (bookId !== DEFAULT_BOOK_ID && !passwordEntered) {
            pendingBookId = bookId;
            pendingChapterIndex = 0;
            passwordOverlay.style.display = 'flex';
            // Reset the dropdown to the current book to avoid confusion
            bookSelect.value = currentBook;
            return;
        }

        loadBook(bookId);
    }

    function loadBook(bookId, chapterIndex = 0) {
        if (!booksData[bookId]) return;
        currentBook = bookId;
        currentChapterIndex = chapterIndex;
        populateChapterSelect(bookId);

        // 預設選擇第一章（或網址、上次閱讀指定的章節）
        if (booksData[bookId].chapters.length > 0) {
            chapterSelect.value = chapterIndex;
            loadChapter(bookId, chapterIndex);
        }
        
        // 清除舊版選擇
        legacySelect.value = '';
        bookSelect.value = bookId;
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
        history.replaceState(null, '', location.pathname + location.search);

        // 清除新版選擇
        bookSelect.value = '';
        chapterSelect.disabled = true;
        chapterSelect.innerHTML = '<option value="">請先選擇經典</option>';
        currentBook = null;
        updateNavigationButtons();
    }

    // 原文以純文字顯示，避免內容中的 < > 被當成 HTML
    function showOriginalText(text) {
        const pre = document.createElement('pre');
        pre.textContent = text;
        originalContentDiv.replaceChildren(pre);
    }

    // 載入章節內容
    async function loadChapter(bookId, chapterIndex) {
        const bookData = booksData[bookId];
        const chapter = bookData.chapters[chapterIndex];
        
        if (!chapter) return;
        rememberChapter(bookId, chapter);

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
                showOriginalText(await originalResponse.text());
            } else {
                originalContentDiv.innerHTML = '<p>❌ 無法載入原文</p>';
            }

            // 載入翻譯（還只是模板的章節不顯示模板內容）
            if (!chapter.translated) {
                translatedContentDiv.innerHTML =
                    '<div class="untranslated-notice">📝 本章尚未翻譯，請先參閱古文原文。</div>';
                updateNavigationButtons();
                return;
            }
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
                showOriginalText(await originalResponse.text());
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
        
        // 章節最多的前五部經典
        const books = Object.values(booksData);
        const topBooks = [...books].sort((a, b) => b.chapters.length - a.chapters.length).slice(0, 5);
        const otherCount = books.length - topBooks.length;
        const topList = topBooks
            .map(book => `<li><strong>${book.title}</strong> - ${book.chapters.length}章</li>`)
            .join('');

        originalContentDiv.innerHTML = `
            <div class="welcome-message">
                <h4>系統說明</h4>
                <p>🏛️ <strong>主要收錄經典：</strong></p>
                <ul>
                    ${topList}
                    ${otherCount > 0 ? `<li><strong>其他經典</strong> - ${otherCount}部</li>` : ''}
                </ul>
                <p>📊 <strong>統計資訊：</strong> 總計${webStats.books}部經典，${webStats.chapters}個章節，已翻譯${webStats.translated}章</p>
            </div>
        `;

        translatedContentDiv.innerHTML = `
            <div class="welcome-message">
                <h4>歡迎使用道教經典翻譯系統 v2.0</h4>
                <p>🎯 <strong>功能特色：</strong></p>
                <ul>
                    <li>📚 <strong>${webStats.books}部經典</strong> - 包含${webStats.chapters}個章節，豐富的道教典籍</li>
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
• 經典總數：${webStats.books}部
• 章節總數：${webStats.chapters}章
• 已翻譯：${webStats.translated}章
• 主要經典：南華真經口義、抱朴子內篇等

🎯 功能特色：
• 智能書籍和章節選擇
• 原文與翻譯對照顯示
• 多種閱讀模式切換
• 向後相容舊版經典

🔗 專案網址：https://github.com/yehwanlan/Taoism`);
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
        // 密語視窗開著時，按鍵交給密語輸入框處理
        if (!currentBook || isPasswordOverlayVisible()) return;
        
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
});
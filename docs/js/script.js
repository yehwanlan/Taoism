// JavaScript for dynamic content loading
document.addEventListener('DOMContentLoaded', () => {
    const originalContentDiv = document.getElementById('original-content');
    const translatedContentDiv = document.getElementById('translated-content');
    const nav = document.querySelector('nav');

    // SCRIPTURES_START
    const scriptures = {
        "太上太清天童護命妙經": { original: "source_texts/太上太清天童護命妙經.txt", translation: "translations/太上太清天童護命妙經.md" },
        "本經陰符七術": { original: "source_texts/本經陰符七術.text", translation: "translations/本經陰符七術.md" },
        "雲笈七籤": { original: "source_texts/雲笈七籤.txt", translation: "translations/雲笈七籤.md" },
        "雲笈七籤121": { original: "source_texts/雲笈七籤121.txt", translation: "translations/雲笈七籤121.md" },
        "雲笈七籤33": { original: "source_texts/雲笈七籤33.txt", translation: "translations/雲笈七籤33.md" },
        "雲笈七籤60中山玉櫃服氣經": { original: "source_texts/雲笈七籤60中山玉櫃服氣經.txt", translation: "translations/雲笈七籤60中山玉櫃服氣經.md" },
        "黃帝陰符經": { original: "source_texts/黃帝陰符經.txt", translation: "translations/黃帝陰符經.md" }
    };
    // SCRIPTURES_END

    // Create a dropdown (select) element for scripture selection
    const selectElement = document.createElement('select');
    selectElement.id = 'scripture-select';

    for (const key in scriptures) {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = key;
        selectElement.appendChild(option);
    }
    nav.appendChild(selectElement);

    // Function to load and display scripture content
    async function loadScripture(scriptureName) {
        const paths = scriptures[scriptureName];
        if (!paths) {
            originalContentDiv.innerHTML = "<p>經文未找到。</p>";
            translatedContentDiv.innerHTML = "<p>經文未找到。</p>";
            return;
        }

        try {
            // Fetch original text
            const originalResponse = await fetch(paths.original);
            if (!originalResponse.ok) {
                throw new Error(`無法載入原文: ${originalResponse.statusText}`);
            }
            const originalText = await originalResponse.text();
            originalContentDiv.textContent = originalText; // Use textContent to preserve formatting

            // Fetch translated text (Markdown)
            const translatedResponse = await fetch(paths.translation);
            if (!translatedResponse.ok) {
                throw new Error(`無法載入譯文: ${translatedResponse.statusText}`);
            }
            const translatedMarkdown = await translatedResponse.text();
            // Convert Markdown to HTML using marked.js
            translatedContentDiv.innerHTML = marked.parse(translatedMarkdown);

        } catch (error) {
            console.error("載入經文時發生錯誤:", error);
            originalContentDiv.innerHTML = `<p>載入原文失敗: ${error.message}</p>`;
            translatedContentDiv.innerHTML = `<p>載入譯文失敗: ${error.message}</p>`;
        }
    }

    // Event listener for dropdown change
    selectElement.addEventListener('change', (event) => {
        loadScripture(event.target.value);
    });

    // Load the first scripture by default
    if (Object.keys(scriptures).length > 0) {
        selectElement.value = Object.keys(scriptures)[0]; // Set dropdown to first item
        loadScripture(Object.keys(scriptures)[0]);
    }
});
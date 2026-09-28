#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專門修復 DZ0336 太上洞玄灵宝业报因缘经 的結構問題

根據meta description中的信息，這本書應該有以下結構：
- 首為《开度品》
- 次為《善对》《恶报》《受罪》三品  
- 再次為《忏悔》《奉戒》等八品
- 再次《生神》《弘教》等九品

但現在的文件只有卷的標題，缺少具體的品的內容。
"""

import requests
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
import sys

# 讓 `python tools/xxx.py` 也能找到 core 套件
sys.path.append(str(Path(__file__).parent.parent))
from core.unicode_handler import safe_print


class DZ0336StructureFixer:
    """DZ0336結構修復器"""
    
    def __init__(self):
        self.base_url = "https://www.shidianguji.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 根據meta description定義的預期結構
        self.expected_structure = {
            "卷之一": ["开度品第一"],
            "卷之二": ["善对品第二"],
            "卷之三": ["恶报品第三", "受罪品第四"],  # 推測
            "卷之四": ["忏悔品第五"],  # 從現有文件可知
            "卷之五": ["奉戒品第六"],  # 從現有文件可知
            "卷之六": ["品第七"],  # 待確認
            "卷之七": ["品第八"],  # 待確認
            "卷之八": ["品第九"],  # 待確認
            "卷之九": ["品第十"],  # 待確認
            "卷之十": ["生神品", "弘教品"]  # 推測
        }
        
    def analyze_actual_structure(self):
        """分析實際的網站結構"""
        safe_print("🔍 分析實際網站結構...")
        
        # 已知的章節ID和對應關係
        known_chapters = {
            "DZ0336_1": "太上洞玄灵宝业报因缘经卷之一",
            "DZ0336_2": "开度品第一",
            "DZ0336_3": "太上洞玄灵宝业报因缘经卷之二", 
            "DZ0336_7": "太上洞玄灵宝紫报因缘经卷之三",
            "DZ0336_9": "太上洞玄灵宝业报因缘经卷之四",
            "DZ0336_12": "太上洞玄灵宝业报因缘经卷之五",
            "DZ0336_19": "太上洞玄灵宝业报因缘经卷之六",
            "DZ0336_22": "太上洞玄灵宝业报因缘经卷之七",
            "DZ0336_26": "太上洞玄灵宝业报因缘经卷之八",
            "DZ0336_28": "太上洞玄灵宝业报因缘经卷之九",
            "DZ0336_33": "太上洞玄灵宝业报因缘经卷之十"
        }
        
        # 分析每個章節ID之間的間隔，推測缺失的章節
        chapter_ids = [1, 2, 3, 7, 9, 12, 19, 22, 26, 28, 33]
        
        missing_ranges = []
        for i in range(len(chapter_ids) - 1):
            current = chapter_ids[i]
            next_id = chapter_ids[i + 1]
            if next_id - current > 1:
                missing_ranges.append((current + 1, next_id - 1))
        
        safe_print("📊 章節ID分析:")
        safe_print(f"已知章節ID: {chapter_ids}")
        safe_print(f"可能缺失的ID範圍: {missing_ranges}")
        
        return missing_ranges, known_chapters
    
    def probe_missing_chapters(self, missing_ranges):
        """探測缺失的章節"""
        safe_print("\n🔎 探測缺失章節...")
        
        found_chapters = []
        
        for start, end in missing_ranges:
            safe_print(f"探測範圍 DZ0336_{start} 到 DZ0336_{end}:")
            
            for chapter_id in range(start, end + 1):
                chapter_key = f"DZ0336_{chapter_id}"
                url = f"{self.base_url}/book/DZ0336/chapter/{chapter_key}"
                
                safe_print(f"  測試: {chapter_key}")
                
                try:
                    response = self.session.get(url, timeout=5)
                    if response.status_code == 200:
                        # 嘗試提取標題
                        soup = BeautifulSoup(response.text, 'html.parser')
                        title_elem = soup.find('h1', class_='Goq6DYSE')
                        if title_elem:
                            title = title_elem.get_text().strip()
                            safe_print(f"    ✅ 找到: {title}")
                            found_chapters.append({
                                'chapter_id': chapter_key,
                                'title': title,
                                'url': url
                            })
                        else:
                            safe_print(f"    ⚠️  響應成功但無標題")
                    else:
                        safe_print(f"    ❌ HTTP {response.status_code}")
                        
                except Exception as e:
                    safe_print(f"    ❌ 錯誤: {e}")
                
                time.sleep(1)  # 避免請求過快
        
        return found_chapters
    
    def probe_extended_chapters(self, max_chapter=40):
        """探測擴展範圍的章節（用於發現更多章節）"""
        safe_print(f"\n🔍 探測擴展章節範圍 (DZ0336_34 到 DZ0336_{max_chapter})...")
        
        found_chapters = []
        
        for chapter_id in range(34, max_chapter + 1):
            chapter_key = f"DZ0336_{chapter_id}"
            url = f"{self.base_url}/book/DZ0336/chapter/{chapter_key}"
            
            safe_print(f"  測試: {chapter_key}")
            
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    # 嘗試提取標題
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_elem = soup.find('h1', class_='Goq6DYSE')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        safe_print(f"    ✅ 找到: {title}")
                        found_chapters.append({
                            'chapter_id': chapter_key,
                            'title': title,
                            'url': url
                        })
                    else:
                        safe_print(f"    ⚠️  響應成功但無標題")
                else:
                    safe_print(f"    ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                safe_print(f"    ❌ 錯誤: {e}")
            
            time.sleep(1)  # 避免請求過快
        
        return found_chapters
    
    def crawl_chapter_content(self, chapter_info):
        """爬取章節內容"""
        safe_print(f"\n📖 爬取章節: {chapter_info['title']}")
        
        try:
            # 嘗試API端點
            api_url = f"{self.base_url}/api/book/DZ0336/chapter/{chapter_info['chapter_id']}"
            
            response = self.session.get(api_url, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    content = self._extract_content_from_api_response(data)
                    if content:
                        # 嘗試從內容中提取實際的品名
                        actual_title = self._extract_actual_title_from_content(content)
                        if actual_title and actual_title != chapter_info['title']:
                            safe_print(f"  📝 發現實際品名: {actual_title}")
                            chapter_info['actual_title'] = actual_title
                        return content
                except json.JSONDecodeError:
                    pass
            
            # 如果API失敗，嘗試直接訪問頁面
            response = self.session.get(chapter_info['url'], timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                content = self._extract_content_from_html(soup)
                if content:
                    # 嘗試從內容中提取實際的品名
                    actual_title = self._extract_actual_title_from_content(content)
                    if actual_title and actual_title != chapter_info['title']:
                        safe_print(f"  📝 發現實際品名: {actual_title}")
                        chapter_info['actual_title'] = actual_title
                    return content
            
            safe_print(f"❌ 無法獲取內容")
            return None
            
        except Exception as e:
            safe_print(f"❌ 爬取失敗: {e}")
            return None
    
    def _extract_content_from_api_response(self, data):
        """從API響應中提取內容"""
        content_parts = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['content', 'text', 'body'] and isinstance(value, str):
                        text = value.strip()
                        if len(text) > 20 and re.search(r'[\u4e00-\u9fff]', text):
                            # 清理HTML標籤
                            clean_text = re.sub(r'<[^>]+>', '', text)
                            if clean_text.strip():
                                content_parts.append(clean_text.strip())
                    else:
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(data)
        
        if content_parts:
            return '\n\n'.join(content_parts)
        return None
    
    def _extract_content_from_html(self, soup):
        """從HTML中提取內容"""
        # 尋找主要內容區域
        content_selectors = [
            'main.read-layout-main article.chapter-reader',
            '.chapter-content',
            '.book-content',
            '.text-content'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content_parts = []
                for element in elements[0].find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                    text = element.get_text().strip()
                    if text and len(text) > 3:
                        content_parts.append(text)
                
                if content_parts:
                    return '\n\n'.join(content_parts)
        
        return None
    
    def _extract_actual_title_from_content(self, content):
        """從內容中提取實際的品名"""
        lines = content.split('\n')
        
        for line in lines[:10]:  # 檢查前10行
            line = line.strip()
            
            # 尋找品名模式
            if '品第' in line and len(line) < 30:
                # 清理品名
                clean_title = line.replace('太上洞玄灵宝业报因缘经', '').strip()
                if clean_title and clean_title != line:
                    return clean_title
                return line
            
            # 尋找其他可能的章節標題
            if line and len(line) < 50 and not line.startswith('#'):
                # 檢查是否包含品、章、卷等關鍵字
                if any(keyword in line for keyword in ['品', '章', '卷']):
                    if '太上洞玄' not in line:  # 排除書名
                        return line
        
        return None
    
    def save_new_chapter(self, book_folder, chapter_info, content):
        """保存新發現的章節"""
        # 使用實際的品名作為標題（如果有的話）
        display_title = chapter_info.get('actual_title', chapter_info['title'])
        
        # 清理標題作為文件名
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', display_title)
        
        # 確定文件編號
        source_folder = book_folder / "原文"
        existing_files = list(source_folder.glob("*.txt"))
        next_number = len(existing_files) + 1
        
        filename = f"{next_number:02d}_{clean_title}.txt"
        file_path = source_folder / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {display_title}\n\n")
            f.write(content)
        
        safe_print(f"✅ 已保存: {filename}")
        
        # 更新chapter_info以便後續使用
        chapter_info['display_title'] = display_title
        chapter_info['filename'] = filename
        
        return filename
    
    def update_readme(self, book_folder, new_chapters):
        """更新README文件"""
        readme_path = book_folder / "README.md"
        if not readme_path.exists():
            return
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新章節總數
            total_chapters = len(list((book_folder / "原文").glob("*.txt")))
            content = re.sub(r'總共 \d+ 個章節', f'總共 {total_chapters} 個章節', content)
            
            # 添加新章節到列表
            if "## 章節列表" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith("## 章節列表"):
                        # 找到列表結束位置
                        j = i + 1
                        while j < len(lines) and (lines[j].startswith('- ') or lines[j].strip() == ''):
                            j += 1
                        
                        # 添加新章節
                        for chapter in new_chapters:
                            chapter_num = len(list((book_folder / "原文").glob("*.txt")))
                            new_line = f"- {chapter_num:02d}. {chapter['title']}"
                            lines.insert(j, new_line)
                            j += 1
                        break
                
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
            
        except Exception as e:
            safe_print(f"⚠️  更新README失敗: {e}")
    
    def fix_dz0336_structure(self):
        """修復DZ0336結構"""
        safe_print("🔧 開始修復 DZ0336 結構問題")
        safe_print("=" * 60)
        
        # 1. 分析實際結構
        missing_ranges, known_chapters = self.analyze_actual_structure()
        
        # 2. 探測缺失章節
        found_chapters = self.probe_missing_chapters(missing_ranges)
        
        # 3. 探測擴展範圍的章節（34-40）
        extended_chapters = self.probe_extended_chapters(40)
        found_chapters.extend(extended_chapters)
        
        if not found_chapters:
            safe_print("\n❌ 沒有找到新的章節")
            return False
        
        safe_print(f"\n🎯 找到 {len(found_chapters)} 個新章節:")
        for chapter in found_chapters:
            safe_print(f"  - {chapter['chapter_id']}: {chapter['title']}")
        
        # 4. 檢查目標文件夾
        book_folder = Path("../docs/source_texts/太上洞玄灵宝业报因缘经_DZ0336")
        if not book_folder.exists():
            safe_print(f"❌ 找不到目標文件夾: {book_folder}")
            return False
        
        # 5. 爬取並保存新章節
        success_count = 0
        saved_chapters = []
        
        for chapter in found_chapters:
            content = self.crawl_chapter_content(chapter)
            if content and len(content) > 100:  # 確保內容有意義
                filename = self.save_new_chapter(book_folder, chapter, content)
                success_count += 1
                saved_chapters.append(chapter)
                
                # 同時生成翻譯模板
                self._generate_translation_template(book_folder, chapter, content)
            
            time.sleep(2)  # 避免請求過快
        
        # 6. 更新README
        if saved_chapters:
            self.update_readme(book_folder, saved_chapters)
        
        safe_print(f"\n🎉 修復完成！成功添加 {success_count}/{len(found_chapters)} 個章節")
        
        if success_count > 0:
            safe_print("\n📋 建議檢查以下內容:")
            safe_print("1. 新添加的原文文件內容是否正確")
            safe_print("2. 翻譯模板是否已生成")
            safe_print("3. README.md 是否已更新")
            safe_print("4. 章節順序是否合理")
        
        return success_count > 0
    
    def _generate_translation_template(self, book_folder, chapter_info, content):
        """生成翻譯模板"""
        translation_folder = Path(f"../docs/translations/太上洞玄灵宝业报因缘经_DZ0336")
        translation_folder.mkdir(parents=True, exist_ok=True)
        
        # 使用實際的品名作為標題
        display_title = chapter_info.get('display_title', chapter_info['title'])
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', display_title)
        
        # 確定文件編號
        existing_files = list(translation_folder.glob("*.md"))
        next_number = len(existing_files) + 1
        
        filename = f"{next_number:02d}_{clean_title}.md"
        file_path = translation_folder / filename
        
        template_content = f"""# {display_title}

## 原文

{content}

## 翻譯

[此處應為現代中文翻譯]

原文字數：{len(content)} 字
建議：請使用AI翻譯工具或人工翻譯此段落。

翻譯要點：
1. 保持原文意思
2. 使用現代中文表達
3. 保留重要的古代術語
4. 添加必要的註解說明

## 註解

**重要詞彙：**
- [待補充]

**文化背景：**
- [待補充]

**翻譯要點：**
- [待補充]

---
*翻譯時間：{time.strftime('%Y-%m-%d %H:%M:%S')}*
*翻譯方式：自動生成模板*
*章節ID：{chapter_info['chapter_id']}*
*實際品名：{display_title}*
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        safe_print(f"📝 已生成翻譯模板: {filename}")


def main():
    """主函數"""
    fixer = DZ0336StructureFixer()
    
    success = fixer.fix_dz0336_structure()
    
    if success:
        safe_print("\n🎊 DZ0336 結構修復成功！")
        safe_print("💡 現在這本經典應該包含了所有缺失的品（章節）")
    else:
        safe_print("\n❌ DZ0336 結構修復失敗")
        safe_print("💡 可能所有章節都已經存在，或者網絡連接有問題")


if __name__ == "__main__":
    main()
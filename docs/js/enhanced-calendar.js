// 增強版萬年曆主程式
class EnhancedCalendar {
    constructor() {
        this.currentDate = new Date();
        this.selectedDate = null;
        this.currentView = 'calendar';
        this.filters = {
            goodDays: true,
            deityDays: true,
            badDays: false
        };
        
        // 初始化功能模組
        this.lunarCalendar = new LunarCalendar();
        this.fortuneChecker = new FortuneChecker();
        this.deityChecker = new DeityBirthdayChecker();
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateTodayInfo();
        this.renderCalendar();
        this.updateStats();
    }

    setupEventListeners() {
        // 視圖切換
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.dataset.view);
            });
        });

        // 月份控制
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.changeMonth(-1);
        });
        
        document.getElementById('nextMonth').addEventListener('click', () => {
            this.changeMonth(1);
        });
        
        document.getElementById('todayBtn').addEventListener('click', () => {
            this.goToToday();
        });

        // 篩選器
        document.getElementById('filterGoodDays').addEventListener('change', (e) => {
            this.filters.goodDays = e.target.checked;
            this.renderCurrentView();
        });
        
        document.getElementById('filterDeityDays').addEventListener('change', (e) => {
            this.filters.deityDays = e.target.checked;
            this.renderCurrentView();
        });
        
        document.getElementById('filterBadDays').addEventListener('change', (e) => {
            this.filters.badDays = e.target.checked;
            this.renderCurrentView();
        });

        // 彈窗關閉
        document.getElementById('modalClose').addEventListener('click', () => {
            this.closeModal();
        });
        
        document.getElementById('dateModal').addEventListener('click', (e) => {
            if (e.target.id === 'dateModal') {
                this.closeModal();
            }
        });
    }

    // 更新今日資訊
    updateTodayInfo() {
        const today = new Date();
        const dateStr = this.formatDate(today);
        const lunarStr = this.lunarCalendar.formatLunarDate(
            this.lunarCalendar.solarToLunar(today.getFullYear(), today.getMonth() + 1, today.getDate())
        );
        
        // 日期（陽曆 + 農曆）
        document.getElementById('todayDate').textContent = `${dateStr} (${lunarStr})`;
        
        // 六十甲子
        const stemBranch = this.fortuneChecker.getStemBranch(today);
        document.getElementById('todayStemBranch').textContent = stemBranch;
        
        // 吉凶
        const fortune = this.fortuneChecker.checkFortune(today);
        const fortuneEl = document.getElementById('todayFortune');
        fortuneEl.textContent = this.getFortuneText(fortune.status);
        fortuneEl.className = `value fortune-status ${fortune.status}`;
        
        // 神明聖誕（使用農曆）
        const deities = this.deityChecker.getDeityBirthdays(today);
        const deitiesEl = document.getElementById('todayDeitiesValue');
        if (deities.length > 0) {
            deitiesEl.innerHTML = deities.map(d => 
                `<span style="color: var(--primary-gold); font-weight: bold;">🏮 ${d.name}</span>`
            ).join('、');
        } else {
            deitiesEl.textContent = '無';
        }
    }

    // 渲染月曆
    renderCalendar() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // 更新月份標題
        document.getElementById('currentMonth').textContent = 
            `${year} 年 ${month + 1} 月`;
        
        // 獲取月份資訊
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const prevLastDay = new Date(year, month, 0);
        
        const firstDayOfWeek = firstDay.getDay();
        const daysInMonth = lastDay.getDate();
        const daysInPrevMonth = prevLastDay.getDate();
        
        // 生成日曆格子
        let html = '';
        let dayCount = 1;
        let nextMonthDay = 1;
        
        // 總共需要顯示的格子數（確保完整週）
        const totalCells = Math.ceil((firstDayOfWeek + daysInMonth) / 7) * 7;
        
        for (let i = 0; i < totalCells; i++) {
            let date, isCurrentMonth, isToday;
            
            if (i < firstDayOfWeek) {
                // 上個月的日期
                date = new Date(year, month - 1, daysInPrevMonth - firstDayOfWeek + i + 1);
                isCurrentMonth = false;
            } else if (dayCount <= daysInMonth) {
                // 當前月的日期
                date = new Date(year, month, dayCount);
                isCurrentMonth = true;
                dayCount++;
            } else {
                // 下個月的日期
                date = new Date(year, month + 1, nextMonthDay);
                isCurrentMonth = false;
                nextMonthDay++;
            }
            
            // 檢查是否為今天
            const today = new Date();
            isToday = date.toDateString() === today.toDateString();
            
            // 獲取日期資訊
            const dayInfo = this.getDayInfo(date);
            
            // 檢查是否應該顯示（根據篩選器）
            if (!this.shouldShowDay(dayInfo)) {
                continue;
            }
            
            // 生成日期格子
            html += this.createDayCell(date, dayInfo, isCurrentMonth, isToday);
        }
        
        document.getElementById('calendarDays').innerHTML = html;
        
        // 添加點擊事件
        document.querySelectorAll('.calendar-day').forEach(cell => {
            cell.addEventListener('click', (e) => {
                const dateStr = e.currentTarget.dataset.date;
                this.showDateDetail(new Date(dateStr));
            });
        });
    }

    // 創建日期格子
    createDayCell(date, dayInfo, isCurrentMonth, isToday) {
        const classes = ['calendar-day'];
        if (!isCurrentMonth) classes.push('other-month');
        if (isToday) classes.push('today');
        if (dayInfo.isGoodDay) classes.push('good-day');
        if (dayInfo.isBadDay) classes.push('bad-day');
        if (dayInfo.hasDeity) classes.push('deity-day');
        
        const indicators = [];
        if (dayInfo.isGoodDay) indicators.push('<span class="indicator good">吉</span>');
        if (dayInfo.isBadDay) indicators.push('<span class="indicator bad">凶</span>');
        if (dayInfo.hasDeity) indicators.push('<span class="indicator deity">🏮</span>');
        
        // 獲取農曆日期
        const lunar = this.lunarCalendar.solarToLunar(date.getFullYear(), date.getMonth() + 1, date.getDate());
        const lunarDay = lunar.day === 1 ? `${lunar.month}/${lunar.day}` : lunar.day;
        
        return `
            <div class="${classes.join(' ')}" data-date="${date.toISOString()}">
                <div class="day-number">${date.getDate()}</div>
                <div class="day-stem-branch">${dayInfo.stemBranch}</div>
                <div class="day-lunar" style="font-size: 0.7rem; color: #999;">${lunarDay}</div>
                <div class="day-indicators">${indicators.join('')}</div>
            </div>
        `;
    }

    // 渲染列表視圖
    renderList() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        let html = '';
        const specialDays = [];
        
        // 收集特殊日期
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const dayInfo = this.getDayInfo(date);
            
            if (!this.shouldShowDay(dayInfo)) continue;
            
            if (dayInfo.isGoodDay || dayInfo.isBadDay || dayInfo.hasDeity) {
                specialDays.push({ date, dayInfo });
            }
        }
        
        // 生成列表項目
        specialDays.forEach(({ date, dayInfo }) => {
            html += this.createListItem(date, dayInfo);
        });
        
        if (html === '') {
            html = '<div style="text-align: center; padding: 2rem; color: #999;">本月無符合篩選條件的特殊日期</div>';
        }
        
        document.getElementById('listContainer').innerHTML = html;
        
        // 添加點擊事件
        document.querySelectorAll('.list-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const dateStr = e.currentTarget.dataset.date;
                this.showDateDetail(new Date(dateStr));
            });
        });
    }

    // 創建列表項目
    createListItem(date, dayInfo) {
        const classes = ['list-item'];
        if (dayInfo.isGoodDay) classes.push('good-day');
        if (dayInfo.isBadDay) classes.push('bad-day');
        if (dayInfo.hasDeity) classes.push('deity-day');
        
        const details = [];
        details.push(`<div class="list-detail">📅 六十甲子：${dayInfo.stemBranch}</div>`);
        
        if (dayInfo.fortune) {
            const statusText = this.getFortuneText(dayInfo.fortune.status);
            details.push(`<div class="list-detail">🔮 ${statusText}：${dayInfo.fortune.description}</div>`);
        }
        
        if (dayInfo.deities.length > 0) {
            const deityNames = dayInfo.deities.map(d => `${d.name}（${d.type}）`).join('、');
            details.push(`<div class="list-detail">🏮 神明聖誕：${deityNames}</div>`);
        }
        
        return `
            <div class="${classes.join(' ')}" data-date="${date.toISOString()}">
                <div class="list-date">${this.formatDate(date)}</div>
                <div class="list-content">${details.join('')}</div>
            </div>
        `;
    }

    // 獲取日期資訊
    getDayInfo(date) {
        const stemBranch = this.fortuneChecker.getStemBranch(date);
        const fortune = this.fortuneChecker.checkFortune(date);
        const deities = this.deityChecker.getDeityBirthdays(date);  // 使用農曆
        
        return {
            stemBranch,
            fortune,
            deities,
            isGoodDay: fortune.status === 'good',
            isBadDay: fortune.status === 'bad',
            hasDeity: deities.length > 0
        };
    }

    // 檢查是否應該顯示該日期
    shouldShowDay(dayInfo) {
        if (dayInfo.isGoodDay && !this.filters.goodDays) return false;
        if (dayInfo.isBadDay && !this.filters.badDays) return false;
        if (dayInfo.hasDeity && !this.filters.deityDays) return false;
        
        // 如果沒有任何特殊屬性，在月曆視圖中總是顯示
        if (this.currentView === 'calendar') return true;
        
        // 在列表視圖中，只顯示有特殊屬性的日期
        return dayInfo.isGoodDay || dayInfo.isBadDay || dayInfo.hasDeity;
    }

    // 顯示日期詳情
    showDateDetail(date) {
        this.selectedDate = date;
        const dayInfo = this.getDayInfo(date);
        const lunar = this.lunarCalendar.solarToLunar(date.getFullYear(), date.getMonth() + 1, date.getDate());
        const lunarStr = this.lunarCalendar.formatLunarDate(lunar);
        
        // 設定標題（陽曆 + 農曆）
        document.getElementById('modalDate').textContent = `${this.formatDate(date)} (${lunarStr})`;
        
        // 六十甲子
        document.getElementById('modalStemBranch').textContent = dayInfo.stemBranch;
        
        // 吉凶
        const fortuneHtml = `
            <div class="status fortune-status ${dayInfo.fortune.status}">
                ${this.getFortuneText(dayInfo.fortune.status)}
            </div>
            <div class="description">${dayInfo.fortune.description}</div>
        `;
        document.getElementById('modalFortune').innerHTML = fortuneHtml;
        
        // 神明聖誕
        const deitiesSection = document.getElementById('modalDeitiesSection');
        if (dayInfo.deities.length > 0) {
            deitiesSection.style.display = 'block';
            const deitiesHtml = dayInfo.deities.map(deity => `
                <div class="deity-item">
                    <div class="deity-name">${deity.name}</div>
                    <span class="deity-type">${deity.type}</span>
                    ${deity.note ? `<span class="deity-note">${deity.note}</span>` : ''}
                </div>
            `).join('');
            document.getElementById('modalDeities').innerHTML = deitiesHtml;
        } else {
            deitiesSection.style.display = 'none';
        }
        
        // 顯示彈窗
        document.getElementById('dateModal').classList.remove('hidden');
    }

    // 關閉彈窗
    closeModal() {
        document.getElementById('dateModal').classList.add('hidden');
    }

    // 切換視圖
    switchView(view) {
        this.currentView = view;
        
        // 更新按鈕狀態
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });
        
        // 切換視圖顯示
        document.getElementById('calendarView').classList.toggle('hidden', view !== 'calendar');
        document.getElementById('listView').classList.toggle('hidden', view !== 'list');
        
        // 渲染對應視圖
        this.renderCurrentView();
    }

    // 渲染當前視圖
    renderCurrentView() {
        if (this.currentView === 'calendar') {
            this.renderCalendar();
        } else {
            this.renderList();
        }
        this.updateStats();
    }

    // 改變月份
    changeMonth(delta) {
        this.currentDate.setMonth(this.currentDate.getMonth() + delta);
        this.renderCurrentView();
    }

    // 回到今天
    goToToday() {
        this.currentDate = new Date();
        this.renderCurrentView();
    }

    // 更新統計
    updateStats() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        let goodDays = 0;
        let badDays = 0;
        let deityDays = 0;
        
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const dayInfo = this.getDayInfo(date);
            
            if (dayInfo.isGoodDay) goodDays++;
            if (dayInfo.isBadDay) badDays++;
            if (dayInfo.hasDeity) deityDays++;
        }
        
        document.getElementById('statGoodDays').textContent = goodDays;
        document.getElementById('statBadDays').textContent = badDays;
        document.getElementById('statDeityDays').textContent = deityDays;
    }

    // 格式化日期
    formatDate(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
        const weekday = weekdays[date.getDay()];
        
        return `${year} 年 ${month} 月 ${day} 日 星期${weekday}`;
    }

    // 獲取吉凶文字
    getFortuneText(status) {
        const texts = {
            'good': '✅ 拜拜好日子',
            'bad': '❌ 不宜拜拜',
            'neutral': '⚠️ 平吉'
        };
        return texts[status] || '未知';
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
    new EnhancedCalendar();
});

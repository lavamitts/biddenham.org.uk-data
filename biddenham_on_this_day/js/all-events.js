let viewDate = new Date();
const rootPath = 'https://raw.githubusercontent.com/lavamitts/on-this-day/refs/heads/main/';

// 1. Create a helper function for the scroll action
function scrollToTop() {
    const topElement = document.getElementById('inner-top');
    if (topElement) {
        topElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

async function updateDisplay(targetDate) {
    const d = targetDate.getDate();
    const m = targetDate.getMonth() + 1;

    // Force 2-digit padding
    const dayStr = d < 10 ? '0' + d : '' + d;
    const monthStr = m < 10 ? '0' + m : '' + m;

    const lookupKey = `${dayStr}-${monthStr}`;
    const fileName = `${monthStr}.json`;

    // 1. Initialise the Layout Shell (Buttons and Title)
    renderLayoutShell(targetDate);

    // 2. Fetch and Render History
    fetchAndRenderData(
        `${rootPath}data/history/${fileName}`,
        'otd-history-list',
        lookupKey,
        renderHistoryItem
    );

    // 3. Fetch and Render Marquee
    fetchAndRenderData(
        `${rootPath}data/marquee/${fileName}`,
        'otd-marquee-list',
        lookupKey,
        renderMarqueeItem
    );
}

function renderLayoutShell(date) {
    const container = document.querySelector('.otd-main-container');
    if (!container) return;

    const dateHeading = date.toLocaleDateString('en-GB', {
        weekday: 'long',
        day: 'numeric',
        month: 'long'
    });

    // Format current viewDate to YYYY-MM-DD for the date input value
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateValue = `${year}-${month}-${day}`;

    container.innerHTML = `
        <div id="inner-top" class="otd-card" style="border: 1px solid #ccc; padding: 1rem; border-radius: 5px;">

            <h2 style="text-align: center;">${dateHeading}</h2>
            
            <div class="otd-nav">
                <button id="otd-prev">&lt;&lt;</button>
                <button id="otd-today">Today</button>
                <button id="otd-next">&gt;&gt;</button>
                <div>
                    <input type="date" id="otd-date-input" value="${dateValue}">
                    <button id="otd-go">Go</button>
                </div>
            </div>

            <hr />
            
            <h2 class="dark-blue">Historical events on ${dateHeading}</h2>
            <div id="otd-history-list">Loading history...</div>
            
            <hr />
            
            <h2 class="dark-blue">Awareness days on ${dateHeading}</h2>
            <div id="otd-marquee-list">Loading marquee...</div>

            <hr />
            <div class="otd-nav" style="text-align: center;">
                <button id="otd-prev-bottom">&lt;&lt;</button>
                <button id="otd-today-bottom">Today</button>
                <button id="otd-next-bottom">&gt;&gt;</button>
            </div>
        </div>
    `;

    // Bind Navigation Buttons
    const bindNav = (suffix = '') => {
        document.getElementById(`otd-prev${suffix}`).onclick = () => {
            navigateDays(-1);
            scrollToTop();
        };
        document.getElementById(`otd-next${suffix}`).onclick = () => {
            navigateDays(1);
            scrollToTop();
        };
        document.getElementById(`otd-today${suffix}`).onclick = () => {
            viewDate = new Date();
            updateDisplay(viewDate);
            scrollToTop();
        };
    };

    bindNav();
    bindNav('-bottom');

    // Bind the "Go" button logic
    document.getElementById('otd-go').onclick = () => {
        const input = document.getElementById('otd-date-input');
        if (input.value) {
            // The date input returns "YYYY-MM-DD", which the Date constructor 
            // parses correctly while respecting leap years.
            viewDate = new Date(input.value);
            updateDisplay(viewDate);
            scrollToTop();
        }
    };
}

async function fetchAndRenderData(url, elementId, lookupKey, itemTemplateFn) {
    const listContainer = document.getElementById(elementId);
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Fetch failed: ${response.status}`);
        
        const monthData = await response.json();
        const dayEntry = monthData.find(entry => entry.date.trim() === lookupKey);

        if (dayEntry && dayEntry.events && dayEntry.events.length > 0) {
            // Sort events by the 'date' property in ascending order
            const sortedEvents = dayEntry.events.sort((a, b) => {
                if (a.date < b.date) return -1;
                if (a.date > b.date) return 1;
                return 0;
            });

            listContainer.innerHTML = sortedEvents.map(itemTemplateFn).join('');
        } else {
            listContainer.innerHTML = '<p>No data found for this date.</p>';
        }
    } catch (error) {
        console.error(`Error loading ${elementId}:`, error);
        listContainer.innerHTML = '<p>Error loading information.</p>';
    }
}

// Template for History items
function renderHistoryItem(ev) {
    // 1. Extract the year from the string "YYYY-MM-DD"
    const eventYear = ev.date.split('-')[0];

    // 2. Create a temporary date object using the year from the event 
    // but the day/month from our current viewDate.
    // Note: getMonth() is 0-indexed, so we don't need to add 1 here.
    const displayDate = new Date(eventYear, viewDate.getMonth(), viewDate.getDate());

    // 3. Format to "7 April 1876"
    const fullDateStr = displayDate.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });

    const themeImg = `${rootPath}themes/otd-theme-${ev.theme.toLowerCase()}.webp`;
    
    return `
        <div class="otd-event-row" style="display: flex; align-items: flex-start; margin-bottom: 20px;">
            <img src="${themeImg}" style="width: 65px; margin-right: 15px;" />
            <div>
                <p style="font-weight: bold; margin: 0;">${fullDateStr}</p>
                <p style="margin: 2px 0 0 0;">${ev.event}</p>
            </div>
        </div>
    `;
}

// Template for Marquee items
function renderMarqueeItem(ev) {
    const urlHtml = ev.url 
                ? `<p class="cal-url"><a href="${ev.url}" target="_blank" rel="noopener">Read more about ${ev.title}</a></p>` 
                : '';

    return `
        <div class="otd-event-row" style="margin-bottom: 20px;">
            <div>
                <p style="font-weight: bold; margin: 0;">${ev.title}</p>
                <p style="margin: 2px 0 0 0;">${ev.summary}</p>
                ${urlHtml}
            </div>
        </div>
    `;
}

function navigateDays(offset) {
    viewDate.setDate(viewDate.getDate() + offset);
    updateDisplay(viewDate);
}

document.addEventListener('DOMContentLoaded', () => updateDisplay(viewDate));
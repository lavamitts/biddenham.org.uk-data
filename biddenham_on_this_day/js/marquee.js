
async function displayTodayCalendarEvent() {
    // 1. Work out today's date
    const now = new Date();
    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const year = now.getFullYear();
    const todayKey = `${day}-${month}`;

    // 2. Define the path 
    const fileName = `${month}.json`;
    const rootPath = 'https://raw.githubusercontent.com/lavamitts/on-this-day/refs/heads/main/';
    const baseUrl = rootPath + 'data/marquee/';
    const filePath = `${baseUrl}${fileName}`;

    try {
        const response = await fetch(filePath);
        
        if (!response.ok) {
            throw new Error(`Could not fetch ${fileName} (Status: ${response.status})`);
        }

        const monthData = await response.json();

        // 3. Find today's entry in the file
        const todayData = monthData.find(entry => entry.date === todayKey);

        if (todayData && todayData.events && todayData.events.length > 0) {
            // 4. Random selection
            const randomIndex = Math.floor(Math.random() * todayData.events.length);
            const selected = todayData.events[randomIndex];
            
            // 5. Format the date for display (e.g., 7 April 2026)
            const formattedDisplayDate = now.toLocaleDateString('en-GB', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            });

            // 6. Prepare the URL link if it exists
            const urlHtml = selected.url 
                ? `<p class="cal-url"><a href="${selected.url}" target="_blank" rel="noopener">Read more about this event</a></p>` 
                : '';

            // 7. Inject into the WordPress container
            const container = document.getElementsByClassName('cal-container')[0];
            
            if (container) {
                container.innerHTML = `
                    <div class="cal-card">
                        <h2>Today's awareness day</h2>
                        <div class="cal-card-content">
                            <div class="cal-event-details">
                                <!--<p class="cal-date">${formattedDisplayDate}</p>//-->
                                <h3 class="cal-title">${selected.title}</h3>
                                <p class="cal-summary">${selected.summary}</p>
                                ${urlHtml}
                            </div>
                        </div>
                    </div>
                `;
            }
        } else {
            console.warn(`No calendar events found for ${todayKey}`);
        }
    } catch (error) {
        console.error("Calendar Error:", error);
    }
}

// Initialise the function
displayTodayCalendarEvent();

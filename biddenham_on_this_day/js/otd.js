async function displayTodayEvent() {
    // 1. Work out today's date for the filename and the lookup key
    const now = new Date();
    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const todayKey = `${day}-${month}`;

    // 2. Define the path (This is where the 'undefined' error usually happens)
    const fileName = `${month}.json`;
    const rootPath = 'https://raw.githubusercontent.com/lavamitts/on-this-day/refs/heads/main/';
    const baseUrl = rootPath + 'data/history/';
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
            const selectedEvent = todayData.events[randomIndex];
            const theme = selectedEvent.theme;
            const otdThemeImage = rootPath + 'themes/otd-theme-' + theme.toLowerCase() + ".webp";

            // 5. Format the date string to "7 April 1945"
            // We split the "1945-04-07" string to avoid timezone shifts
            const [y, m, d] = selectedEvent.date.split('-');
            const eventDateObj = new Date(y, m - 1, d);
            
            const formattedDate = eventDateObj.toLocaleDateString('en-GB', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            });

            // 6. Inject into the WordPress container
            // const container = document.getElementById('otd-container');
            const container = document.getElementsByClassName('otd-container')[0];
            
            if (container) {
                container.innerHTML = `
                    <div class="otd-card">
                        <h2>On this day in history...</h2>
                        <div class="otd-card-content">
                            <img src="${otdThemeImage}" />
                            <div class="otd-event-and-date">
                                <p class="otd-date">${formattedDate}</p>
                                <p class="otd-event">${selectedEvent.event}</p>
                            </div>
                        </div>
                    </div>
                `;
            }
        } else {
            console.warn(`No events found for ${todayKey}`);
        }
    } catch (error) {
        // This will now report the specific error if something else fails
        console.error("OTD Error:", error);
    }
}

// Initialise the function
displayTodayEvent();
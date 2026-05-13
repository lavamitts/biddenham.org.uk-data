// 1. Signal JS is active immediately to avoid flicker
document.documentElement.classList.add('has-js');

document.addEventListener('DOMContentLoaded', () => {
    /**
     * @param {string} filterType - 'future' to hide past, 'past' to hide future.
     */
    function filterAllFilmContainers(filterType) {
        const filmRows = document.querySelectorAll('.picture-house-columns');
        if (filmRows.length === 0) return;

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const parentContainers = new Set();
        filmRows.forEach(row => parentContainers.add(row.parentNode));

        filmRows.forEach(row => {
            const dateElement = row.querySelector('div:first-child') || row;
            if (!dateElement) return;

            let dateText = dateElement.textContent.includes(',') 
                ? dateElement.textContent.split(',')[1] 
                : dateElement.textContent;

            dateText = dateText.replace(/(\d+)(st|nd|rd|th)/i, '$1').trim();
            const rowDate = new Date(dateText);

            if (!isNaN(rowDate.getTime())) {
                let shouldHide = false;

                if (filterType === 'future') {
                    if (rowDate < today) shouldHide = true;
                } else if (filterType === 'past') {
                    if (rowDate > today) shouldHide = true;
                }

                if (shouldHide) {
                    row.style.display = 'none';
                } else {
                    row.style.visibility = 'visible';
                }
            }
        });

        // Handle the "No movies" message placement
        parentContainers.forEach(container => {
            const allRowsInThisContainer = container.querySelectorAll('.picture-house-columns');
            const visibleRows = Array.from(allRowsInThisContainer)
                                     .filter(row => row.style.display !== 'none');

            if (visibleRows.length === 0 && allRowsInThisContainer.length > 0) {
                const message = document.createElement('p');
                message.textContent = 'Upcoming movies to be announced.';
                
                // Identify the first hidden row to use as a placeholder for the position
                const referenceNode = allRowsInThisContainer[0];
                
                // Insert the message directly before the first hidden row
                container.insertBefore(message, referenceNode);
            }
        });
    }

    // Call the function
    filterAllFilmContainers('past'); 
});
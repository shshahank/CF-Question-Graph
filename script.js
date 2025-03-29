document.getElementById('fetchForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value.trim();

    console.log('Fetching data for:', username);
    
    fetch('/fetch_data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username })
    })
    .then(response => response.json())
    .then(data => {
        console.log('API Response:', data);
        if (data.error) {
            alert(data.error);
            return;
        }
        
        const ratings = Object.keys(data.ratings).map(Number).sort((a, b) => a - b);
        const counts = ratings.map(rating => data.ratings[rating] || 0);
        
        console.log('Processed Ratings:', ratings);
        console.log('Processed Counts:', counts);
        
        const ctx = document.getElementById('ratingChart').getContext('2d');
        if (window.ratingChart instanceof Chart) {
            window.ratingChart.destroy();
        }
        
        window.ratingChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ratings,
                datasets: [{
                    label: 'Problems Solved',
                    data: counts,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                onClick: (evt, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const rating = ratings[index];
                        window.open(`/result?rating=${rating}&username=${username}`, '_blank');
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        alert('Failed to fetch data. Check console for details.');
    });
});

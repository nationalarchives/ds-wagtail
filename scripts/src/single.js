
      const queryString = window.location.search;
      const urlParams = new URLSearchParams(queryString);
      //const startDate = urlParams.get('startDate');
      const startDateString = urlParams.get("startDate");

      // Convert startDateString to a number
      const startDateNumber = Number(startDateString); // Using Number() function

      const endDate = startDateNumber + 9;

      console.log(startDateNumber); // Output: 2000
      console.log(endDate); // Output: 2010
    

    

    
      // To write to the screen (assuming you have elements with id="output" and "outputEnd")
      document.getElementById("output").textContent = startDateNumber;
      document.getElementById("outputEnd").textContent = endDate;



// Fetch the JSON data from a URL
fetch("data/data.json")
  .then((response) => response.json())
  .then((data) => {
    // Assign the data to a variable
    const jsonData = data;

    // Initialize a dictionary to store year counts
    const yearCounts = {};
    for (let year = startDateNumber; year <= endDate; year++) {
      yearCounts[year] = 0;
    }

    for (const item of data.data) {
      if (item["@template"].details && item["@template"].details.creationDateFrom) {
        const creationDate = parseInt(item["@template"].details.creationDateFrom, 10);
        if (!isNaN(creationDate) && startDateNumber <= creationDate && creationDate <= endDate) {
          yearCounts[creationDate] += 1;
        }
      }
    }

    const ctx = document.getElementById("decade-counts-chart").getContext("2d");

    const chartData = {
      labels: Object.keys(yearCounts), // Use years as labels
      datasets: [
        {
          label: "Record Counts",
          data: Object.values(yearCounts), // Use counts as data
          backgroundColor: "rgba(219, 98, 91, 1)",
          borderColor: "rgba(255, 99, 132, 1)",
          borderWidth: 1,
        },
      ],
    };

    const chart = new Chart(ctx, {
      type: "bar",
      data: chartData,
      options: {
      // Adjust chart options as needed (e.g., scales, title)
      scales: {
        y:{ grid: {
            drawOnChartArea: false,
            color: "rgba(217 217, 214, 1)"
        },
        ticks: {
          display:false
        }
      },
      x: {
          position: 'top',
          grid: {
          drawBorder: false
       }
        },
    },
      plugins: {
      legend: {
        display: false,  // This line hides the legend
        }
      }
    },
    });

    // Print results
    console.log("Number of records per year (1990-2000):");
    for (const year in yearCounts) {
      console.log(`${year}: ${yearCounts[year]}`);
    }
  });


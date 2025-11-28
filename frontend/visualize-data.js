<!DOCTYPE
html>
<html>
<head>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  :root {
    --primary-color: steelblue;
  }
  .chart {
    width: 600px;
    height: 300px;
  }
</style>
</head>
<body>
<form id="visualizeForm">
  <label for="visualize_user_id">User ID:</label>
  <input type="text" id="visualize_user_id" name="visualize_user_id">
  <button type="submit">Visualize</button>
</form>
<svg class="chart"></svg>

<script>
document.getElementById("visualizeForm").addEventListener("submit", function(event) {
    event.preventDefault();
    let userId = document.getElementById("visualize_user_id").value;
    fetchTransactions(userId);
});

function fetchTransactions(user_id) {
    // Dummy data visualization (Replace with API call if necessary)
    let data = [
        { amount: 50 }, { amount: 100 }, { amount: 200 }
    ];

    let svg = d3.select(".chart");
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 20, bottom: 30, left: 40 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const x = d3.scaleBand()
        .range([0, width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .range([height, 0]);

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    x.domain(data.map((d, i) => i));
    y.domain([0, d3.max(data, d => d.amount)]);

    g.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x));

    g.append("g")
        .call(d3.axisLeft(y));

    g.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", (d, i) => x(i))
        .attr("y", d => y(d.amount))
        .attr("width", x.bandwidth())
        .attr("height", d => height - y(d.amount))
        .attr("fill", "var(--primary-color)");
}
</script>

</body>
</html>


document.getElementById("upload-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData();
    const files = document.getElementById("images").files;

    if (files.length === 0) {
        alert("Izaberi bar jednu sliku!");
        return;
    }

    for (let i = 0; i < files.length; i++) {
        formData.append("images", files[i]);
    }

    const resultDiv = document.getElementById("result");
    resultDiv.textContent = "Obrada u toku...";

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then((res) => res.json())
    .then((data) => {
        const ctx = document.getElementById("chart").getContext("2d");
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: ["Serijsko", "Paralelno"],
                datasets: [{
                    label: "Vreme (s)",
                    data: [data.serial_time, data.parallel_time],
                    backgroundColor: ["#f77f00", "#219ebc"]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: "Poređenje vremena izvršavanja" }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        resultDiv.innerHTML = `
            <p><strong>Serijsko vreme:</strong> ${data.serial_time.toFixed(4)} sekundi</p>
            <p><strong>Paralelno vreme:</strong> ${data.parallel_time.toFixed(4)} sekundi</p>
            <p><strong>Ubrzanje:</strong> ${(data.serial_time / data.parallel_time).toFixed(2)}x</p>
        `;
    });
});
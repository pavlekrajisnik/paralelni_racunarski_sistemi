// Dodavanje event listener-a na formu za slanje podataka
document.getElementById("upload-form").addEventListener("submit", function (e) {
    e.preventDefault(); // Spriječava podrazumijevano ponašanje forme (reload stranice)

    const formData = new FormData(); // Kreira novi FormData objekat za slanje fajlova
    const files = document.getElementById("images").files; // Dohvata fajlove iz inputa

    // Ako nijedna slika nije izabrana, prikazuje se upozorenje
    if (files.length === 0) {
        alert("Izaberi bar jednu sliku!");
        return; // Prekida dalje izvršavanje ako nema fajlova
    }

    // Dodaje sve izabrane slike u formData pod ključem "images"
    for (let i = 0; i < files.length; i++) {
        formData.append("images", files[i]);
    }

    // Prikazuje poruku dok traje obrada
    const resultDiv = document.getElementById("result");
    resultDiv.textContent = "Obrada u toku...";

    // Slanje POST zahtjeva ka backendu (Flask /upload ruta)
    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then((res) => res.json()) // Parsira JSON odgovor sa servera
    .then((data) => {
        // Priprema chart.js kontekst za crtanje grafikona
        const ctx = document.getElementById("chart").getContext("2d");

        // Kreira novi bar grafikon koji prikazuje serijsko vs paralelno vrijeme
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: ["Serijsko", "Paralelno"],
                datasets: [{
                    label: "Vreme (s)",
                    data: [data.serial_time, data.parallel_time],
                    backgroundColor: ["#f77f00", "#219ebc"] // Boje stubića
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: "Poređenje vremena izvršavanja" }
                },
                scales: {
                    y: { beginAtZero: true } // Y osa počinje od 0
                }
            }
        });

        // Prikazuje konkretne rezultate ispod grafikona
        resultDiv.innerHTML = `
            <p><strong>Serijsko vreme:</strong> ${data.serial_time.toFixed(4)} sekundi</p>
            <p><strong>Paralelno vreme:</strong> ${data.parallel_time.toFixed(4)} sekundi</p>
            <p><strong>Ubrzanje:</strong> ${(data.serial_time / data.parallel_time).toFixed(2)}x</p>
        `;
    });
});

async function transcode() {
    const form = document.getElementById("transcodeForm");
    const resultSection = document.getElementById("resultSection");
    const resultElement = document.getElementById("result");

    try {
        const formData = new FormData(form);
        const response = await fetch("/transcode", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const result = await response.text();
            resultSection.style.display = "block";
            resultElement.textContent = result;
        } else {
            const errorText = await response.text();
            alert(`Error: ${errorText}`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
}

document.addEventListener("DOMContentLoaded", function () {
  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("fileInput");
  const resultArea = document.getElementById("resultArea");
  const resultImage = document.getElementById("resultImage");
  const downloadBtn = document.getElementById("downloadBtn");
  const proOptions = document.getElementById("proOptions");
  const modeRadios = document.querySelectorAll('input[name="mode"]');
  const colorOptions = document.querySelectorAll(".color-option");
  const bgColorInput = document.getElementById("bgColor");
  const shadowIntensity = document.getElementById("shadowIntensity");
  const shadowValue = document.getElementById("shadowValue");

  // Mode selection handler
  modeRadios.forEach((radio) => {
    radio.addEventListener("change", function () {
      proOptions.style.display = this.value === "pro_mode" ? "block" : "none";
    });
  });

  // Color selection handler
  colorOptions.forEach((option) => {
    option.addEventListener("click", function () {
      // Remove active class from all options
      colorOptions.forEach((opt) => opt.classList.remove("active"));

      // Add active class to selected option
      this.classList.add("active");

      // Update hidden input value
      bgColorInput.value = this.dataset.color;
    });
  });

  // Set first color as active by default
  if (colorOptions.length > 0) {
    colorOptions[0].classList.add("active");
  }

  // Drag and drop handlers
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, unhighlight, false);
  });

  function highlight() {
    dropArea.classList.add("highlight");
  }

  function unhighlight() {
    dropArea.classList.remove("highlight");
  }

  // Handle dropped files
  dropArea.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
  }

  // Handle click to select files
  dropArea.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", function () {
    handleFiles(this.files);
  });

  function handleFiles(files) {
    if (files.length > 0) {
      const file = files[0];
      if (file.type.match("image.*")) {
        processImage(file);
      } else {
        alert("Please select an image file.");
      }
    }
  }

  function processImage(file) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append(
      "mode",
      document.querySelector('input[name="mode"]:checked').value
    );
    formData.append("bg_color", bgColorInput.value);
    formData.append("shadow_intensity", shadowIntensity.value);

    dropArea.classList.add("uploading");
    dropArea.querySelector(".upload-text").textContent = "Processing...";

    fetch("/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          resultImage.src = data.image;
          resultArea.style.display = "block";
          downloadBtn.href = data.image;
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while processing the image.");
      })
      .finally(() => {
        dropArea.classList.remove("uploading");
        dropArea.querySelector(".upload-text").textContent =
          "Drag & Drop your image here or click to browse";
      });
  }
});

shadowIntensity.addEventListener("input", function () {
  const value = this.value;
  shadowValue.textContent = `${value}%`;

  // Update the preview image shadow
  if (resultImage.src) {
    const intensity = value / 100;
    resultImage.style.filter = `
            drop-shadow(0 0 ${10 * intensity}px rgba(255,255,255,0.9))
            drop-shadow(0 0 ${15 * intensity}px rgba(255,255,255,0.7))
            drop-shadow(0 0 ${20 * intensity}px rgba(255,255,255,0.5))
        `;
  }
});

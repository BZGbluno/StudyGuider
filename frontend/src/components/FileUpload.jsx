import React, { useState } from 'react';

const FileUpload = () => {
  // State for each file type
  const [csvFile, setCsvFile] = useState(null);
  const [imageFile, setImageFile] = useState(null);

  // Event handler for CSV file selection
  const handleCsvChange = (event) => {
    const file = event.target.files[0];
    setCsvFile(file);
    console.log('Selected CSV file:', file);
  };

  // Event handler for image file selection
  const handleImageChange = (event) => {
    const file = event.target.files[0];
    setImageFile(file);
    console.log('Selected image file:', file);
  };

  // Form submission handler
  const handleSubmit = (event) => {
    event.preventDefault();

    // Basic validation: ensuring that both files are selected
    if (!csvFile || !imageFile) {
      console.log('Please select both a CSV file and an image file.');
      return;
    }

    console.log('Uploading files:', csvFile, imageFile);

    // Create a FormData object to hold the files
    const formData = new FormData();
    formData.append('csv', csvFile);
    formData.append('image', imageFile);

    // Example: Using fetch to upload files to a server endpoint
    // Replace 'your-upload-url' with your actual API endpoint.
    fetch('your-upload-url', {
      method: 'POST',
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Upload failed!');
        }
        return response.json();
      })
      .then((data) => {
        console.log('Upload successful:', data);
      })
      .catch((error) => {
        console.error('Error during file upload:', error);
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="csvInput">Upload CSV File:</label>
        <input
          id="csvInput"
          type="file"
          accept=".csv"
          onChange={handleCsvChange}
        />
      </div>
      <div>
        <label htmlFor="imageInput">Upload Image File:</label>
        <input
          id="imageInput"
          type="file"
          accept="image/*"
          onChange={handleImageChange}
        />
      </div>
      <button type="submit">Upload Files</button>
    </form>
  );
};

export default FileUpload;

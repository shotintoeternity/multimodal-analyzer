/**
 * Multimodal Technical Analysis System
 * Main JavaScript for frontend functionality
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize the application
  initApp();
});

/**
 * Initialize the application
 */
function initApp() {
  // Set up file upload handlers
  setupFileUploads();
  
  // Set up tab navigation
  setupTabs();
  
  // Set up form submission
  setupFormSubmission();
}

/**
 * Set up file upload functionality
 */
function setupFileUploads() {
  // Get all upload areas
  const uploadAreas = document.querySelectorAll('.upload-area');
  
  uploadAreas.forEach(area => {
    const input = area.querySelector('input[type="file"]');
    const preview = area.querySelector('.file-preview');
    
    // Handle drag and drop events
    area.addEventListener('dragover', (e) => {
      e.preventDefault();
      area.classList.add('active');
    });
    
    area.addEventListener('dragleave', () => {
      area.classList.remove('active');
    });
    
    area.addEventListener('drop', (e) => {
      e.preventDefault();
      area.classList.remove('active');
      
      if (e.dataTransfer.files.length) {
        handleFiles(e.dataTransfer.files, input, preview, area);
      }
    });
    
    // Handle click to upload
    area.addEventListener('click', () => {
      input.click();
    });
    
    // Handle file selection
    input.addEventListener('change', () => {
      if (input.files.length) {
        handleFiles(input.files, input, preview, area);
      }
    });
  });
}

/**
 * Handle uploaded files
 * @param {FileList} files - The uploaded files
 * @param {HTMLElement} input - The file input element
 * @param {HTMLElement} preview - The preview element
 * @param {HTMLElement} area - The upload area element
 */
function handleFiles(files, input, preview, area) {
  const file = files[0];
  
  // Update the input files
  if (input) {
    // Create a DataTransfer object and add the file
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    input.files = dataTransfer.files;
  }
  
  // Show preview based on file type
  if (preview) {
    preview.innerHTML = '';
    
    if (file.type.startsWith('image/')) {
      // Image preview
      const img = document.createElement('img');
      img.classList.add('image-preview');
      img.file = file;
      preview.appendChild(img);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);
      
      // Add file info
      const fileInfo = document.createElement('div');
      fileInfo.classList.add('file-info');
      fileInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;
      preview.appendChild(fileInfo);
    } else {
      // Text/code preview
      const fileInfo = document.createElement('div');
      fileInfo.classList.add('file-info');
      fileInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;
      preview.appendChild(fileInfo);
      
      // If it's likely a text file, show content preview
      if (isTextFile(file)) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target.result;
          const codePreview = document.createElement('div');
          codePreview.classList.add('code-preview');
          
          // Limit preview to first few lines
          const lines = content.split('\n').slice(0, 5);
          const previewText = lines.join('\n') + (lines.length < content.split('\n').length ? '\n...' : '');
          
          codePreview.textContent = previewText;
          preview.appendChild(codePreview);
        };
        reader.readAsText(file);
      }
    }
    
    // Show the preview section
    preview.style.display = 'block';
    
    // Update upload area to show "Change file" instead
    const uploadText = area.querySelector('.upload-text');
    if (uploadText) {
      uploadText.textContent = 'Click to change file';
    }
  }
}

/**
 * Check if a file is likely a text file
 * @param {File} file - The file to check
 * @returns {boolean} - Whether the file is likely a text file
 */
function isTextFile(file) {
  const textTypes = [
    'text/plain', 'text/html', 'text/css', 'text/javascript',
    'application/json', 'application/xml', 'application/javascript',
    'application/typescript'
  ];
  
  // Check MIME type
  if (textTypes.includes(file.type)) {
    return true;
  }
  
  // Check file extension
  const textExtensions = [
    '.txt', '.js', '.py', '.html', '.css', '.json', '.xml',
    '.md', '.csv', '.ts', '.jsx', '.tsx', '.java', '.c',
    '.cpp', '.h', '.cs', '.php', '.rb', '.go', '.rs',
    '.swift', '.kt', '.sh', '.bat', '.ps1', '.yml', '.yaml'
  ];
  
  return textExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
}

/**
 * Format file size in human-readable format
 * @param {number} bytes - The file size in bytes
 * @returns {string} - Formatted file size
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Set up tab navigation
 */
function setupTabs() {
  const tabs = document.querySelectorAll('.tab');
  const tabContents = document.querySelectorAll('.tab-content');
  
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active class from all tabs
      tabs.forEach(t => t.classList.remove('active'));
      
      // Add active class to clicked tab
      tab.classList.add('active');
      
      // Hide all tab contents
      tabContents.forEach(content => {
        content.style.display = 'none';
      });
      
      // Show the selected tab content
      const target = tab.getAttribute('data-target');
      const targetContent = document.getElementById(target);
      if (targetContent) {
        targetContent.style.display = 'block';
      }
    });
  });
  
  // Activate the first tab by default
  if (tabs.length > 0) {
    tabs[0].click();
  }
}

/**
 * Set up form submission
 */
function setupFormSubmission() {
  const forms = document.querySelectorAll('form[data-api]');
  
  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      // Get the API endpoint from the form
      const apiEndpoint = form.getAttribute('data-api');
      
      // Show loading state
      const submitButton = form.querySelector('button[type="submit"]');
      const originalButtonText = submitButton.textContent;
      submitButton.disabled = true;
      submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
      
      // Get the result container
      const resultContainer = document.querySelector(form.getAttribute('data-result-container'));
      if (resultContainer) {
        resultContainer.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
      }
      
      try {
        // Create form data
        const formData = new FormData(form);
        
        // Send the request
        const response = await fetch(apiEndpoint, {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        // Parse the response
        const result = await response.json();
        
        // Display the results
        displayResults(result, resultContainer);
        
        // Scroll to results
        resultContainer.scrollIntoView({ behavior: 'smooth' });
      } catch (error) {
        console.error('Error submitting form:', error);
        
        if (resultContainer) {
          resultContainer.innerHTML = `
            <div class="card">
              <div class="card-body">
                <h5 class="card-title text-danger">Error</h5>
                <p>An error occurred while analyzing: ${error.message}</p>
              </div>
            </div>
          `;
        }
      } finally {
        // Restore button state
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
      }
    });
  });
}

/**
 * Display analysis results
 * @param {Object} result - The analysis result
 * @param {HTMLElement} container - The container to display results in
 */
function displayResults(result, container) {
  if (!container) return;
  
  // Clear the container
  container.innerHTML = '';
  
  // Create the results UI
  const resultCard = document.createElement('div');
  resultCard.classList.add('card');
  
  // Add header
  const cardHeader = document.createElement('div');
  cardHeader.classList.add('card-header');
  cardHeader.innerHTML = `
    <h5 class="card-title">Analysis Results</h5>
    <span class="text-muted">ID: ${result.analysis_id}</span>
  `;
  resultCard.appendChild(cardHeader);
  
  // Add body
  const cardBody = document.createElement('div');
  cardBody.classList.add('card-body');
  
  // Add result sections based on what's available in the result
  if (result.result) {
    // Image analysis results
    if (result.result.description) {
      cardBody.appendChild(createSection('Description', result.result.description));
    }
    
    // Code analysis results
    if (result.result.language) {
      cardBody.appendChild(createSection('Code Analysis', `
        <p><strong>Language:</strong> ${result.result.language}</p>
        ${result.result.summary ? `<p>${result.result.summary}</p>` : ''}
      `));
    }
    
    // Issues section
    if (result.result.issues || result.result.potential_issues) {
      const issues = result.result.issues || result.result.potential_issues || [];
      const issuesSection = document.createElement('div');
      issuesSection.classList.add('result-section');
      issuesSection.innerHTML = `<h6 class="result-title">Issues Detected</h6>`;
      
      const issuesList = document.createElement('div');
      
      if (Array.isArray(issues)) {
        issues.forEach(issue => {
          const issueItem = document.createElement('div');
          issueItem.classList.add('result-item');
          
          if (typeof issue === 'object') {
            issueItem.innerHTML = `
              <div class="result-item-header">
                <span class="result-item-title">${issue.description || issue.type || 'Issue'}</span>
                ${issue.line ? `<span class="result-item-badge badge-error">Line ${issue.line}</span>` : ''}
              </div>
              ${issue.details ? `<p>${issue.details}</p>` : ''}
            `;
          } else {
            issueItem.innerHTML = `<p>${issue}</p>`;
          }
          
          issuesList.appendChild(issueItem);
        });
      }
      
      issuesSection.appendChild(issuesList);
      cardBody.appendChild(issuesSection);
    }
    
    // Combined analysis
    if (result.result.combined_analysis) {
      cardBody.appendChild(createSection('Combined Analysis', result.result.combined_analysis));
      
      // Correlations
      if (result.result.correlations && result.result.correlations.length) {
        const correlationsSection = document.createElement('div');
        correlationsSection.classList.add('result-section');
        correlationsSection.innerHTML = `<h6 class="result-title">Correlations</h6>`;
        
        const correlationsList = document.createElement('ul');
        result.result.correlations.forEach(correlation => {
          const item = document.createElement('li');
          item.textContent = correlation;
          correlationsList.appendChild(item);
        });
        
        correlationsSection.appendChild(correlationsList);
        cardBody.appendChild(correlationsSection);
      }
    }
  }
  
  // Recommendations section
  if (result.recommendations && result.recommendations.length) {
    const recommendationsSection = document.createElement('div');
    recommendationsSection.classList.add('recommendations');
    recommendationsSection.innerHTML = `<h6 class="result-title">Recommendations</h6>`;
    
    const recommendationsList = document.createElement('div');
    result.recommendations.forEach(recommendation => {
      const recommendationItem = document.createElement('div');
      recommendationItem.classList.add('recommendation-item');
      recommendationItem.innerHTML = `
        <div class="recommendation-icon">✓</div>
        <div class="recommendation-text">${recommendation}</div>
      `;
      recommendationsList.appendChild(recommendationItem);
    });
    
    recommendationsSection.appendChild(recommendationsList);
    cardBody.appendChild(recommendationsSection);
  }
  
  resultCard.appendChild(cardBody);
  container.appendChild(resultCard);
}

/**
 * Create a section for the results
 * @param {string} title - The section title
 * @param {string} content - The section content (can be HTML)
 * @returns {HTMLElement} - The section element
 */
function createSection(title, content) {
  const section = document.createElement('div');
  section.classList.add('result-section');
  
  const titleElement = document.createElement('h6');
  titleElement.classList.add('result-title');
  titleElement.textContent = title;
  
  const contentElement = document.createElement('div');
  contentElement.innerHTML = content;
  
  section.appendChild(titleElement);
  section.appendChild(contentElement);
  
  return section;
}

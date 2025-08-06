import { createSection, getXsrfToken } from '../utils';
import { apiService } from '../services/api';

// Use a relative path to ensure it's created in the current workspace
const AWS_ENV_FILE = 'reprolab_data/aws_env.json';

export class ArchiveSection {
  private accessKey: string = '';
  private secretKey: string = '';
  private bucketName: string = '';
  private initialized: boolean = false;

  constructor() {
    this.initialize();
  }

  private async initialize() {
    console.log('[ReproLab Archive] Initializing...');
    await this.loadAWSEnv();
    this.initialized = true;
    console.log('[ReproLab Archive] Initialized with values:', {
      accessKey: this.accessKey ? '***' : '',
      secretKey: this.secretKey ? '***' : '',
      bucketName: this.bucketName
    });
  }

  render(): string {
    if (!this.initialized) {
      console.log('[ReproLab Archive] Not yet initialized, rendering with empty values');
    }
    
    const archiveContent = `
      <p>Configure AWS S3 credentials for data archiving</p>
      <div class="reprolab-archive-inputs">
        <input id="reprolab-archive-input1" type="password" class="reprolab-input" placeholder="Access Key" value="${this.accessKey}">
        <input id="reprolab-archive-input2" type="password" class="reprolab-input" placeholder="Secret Key" value="${this.secretKey}">
        <input id="reprolab-archive-input3" type="text" class="reprolab-input" placeholder="Bucket Name" value="${this.bucketName}">
        <button id="reprolab-archive-save" class="reprolab-button">Save</button>
      </div>
    `;
    
    const section = createSection('AWS S3 Configuration', archiveContent);
    return section.outerHTML;
  }

  async handleSaveButton(node: HTMLElement) {
    const accessKey = (node.querySelector('#reprolab-archive-input1') as HTMLInputElement)?.value || '';
    const secretKey = (node.querySelector('#reprolab-archive-input2') as HTMLInputElement)?.value || '';
    const bucketName = (node.querySelector('#reprolab-archive-input3') as HTMLInputElement)?.value || '';
    
    this.accessKey = accessKey;
    this.secretKey = secretKey;
    this.bucketName = bucketName;

    await this.saveAWSEnv();
    console.log('[ReproLab Archive Save]', { 
      accessKey: accessKey ? '***' : '', 
      secretKey: secretKey ? '***' : '', 
      bucketName 
    });

    // Create archive via API
    try {
      const response = await apiService.createArchive({
        name: `archive_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}`,
        include_data: true,
        include_notebooks: true
      });

      if (response.status === 'success') {
        console.log('[ReproLab] Archive created successfully:', response.message);
      } else {
        console.error('[ReproLab] Failed to create archive:', response.message);
      }
    } catch (error) {
      console.error('[ReproLab] Error creating archive:', error);
    }
  }

  private async loadAWSEnv() {
    console.log('[ReproLab Archive] Loading AWS environment...');
    try {
      const response = await fetch(`/api/contents/${AWS_ENV_FILE}`);
      console.log('[ReproLab Archive] Fetch response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('[ReproLab Archive] Received data:', data ? 'success' : 'empty');
        
        if (data && data.content) {
          const parsed = JSON.parse(data.content);
          console.log('[ReproLab Archive] Parsed content:', parsed ? 'success' : 'failed');
          
          if (typeof parsed === 'object' && parsed !== null) {
            this.accessKey = parsed.AWS_ACCESS_KEY_ID || '';
            this.secretKey = parsed.AWS_SECRET_ACCESS_KEY || '';
            this.bucketName = parsed.AWS_BUCKET || '';
            console.log('[ReproLab Archive] Loaded values:', {
              accessKey: this.accessKey ? '***' : '',
              secretKey: this.secretKey ? '***' : '',
              bucketName: this.bucketName
            });
          }
        }
      } else if (response.status === 404) {
        console.log('[ReproLab Archive] File not found, creating with empty values');
        // File does not exist, create it with empty values
        this.accessKey = '';
        this.secretKey = '';
        this.bucketName = '';
        await this.saveAWSEnv();
      }
    } catch (e) {
      console.error('[ReproLab Archive] Could not load AWS environment variables:', e);
      // If there's an error, initialize with empty values
      this.accessKey = '';
      this.secretKey = '';
      this.bucketName = '';
      await this.saveAWSEnv();
    }
  }

  private async saveAWSEnv() {
    console.log('[ReproLab Archive] Saving AWS environment...');
    try {
      const xsrfToken = getXsrfToken();
      const response = await fetch(`/api/contents/${AWS_ENV_FILE}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(xsrfToken ? { 'X-XSRFToken': xsrfToken } : {})
        },
        body: JSON.stringify({
          type: 'file',
          format: 'text',
          content: JSON.stringify({
            AWS_ACCESS_KEY_ID: this.accessKey,
            AWS_SECRET_ACCESS_KEY: this.secretKey,
            AWS_BUCKET: this.bucketName
          })
        })
      });
      console.log('[ReproLab Archive] Save response status:', response.status);
    } catch (e) {
      console.error('[ReproLab Archive] Could not save AWS environment variables:', e);
    }
  }
}

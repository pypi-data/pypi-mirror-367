/**
 * API Service for ReproLab
 * Handles communication with the backend server extension
 */

import { getXsrfToken } from '../utils';

export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  message: string;
  data?: T;
  path?: string;
}

export interface ExperimentData {
  name?: string;
  description?: string;
  notebook_path?: string;
  action?: 'start' | 'end';
}

export interface EnvironmentData {
  action: 'create_environment' | 'freeze_dependencies';
  venv_name?: string;
}

export interface ArchiveData {
  name?: string;
  include_data?: boolean;
  include_notebooks?: boolean;
  tag_name?: string;
}

export interface ZenodoData {
  title?: string;
  description?: string;
  authors?: string[];
  tag_name?: string;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    // Get the base URL from JupyterLab and ensure it points to the server extension
    const jupyterBaseUrl = (window as any).__jupyter_config_data?.baseUrl || '';
    console.log('[ReproLab API] Jupyter base URL:', jupyterBaseUrl);
    
    // The server extension is registered at the root level, not under lab/tree
    // We need to use the server URL directly
    const serverUrl = window.location.origin + '/';
    this.baseUrl = serverUrl;
    console.log('[ReproLab API] Server base URL:', this.baseUrl);
  }

  private async makeRequest<T>(
    endpoint: string,
    method: 'GET' | 'POST' = 'GET',
    data?: any
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}reprolab/api/${endpoint}`;
    
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    // Add XSRF token for POST requests
    if (method === 'POST') {
      const xsrfToken = getXsrfToken();
      console.log('[ReproLab API] XSRF Token:', xsrfToken);
      if (xsrfToken) {
        options.headers = {
          ...options.headers,
          'X-XSRFToken': xsrfToken,
        };
      }
    }

    if (data && method === 'POST') {
      options.body = JSON.stringify(data);
    }

    try {
      console.log('[ReproLab API] Making request to:', url);
      console.log('[ReproLab API] Headers:', options.headers);
      const response = await fetch(url, options);
      const result = await response.json();
      
      if (!response.ok) {
        console.error('[ReproLab API] Request failed:', response.status, result);
        throw new Error(result.message || `HTTP ${response.status}`);
      }
      
      return result;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Check if the server extension is running
   */
  async checkStatus(): Promise<ApiResponse> {
    return this.makeRequest('status');
  }

  /**
   * Create a new experiment
   */
  async createExperiment(data: ExperimentData): Promise<ApiResponse> {
    return this.makeRequest('experiment', 'POST', data);
  }

  /**
   * Perform environment-related actions
   */
  async performEnvironmentAction(data: EnvironmentData): Promise<ApiResponse> {
    return this.makeRequest('environment', 'POST', data);
  }

  /**
   * Create an archive package
   */
  async createArchive(data: ArchiveData): Promise<ApiResponse> {
    return this.makeRequest('archive', 'POST', data);
  }

  /**
   * Create a Zenodo-ready package
   */
  async createZenodoPackage(data: ZenodoData): Promise<ApiResponse> {
    return this.makeRequest('zenodo', 'POST', data);
  }
}

// Export a singleton instance
export const apiService = new ApiService(); 

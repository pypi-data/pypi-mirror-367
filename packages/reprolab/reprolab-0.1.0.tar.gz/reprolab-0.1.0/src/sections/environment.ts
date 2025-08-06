import { createSection } from '../utils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { apiService } from '../services/api';

// Constants
const ENVIRONMENT_OPTIONS = {
  CREATE_BUTTON_ID: 'reprolab-create-environment-btn',
  FREEZE_DEPS_BUTTON_ID: 'reprolab-freeze-deps-btn'
} as const;

export class EnvironmentSection {
  private readonly notebooks: INotebookTracker | undefined;
  private readonly app: JupyterFrontEnd;

  constructor(app: JupyterFrontEnd, notebooks?: INotebookTracker) {
    this.app = app;
    this.notebooks = notebooks;
  }

  render(): string {
    const environmentContent = `
      <p>Create a reproducible environment with pinned dependencies.</p>
      <button id="${ENVIRONMENT_OPTIONS.CREATE_BUTTON_ID}" class="reprolab-button">
        Create Environment
      </button>
      <button id="${ENVIRONMENT_OPTIONS.FREEZE_DEPS_BUTTON_ID}" class="reprolab-button">
        Freeze Dependencies
      </button>
    `;
    const section = createSection('Create reproducible environment', environmentContent);
    return section.outerHTML;
  }

  private validateNotebookContext(): boolean {
    if (!this.notebooks || !this.notebooks.currentWidget) {
      console.error('[ReproLab] No active notebook found');
      return false;
    }
    return true;
  }

  public async createEnvironment(): Promise<void> {
    if (!this.validateNotebookContext()) {
      return;
    }

    try {
      console.log('[ReproLab] Creating environment via API...');
      
      // Create environment via API
      const response = await apiService.performEnvironmentAction({
        action: 'create_environment',
        venv_name: 'my_venv'
      });

      if (response.status === 'success') {
        console.log('[ReproLab] Environment created successfully:', response.message);
        
        // Add environment cells to notebook
        await this.addEnvironmentCells();
        await this.executeEnvironment();
        
        console.log('[ReproLab] Environment setup completed successfully');
      } else {
        console.error('[ReproLab] Failed to create environment:', response.message);
      }
    } catch (error) {
      console.error('[ReproLab] Error creating environment:', error);
    }
  }

  public async addFreezeDepsCell(): Promise<void> {
    if (!this.validateNotebookContext()) {
      return;
    }

    try {
      console.log('[ReproLab] Freezing dependencies via API...');
      
      // Freeze dependencies via API
      const response = await apiService.performEnvironmentAction({
        action: 'freeze_dependencies',
        venv_name: 'my_venv'
      });

      if (response.status === 'success') {
        console.log('[ReproLab] Dependencies frozen successfully:', response.message);
        
        // Add freeze dependencies cell to notebook
        await this.addFreezeDepsCellToNotebook();
        await this.executeFreezeDeps();
        
        console.log('[ReproLab] Dependencies freeze completed successfully');
      } else {
        console.error('[ReproLab] Failed to freeze dependencies:', response.message);
      }
    } catch (error) {
      console.error('[ReproLab] Error freezing dependencies:', error);
    }
  }

  private async addEnvironmentCells(): Promise<void> {
    const notebook = this.notebooks!.currentWidget!.content;
    
    console.log('[ReproLab] Adding environment cells...');

    // Add environment setup cell at the bottom of the notebook
    const cellCount = notebook.model!.cells.length;
    notebook.activeCellIndex = cellCount;
    this.app.commands.execute('notebook:insert-cell-below');
    await this.delay(100);
    
    const envCell = notebook.model!.cells.get(cellCount);
    if (envCell) {
      envCell.sharedModel.setSource(`from reprolab.environment import create_new_venv
create_new_venv('my_venv')`);
      console.log('[ReproLab] Added environment setup cell');
    }
  }

  private async addFreezeDepsCellToNotebook(): Promise<void> {
    const notebook = this.notebooks!.currentWidget!.content;
    
    console.log('[ReproLab] Adding freeze dependencies cell...');

    // Add freeze dependencies cell at the bottom of the notebook
    const cellCount = notebook.model!.cells.length;
    notebook.activeCellIndex = cellCount;
    this.app.commands.execute('notebook:insert-cell-below');
    await this.delay(100);
    
    const freezeCell = notebook.model!.cells.get(cellCount);
    if (freezeCell) {
      freezeCell.sharedModel.setSource(`from reprolab.environment import freeze_venv_dependencies
freeze_venv_dependencies('my_venv')`);
      console.log('[ReproLab] Added freeze dependencies cell');
    }
  }

  private async executeEnvironment(): Promise<void> {
    console.log('[ReproLab] Running environment setup...');
    await this.app.commands.execute('notebook:run-all-cells');
    await this.delay(2000);
  }

  private async executeFreezeDeps(): Promise<void> {
    console.log('[ReproLab] Running freeze dependencies...');
    await this.app.commands.execute('notebook:run-all-cells');
    await this.delay(2000);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
} 


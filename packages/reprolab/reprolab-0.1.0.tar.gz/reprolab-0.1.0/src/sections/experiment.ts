import { createSection } from '../utils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { apiService } from '../services/api';

// Constants
const EXPERIMENT_OPTIONS = {
  CREATE_BUTTON_ID: 'reprolab-create-experiment-btn'
} as const;

export class ExperimentSection {
  private readonly notebooks: INotebookTracker | undefined;
  private readonly app: JupyterFrontEnd;

  constructor(app: JupyterFrontEnd, notebooks?: INotebookTracker) {
    this.app = app;
    this.notebooks = notebooks;
  }

  render(): string {
    const experimentContent = `
      <p>Create an experiment to save your current project state with a git tag.</p>
      <button id="${EXPERIMENT_OPTIONS.CREATE_BUTTON_ID}" class="reprolab-button">
        Create Experiment
      </button>
    `;
    const section = createSection('Create experiment', experimentContent);
    return section.outerHTML;
  }

  private validateNotebookContext(): boolean {
    if (!this.notebooks || !this.notebooks.currentWidget) {
      console.error('[ReproLab] No active notebook found');
      return false;
    }
    return true;
  }

  public async createExperiment(): Promise<void> {
    if (!this.validateNotebookContext()) {
      return;
    }

    try {
      console.log('[ReproLab] Creating experiment via API...');
      
      // Create experiment via API
      const response = await apiService.createExperiment({
        action: 'start'
      });

      if (response.status === 'success') {
        console.log('[ReproLab] Experiment created successfully:', response.message);
        
        // Add experiment cells to notebook
        await this.addExperimentCells();
        await this.executeExperiment();
        
        console.log('[ReproLab] Experiment completed successfully');
      } else {
        console.error('[ReproLab] Failed to create experiment:', response.message);
      }
    } catch (error) {
      console.error('[ReproLab] Error creating experiment:', error);
    }
  }

  private async addExperimentCells(): Promise<void> {
    const notebook = this.notebooks!.currentWidget!.content;
    
    console.log('[ReproLab] Adding experiment cells...');

    // Add start experiment cell at the bottom of the notebook
    const cellCount = notebook.model!.cells.length;
    notebook.activeCellIndex = cellCount;
    this.app.commands.execute('notebook:insert-cell-below');
    await this.delay(100);
    
    const startCell = notebook.model!.cells.get(cellCount);
    if (startCell) {
      startCell.sharedModel.setSource(`from reprolab.experiment import start_experiment
start_experiment()`);
      console.log('[ReproLab] Added start experiment cell');
    }

    // Add end experiment cell
    notebook.activeCellIndex = cellCount + 1;
    this.app.commands.execute('notebook:insert-cell-below');
    await this.delay(100);
    
    const endCell = notebook.model!.cells.get(cellCount + 1);
    if (endCell) {
      endCell.sharedModel.setSource(`from reprolab.experiment import end_experiment
end_experiment()`);
      console.log('[ReproLab] Added end experiment cell');
    }
  }

  private async executeExperiment(): Promise<void> {
    console.log('[ReproLab] Running experiment cells...');
    await this.app.commands.execute('notebook:run-all-cells');
    await this.delay(2000);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

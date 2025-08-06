import { createSection } from '../utils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { apiService } from '../services/api';

export class ZenodoSection {
  private readonly notebooks: INotebookTracker | undefined;
  private readonly app: JupyterFrontEnd;

  constructor(app: JupyterFrontEnd, notebooks?: INotebookTracker) {
    this.app = app;
    this.notebooks = notebooks;
  }

  render(): string {
    const zenodoContent = `
      <p>Create a Zenodo-ready reproducibility package.</p>
      <button id="reprolab-zenodo-more" class="reprolab-button">
        Create Reproducibility Package
      </button>
    `;
    const section = createSection('Publishing software and data to Zenodo', zenodoContent);
    return section.outerHTML;
  }

  private validateNotebookContext(): boolean {
    if (!this.notebooks || !this.notebooks.currentWidget) {
      console.error('[ReproLab] No active notebook found');
      return false;
    }
    return true;
  }

  async handleZenodoButton(modal: HTMLElement): Promise<void> {
    modal.style.display = 'block';
  }

  async handleTestButton(): Promise<void> {
    if (!this.validateNotebookContext()) {
      return;
    }

    try {
      console.log('[ReproLab] Creating Zenodo package via API...');
      
      // Create Zenodo package via API
      const response = await apiService.createZenodoPackage({
        title: 'Reproducible Research Package',
        description: 'Complete reproducibility package created via ReproLab',
        authors: ['Researcher']
      });

      if (response.status === 'success') {
        console.log('[ReproLab] Zenodo package created successfully:', response.message);
        
        // Add reproducability cells to notebook
        await this.addReproducabilityCells();
        await this.executeFirstCell();
        
        console.log('[ReproLab] Reproducability package cells added successfully');
      } else {
        console.error('[ReproLab] Failed to create Zenodo package:', response.message);
      }
    } catch (error) {
      console.error('[ReproLab] Error adding reproducability cells:', error);
    }
  }

  private async addReproducabilityCells(): Promise<void> {
    const notebook = this.notebooks!.currentWidget!.content;
    
    console.log('[ReproLab] Adding reproducability package cells...');

    // Add first cell at the bottom of the notebook
    const cellCount = notebook.model!.cells.length;
    notebook.activeCellIndex = cellCount;
    this.app.commands.execute('notebook:insert-cell-below');
    await this.delay(100);
    
    const listTagsCell = notebook.model!.cells.get(cellCount);
    if (listTagsCell) {
      listTagsCell.sharedModel.setSource(`from reprolab.experiment import list_and_sort_git_tags
list_and_sort_git_tags()
# Pick your git tag, to download the reproducability package`);
      console.log('[ReproLab] Added git tags listing cell');
    }

    // Add second cell
    notebook.activeCellIndex = cellCount + 1;
    this.app.commands.execute('notebook:insert-cell-below');
    await this.delay(100);
    
    const downloadCell = notebook.model!.cells.get(cellCount + 1);
    if (downloadCell) {
      downloadCell.sharedModel.setSource(`from reprolab.experiment import download_reproducability_package
download_reproducability_package('<git_tag>')`);
      console.log('[ReproLab] Added download package cell');
    }
  }

  private async executeFirstCell(): Promise<void> {
    console.log('[ReproLab] Executing git tags listing cell...');
    
    const notebook = this.notebooks!.currentWidget!.content;
    const cellCount = notebook.model!.cells.length;
    
    // Set the first new cell as active and execute it
    notebook.activeCellIndex = cellCount - 2; // First of the two new cells
    await this.app.commands.execute('notebook:run-cell');
    await this.delay(2000);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

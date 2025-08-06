import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  ICommandPalette
} from '@jupyterlab/apputils';

import {
  LabIcon
} from '@jupyterlab/ui-components';

import {
  Widget
} from '@lumino/widgets';

import { INotebookTracker } from '@jupyterlab/notebook';

// Import CSS styles
import '../style/index.js';

import { createButton } from './utils';
import { ChecklistSection } from './sections/checklist';
import { DemoSection } from './sections/demo';
import { ArchiveSection } from './sections/archive';
import { ZenodoSection } from './sections/zenodo';
import { ExperimentSection } from './sections/experiment';
import { EnvironmentSection } from './sections/environment';

// Constants
const REPROLAB_CONFIG = {
  ID: 'reprolab-sidebar',
  TITLE: 'ReproLab',
  CAPTION: 'ReproLab Panel',
  COMMAND: 'reprolab:open',
  COMMAND_LABEL: 'Open ReproLab Panel',
  COMMAND_CATEGORY: 'ReproLab'
} as const;

const BUTTON_IDS = {
  DEMO: 'reprolab-demo-btn',
  ARCHIVE_SAVE: 'reprolab-archive-save',
  ZENODO_MORE: 'reprolab-zenodo-more',
  CREATE_EXPERIMENT: 'reprolab-create-experiment-btn',
  CREATE_ENVIRONMENT: 'reprolab-create-environment-btn',
  FREEZE_DEPS: 'reprolab-freeze-deps-btn',
  MODAL_TEST: 'reprolab-modal-test'
} as const;

const CHECKBOX_SELECTOR = 'input[type="checkbox"]';

/** SVG string for the ReproLab icon */
const REPROLAB_ICON_SVG = `
<svg xmlns="http://www.w3.org/2000/svg" width="16" viewBox="0 0 24 24">
  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" fill="currentColor"/>
</svg>
`;

/** Create the ReproLab icon */
const reprolabIcon = new LabIcon({
  name: 'reprolab:icon',
  svgstr: REPROLAB_ICON_SVG
});

/** The sidebar widget for the ReproLab panel */
class ReprolabSidebarWidget extends Widget {
  private checklistSection!: ChecklistSection;
  private demoSection!: DemoSection;
  private archiveSection!: ArchiveSection;
  private zenodoSection!: ZenodoSection;
  private experimentSection!: ExperimentSection;
  private environmentSection!: EnvironmentSection;
  private readonly notebooks: INotebookTracker | undefined;
  private readonly app: JupyterFrontEnd;

  constructor(app: JupyterFrontEnd, notebooks?: INotebookTracker) {
    super();
    this.app = app;
    this.notebooks = notebooks;
    
    this.initializeWidget();
    this.initializeSections();
    this.render();
    this.loadChecklistState();
  }

  private initializeWidget(): void {
    this.id = REPROLAB_CONFIG.ID;
    this.addClass('jp-SideBar');
    this.addClass('reprolab-sidebar');
    this.title.icon = reprolabIcon;
    this.title.label = REPROLAB_CONFIG.TITLE;
    this.title.caption = REPROLAB_CONFIG.CAPTION;
  }

  private initializeSections(): void {
    this.checklistSection = new ChecklistSection();
    this.demoSection = new DemoSection(this.app, this.notebooks);
    this.archiveSection = new ArchiveSection();
    this.zenodoSection = new ZenodoSection(this.app, this.notebooks);
    this.experimentSection = new ExperimentSection(this.app, this.notebooks);
    this.environmentSection = new EnvironmentSection(this.app, this.notebooks);
  }

  private async loadChecklistState(): Promise<void> {
    await this.checklistSection.loadChecklistState();
    this.render();
  }

  render(): void {
    const container = this.createMainContainer();
    const modal = this.createModal();
    
    this.node.innerHTML = '';
    this.node.appendChild(container);
    document.body.appendChild(modal);

    this.setupEventListeners(modal);
  }

  private createMainContainer(): HTMLElement {
    const container = document.createElement('div');
    
    // Header section
    const header = this.createHeader();
    container.appendChild(header);

    // Sections
    const sections = [
      this.demoSection.render(),
      this.checklistSection.render(),
      this.environmentSection.render(),
      this.experimentSection.render(),
      this.archiveSection.render(),
      this.zenodoSection.render()
    ];

    sections.forEach(sectionHtml => {
      const fragment = document.createRange().createContextualFragment(sectionHtml);
      container.appendChild(fragment);
    });

    return container;
  }

  private createHeader(): HTMLElement {
    const header = document.createElement('div');
    header.className = 'reprolab-header';
    header.innerHTML = `
      <h1>ReproLab</h1>
      <h3>One step closer to accessible reproducible research</h3>
    `;
    return header;
  }

  private createModal(): HTMLElement {
    const modal = document.createElement('div');
    modal.className = 'reprolab-modal';
    
    const modalContent = document.createElement('div');
    modalContent.className = 'reprolab-modal-content';
    
    const closeButton = document.createElement('span');
    closeButton.className = 'reprolab-modal-close';
    closeButton.textContent = '×';
    
    const modalText = document.createElement('div');
    modalText.innerHTML = `
      <section style="font-size: 16px; line-height: 1.6;">
        <p>
          Clicking the <strong>Create Reproducibility Package</strong> button below will insert and execute a Python code cell that generates a complete reproducibility package—bundling both your data and code.
        </p>
        <p>
          You can share this package with colleagues or publish it on platforms like 
          <a href="https://zenodo.org/" target="_blank" rel="noopener noreferrer" style="color: #0066cc; text-decoration: underline;">Zenodo</a>, which will assign a persistent identifier (DOI) to your work.
        </p>
        <p>
          For detailed instructions on structuring and publishing reproducible research, please consult the official Zenodo guide:  
          <a href="https://doi.org/10.5281/zenodo.11146986" target="_blank" rel="noopener noreferrer" style="color: #0066cc; text-decoration: underline;">
            Make Your Research Reproducible: Practical Guide for Researchers (DOI: 10.5281/zenodo.11146986)
          </a>
        </p>
        <p>
          Additional help can be found in the Zenodo documentation under their "Guide" and "GitHub and Software" sections:  
          <a href="https://help.zenodo.org/docs/" target="_blank" rel="noopener noreferrer" style="color: #0066cc; text-decoration: underline;">Zenodo Guides & Docs</a>
        </p>
      </section>
    `;
    
    const createPackageButton = createButton(BUTTON_IDS.MODAL_TEST, 'Create Reproducibility Package');
    
    modalContent.appendChild(closeButton);
    modalContent.appendChild(modalText);
    modalContent.appendChild(createPackageButton);
    
    modal.appendChild(modalContent);
    return modal;
  }

  private setupEventListeners(modal: HTMLElement): void {
    this.setupButtonListeners();
    this.setupCheckboxListeners();
    this.setupModalListeners(modal);
  }

  private setupButtonListeners(): void {
    // Demo button
    const demoBtn = this.node.querySelector(`#${BUTTON_IDS.DEMO}`);
    if (demoBtn) {
      demoBtn.addEventListener('click', () => this.demoSection.handleDemoButton());
    }

    // Archive save button
    const saveBtn = this.node.querySelector(`#${BUTTON_IDS.ARCHIVE_SAVE}`);
    if (saveBtn) {
      saveBtn.addEventListener('click', () => this.archiveSection.handleSaveButton(this.node));
    }

    // Zenodo button
    const zenodoBtn = this.node.querySelector(`#${BUTTON_IDS.ZENODO_MORE}`);
    if (zenodoBtn) {
      zenodoBtn.addEventListener('click', () => {
        const modal = document.querySelector('.reprolab-modal') as HTMLElement;
        if (modal) {
          this.zenodoSection.handleZenodoButton(modal);
        }
      });
    }

    // Create experiment button
    const createExperimentBtn = this.node.querySelector(`#${BUTTON_IDS.CREATE_EXPERIMENT}`);
    if (createExperimentBtn) {
      createExperimentBtn.addEventListener('click', () => this.handleCreateExperiment());
    }

    // Create environment button
    const createEnvironmentBtn = this.node.querySelector(`#${BUTTON_IDS.CREATE_ENVIRONMENT}`);
    if (createEnvironmentBtn) {
      createEnvironmentBtn.addEventListener('click', () => this.handleCreateEnvironment());
    }

    // Freeze dependencies button
    const freezeDepsBtn = this.node.querySelector(`#${BUTTON_IDS.FREEZE_DEPS}`);
    if (freezeDepsBtn) {
      freezeDepsBtn.addEventListener('click', () => this.handleFreezeDependencies());
    }
  }

  private setupCheckboxListeners(): void {
    this.node.querySelectorAll(CHECKBOX_SELECTOR).forEach(cb => {
      cb.addEventListener('change', (event: Event) => 
        this.checklistSection.handleCheckboxChange(event)
      );
    });
  }

  private setupModalListeners(modal: HTMLElement): void {
    // Modal close button
    const closeBtn = modal.querySelector('.reprolab-modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
      });
    }

    // Modal test button
    const modalTestBtn = modal.querySelector(`#${BUTTON_IDS.MODAL_TEST}`);
    if (modalTestBtn) {
      modalTestBtn.addEventListener('click', () => {
        console.log('Create Reproducibility Package button clicked');
        this.zenodoSection.handleTestButton();
        modal.style.display = 'none';
      });
    }

    // Close modal when clicking outside
    modal.addEventListener('click', (event) => {
      if (event.target === modal) {
        modal.style.display = 'none';
      }
    });
  }

  private handleCreateExperiment(): void {
    console.log('[ReproLab] Creating experiment...');
    
    // Create the experiment
    this.experimentSection.createExperiment();
  }

  private handleCreateEnvironment(): void {
    console.log('[ReproLab] Creating environment...');
    
    // Create the environment
    this.environmentSection.createEnvironment();
  }

  private handleFreezeDependencies(): void {
    console.log('[ReproLab] Freezing dependencies...');
    
    // Add dependency freeze cell
    this.environmentSection.addFreezeDepsCell();
  }
}

/** Activate the extension */
function activateReprolab(
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  notebooks: INotebookTracker
): void {
  console.log('JupyterLab extension reprolab is activated!');

  // Add command to open the sidebar panel
  app.commands.addCommand(REPROLAB_CONFIG.COMMAND, {
    label: REPROLAB_CONFIG.COMMAND_LABEL,
    icon: reprolabIcon,
    execute: () => {
      app.shell.activateById(REPROLAB_CONFIG.ID);
    }
  });

  // Add the command to the command palette
  palette.addItem({ 
    command: REPROLAB_CONFIG.COMMAND, 
    category: REPROLAB_CONFIG.COMMAND_CATEGORY 
  });

  // Add the sidebar widget (only once)
  const sidebarWidget = new ReprolabSidebarWidget(app, notebooks);
  app.shell.add(sidebarWidget, 'left', { rank: 100 });
}

/**
 * Initialization data for the reprolab extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'reprolab:plugin',
  description: 'One step closer reproducible research',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker],
  activate: activateReprolab
};

export default plugin;

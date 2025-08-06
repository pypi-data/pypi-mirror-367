import { createSection, getXsrfToken } from '../utils';

const CHECKLIST_FILE = 'reprolab_data/reproducibility_checklist.json';
const DEFAULT_CHECKLIST = [
  "Notebook contains clear narrative text explaining analysis steps.",
  "All software dependencies are specified with pinned versions.",
  "Project is under version control (e.g., Git) in a public repository.",
  "Notebook can be run end-to-end without manual steps.",
  "All input data are available or easily accessible.",
  "Project includes clear usage and interpretation instructions."
];

export class ChecklistSection {
  private checklist: string[];
  private checked: Record<string, boolean>;

  constructor() {
    this.checklist = DEFAULT_CHECKLIST;
    this.checked = {};
    this.checklist.forEach(item => { this.checked[item] = false; });
  }

  render(): string {
    const checklistContent = `
      <ul style="list-style: none; padding-left: 0;">
        ${this.checklist
          .map(
            item => `
          <li>
            <label>
              <input type="checkbox" data-item="${encodeURIComponent(item)}" ${this.checked[item] ? 'checked' : ''} />
              ${item}
            </label>
          </li>
        `
          )
          .join('')}
      </ul>
    `;
    const section = createSection(
      'Reproducibility Checklist',
      checklistContent
    );
    return section.outerHTML;
  }

  handleCheckboxChange(event: Event) {
    const target = event.target as HTMLInputElement;
    const item = decodeURIComponent(target.getAttribute('data-item') || '');
    this.checked[item] = target.checked;
    this.saveChecklistState();
  }

  async loadChecklistState() {
    try {
      const response = await fetch(`/api/contents/${CHECKLIST_FILE}`);
      if (response.ok) {
        const data = await response.json();
        if (data && data.content) {
          const parsed = JSON.parse(data.content);
          if (typeof parsed === 'object' && parsed !== null) {
            // Only keep keys that are in the current checklist
            this.checked = {};
            this.checklist.forEach(item => {
              this.checked[item] = !!parsed[item];
            });
          }
        }
      } else if (response.status === 404) {
        // File does not exist, create it with all unchecked
        this.checked = {};
        this.checklist.forEach(item => { this.checked[item] = false; });
        await this.saveChecklistState();
      }
    } catch (e) {
      // Could not load or parse, fallback to all unchecked
      this.checked = {};
      this.checklist.forEach(item => { this.checked[item] = false; });
      await this.saveChecklistState();
    }
  }

  async saveChecklistState() {
    try {
      const xsrfToken = getXsrfToken();
      await fetch(`/api/contents/${CHECKLIST_FILE}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(xsrfToken ? { 'X-XSRFToken': xsrfToken } : {})
        },
        body: JSON.stringify({
          type: 'file',
          format: 'text',
          content: JSON.stringify(this.checked)
        })
      });
    } catch (e) {
      // Could not save
    }
  }

  getChecklist(): string[] {
    return this.checklist;
  }

  getChecked(): Record<string, boolean> {
    return this.checked;
  }
} 

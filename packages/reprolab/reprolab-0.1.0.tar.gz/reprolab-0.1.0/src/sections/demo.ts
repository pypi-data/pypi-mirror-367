import { createSection, createButton } from '../utils';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';

// Demo content stored as a variable instead of reading from file
const DEMO_CONTENT = `# ReproLab Demo

Welcome to ReproLab! This extension helps you make your research more reproducible.

## Features

- **Create Experiments**: Automatically save immutable snapshots of your code under \`git\` tags to preserve the **exact code and outputs**
- **Manage Dependencies**: Automatically gather and pin **exact package versions**, so that others can set up your environment with one command
- **Cache Data**: Call external API/load manually dataset only once, caching function will handle the rest
- **Archive Data**: Caching function can also preserve the compressed data in *AWS S3*, so you always know what data was used and reduce the API calls
- **Publishing guide**: The reproducibility checklist & automated generation of reproducability package make publishing to platforms such as Zenodo very easy

## Getting Started

1. Use the sidebar to view ReproLab features
2. Create virtual environment and pin your dependencies, go to reprolab section \`Create reproducible environment\` 
3. Create an experiment to save your current state, go to reprolab section \`Create experiment\`
4. Archive your data for long-term storage, go to reprolab section \`Demo\` and play around with it.
5. Publish your work when ready, remember to use reproducability checklist from the section \`Reproducibility Checklist\`

## Example Usage of persistio decorator

To cache and archive the datasets you use, both from local files and APIs we developed a simple decorator that put over your function that gets the datasets caches the file both locally and in the cloud so that the dataset you use is archived and the number of calls to external APIs is minimal and you don't need to keep the file around after you run it once.

Here is an example using one of NASA open APIs. If you want to test it out yourself, you can copy the code, but you need to provide bucket name and access and secret key in the left-hand panel using the \`AWS S3 Configuration\` section.

\`\`\`python
import requests
import pandas as pd
from io import StringIO

# The two lines below is all that you need to add
from reprolab.experiment import persistio
@persistio()
def get_exoplanets_data_from_nasa():
    url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

    query = """
    SELECT TOP 10
        pl_name AS planet_name,
        hostname AS host_star,
        pl_orbper AS orbital_period_days,
        pl_rade AS planet_radius_earth,
        disc_year AS discovery_year
    FROM
        ps
    WHERE
        default_flag = 1
    """

    params = {
        "query": query,
        "format": "csv"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text))
        
        print(df)
        
    else:
        print(f"Error: {response.status_code} - {response.text}")
    return df

exoplanets_data = get_exoplanets_data_from_nasa()
\`\`\`

If you run this cell twice you will notice from the logs that the second time file was read from the compressed file in the cache. If you were to lose access to local cache (e.g. by pulling the repository using different device) \`persistio\` would fetch the data from the cloud archive.


For more information, visit our [documentation](https://github.com/your-repo/reprolab).`;

export class DemoSection {
  private app: JupyterFrontEnd;
  private notebooks: INotebookTracker | undefined;

  constructor(app: JupyterFrontEnd, notebooks?: INotebookTracker) {
    this.app = app;
    this.notebooks = notebooks;
  }

  render(): string {
    const demoContent = document.createElement('div');
    demoContent.innerHTML =
      '<p>Press the button below to add a demo cell to the top of the active notebook. The cell will display the ReproLab documentation.</p>';
    demoContent.appendChild(createButton('reprolab-demo-btn', 'Add Demo Cell'));
    const section = createSection('Demo', demoContent.innerHTML);
    return section.outerHTML;
  }

  async handleDemoButton() {
    if (this.notebooks && this.notebooks.currentWidget) {
      const notebook = this.notebooks.currentWidget.content;
      if (notebook.model && notebook.model.cells.length > 0) {
        notebook.activeCellIndex = 0;
      } else {
        this.app.commands.execute('notebook:insert-cell-below');
        notebook.activeCellIndex = 0;
      }
      this.app.commands.execute('notebook:insert-cell-above');
      if (notebook.model && notebook.model.cells.length > 0) {
        const cell = notebook.model.cells.get(0);
        if (cell) {
          try {
            // Use the hardcoded demo content instead of reading from file
            cell.sharedModel.setSource(DEMO_CONTENT);
            // Change cell type to markdown
            this.app.commands.execute('notebook:change-cell-to-markdown');
            // Render all markdown cells to ensure proper display
            this.app.commands.execute('notebook:render-all-markdown');
          } catch (error) {
            console.error('Error setting demo content:', error);
          }
        }
      }
    }
  }
}

/**
 * Utility functions for the ReproLab extension
 */

/**
 * Creates a section element with a title and content
 */
export function createSection(title: string, content: string): HTMLElement {
  const section = document.createElement('div');
  section.className = 'reprolab-section';
  section.innerHTML = `
    <h3>${title}</h3>
    ${content}
  `;
  return section;
}

/**
 * Creates a button element with the specified ID and text
 */
export function createButton(id: string, text: string): HTMLButtonElement {
  const button = document.createElement('button');
  button.id = id;
  button.className = 'reprolab-button';
  button.textContent = text;
  return button;
}

/**
 * Creates an input element with the specified ID, type, placeholder, default value, and placeholder text
 */
export function createInput(
  id: string,
  type: string,
  placeholder: string,
  defaultValue: string = '',
  placeholderText: string = ''
): HTMLInputElement {
  const input = document.createElement('input');
  input.id = id;
  input.type = type;
  input.className = 'reprolab-input';
  input.placeholder = placeholderText || placeholder;
  input.value = defaultValue;
  return input;
}

/**
 * Gets the XSRF token from cookies
 */
export function getXsrfToken(): string | null {
  const match = document.cookie.match('\\b_xsrf=([^;]*)\\b');
  return match ? decodeURIComponent(match[1]) : null;
} 
